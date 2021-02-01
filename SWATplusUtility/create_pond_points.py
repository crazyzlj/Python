# -*- coding: utf-8 -*-
"""This program helps you to create pond points for SWAT+ modeling.

    @author   : Liangjun Zhu
    @Email    : zlj@lreis.ac.cn
"""
from __future__ import absolute_import, unicode_literals

import os
import json
from io import open
from collections import OrderedDict

from osgeo import ogr
from pygeoc.utils import FileClass
from pygeoc.raster import RasterUtilClass
from pygeoc.hydro import D8Util, FlowModelConst


def main(prjpath, pondfile, floodfile, demname, minpondcount, maxaccpercent):
    wtsd_dir = prjpath + os.sep + 'Watershed'
    rasters_dir = wtsd_dir + os.sep + 'Rasters'
    demderiv_dir = rasters_dir + os.sep + 'DEM'
    vectors_dir = wtsd_dir + os.sep + 'Shapes'

    # inputs
    fd8_file = demderiv_dir + os.sep + '%spclip.tif' % demname
    chanw_file = demderiv_dir + os.sep + '%swChannel.tif' % demname  # with ID, but not masked
    chan_file = demderiv_dir + os.sep + '%ssrcChannelclip.tif' % demname  # without ID
    outlet_file = vectors_dir + os.sep + 'outlet_single.shp'

    # temporary outputs
    wtsdclip_file = rasters_dir + os.sep + 'channel_wtsd.tif'
    chanclip_file = rasters_dir + os.sep + 'channel.tif'
    pondclip_file = rasters_dir + os.sep + 'pond.tif'

    # outputs
    out_all_channel_data = wtsd_dir + os.sep + 'all_channel_data.json'
    out_sel_channel_data = wtsd_dir + os.sep + 'selected_channel_data.json'
    out_file = vectors_dir + os.sep + 'outlets_with_pond.shp'

    # Check the existence of input files
    input_files = [fd8_file, chanw_file, chan_file]
    for infile in input_files:
        if not os.path.exists(infile):
            print('%s not existed!' % os.path.basename(infile))
            return

    # Read flow direction D8, and perform as mask
    d8_rs = RasterUtilClass.read_raster(fd8_file)

    # Clip and read pond raster file
    #  Cells with values (i.e., not nodata) are ponds
    RasterUtilClass.mask_raster(pondfile, fd8_file, pondclip_file)
    pond_rs = RasterUtilClass.read_raster(pondclip_file)

    # Clip and read channel (without ID) and channel-induced subbasins (with ID)
    RasterUtilClass.mask_raster(chanw_file, fd8_file, wtsdclip_file)
    RasterUtilClass.mask_raster(chan_file, fd8_file, chanclip_file)
    wtsd_rs = RasterUtilClass.read_raster(wtsdclip_file)
    chan_rs = RasterUtilClass.read_raster(chanclip_file)

    # Read floodplain
    flood_rs = RasterUtilClass.read_raster(floodfile)

    # Check rows and cols
    rsdata_filename = [(pond_rs, pondclip_file), (wtsd_rs, wtsdclip_file),
                       (chan_rs, chanclip_file), (flood_rs, floodfile)]
    for (rsdata, rsfile) in rsdata_filename:
        if d8_rs.nRows != rsdata.nRows or d8_rs.nCols != rsdata.nCols:
            print('Raster size unmatched! Please check %s and %s' % (os.path.basename(fd8_file),
                                                                     os.path.basename(rsfile)))
            return

    # Read channel row-col data
    #  'id': int,
    #  'length': float,
    #  'rowcol': list[[int, int]],
    #  'pond_in_count': list[int],
    #  'pond_in_count_acc': list[int],
    #  'pond_in_count_acc_percent': list[float]
    channel_data = dict()

    nrows = d8_rs.nRows
    ncols = d8_rs.nCols
    cellsize = d8_rs.dx

    # Initialize channel coordinates
    for row in range(nrows):
        for col in range(ncols):
            chan_value = chan_rs.get_value_by_row_col(row, col)
            if chan_value is None or chan_value - chan_rs.noDataValue < 1.e-6 or chan_value <= 0:
                continue
            wtsd_id = int(wtsd_rs.get_value_by_row_col(row, col))
            if wtsd_id in channel_data:
                continue
            # Check if current cell is the headwater of current channel
            headwater = True
            for dr, dc in zip(FlowModelConst.ccw_drow, FlowModelConst.ccw_dcol):
                newr = dr + row
                newc = dc + col
                newfd8 = d8_rs.get_value_by_row_col(newr, newc)
                if newfd8 is None or int(newfd8) not in list(range(1, 9)):
                    continue
                newfd8 = int(newfd8)
                newr2, newc2 = D8Util.downstream_index(newfd8, newr, newc)
                if newr2 == row and newc2 == col:
                    newchan = chan_rs.get_value_by_row_col(newr, newc)
                    newwtsd = int(wtsd_rs.get_value_by_row_col(newr, newc))
                    if newchan is not None and newwtsd is not None and newchan == chan_value and \
                            newwtsd == wtsd_id:
                        headwater = False
                        break
            if not headwater:
                continue
            # print(wtsd_id, row, col)
            channel_data.setdefault(wtsd_id, {'length': 0.,
                                              'rowcol': [[row, col]],
                                              'pond_in_count': list(),
                                              'pond_in_count_acc': list(),
                                              'pond_in_count_acc_percent': list()})
            terminated = False
            currow = row
            curcol = col
            while not terminated:
                fd8 = d8_rs.get_value_by_row_col(currow, curcol)
                if fd8 is None or int(fd8) not in list(range(1, 9)):
                    terminated = True
                    continue
                fd8 = int(fd8)
                currow, curcol = D8Util.downstream_index(fd8, currow, curcol)
                if currow >= nrows or curcol >= ncols:
                    terminated = True
                    continue
                next_wtsd_id = wtsd_rs.get_value_by_row_col(currow, curcol)
                if next_wtsd_id is None:
                    terminated = True
                    continue
                channel_data[wtsd_id]['length'] += FlowModelConst.d8len_td[fd8] * cellsize
                channel_data[wtsd_id]['rowcol'].append([currow, curcol])
                if next_wtsd_id != wtsd_id:
                    terminated = True
                    continue

    # Initialize pond related statistics lists
    for cid in channel_data:
        channel_data[cid]['pond_in_count'] = [0] * len(channel_data[cid]['rowcol'])
        channel_data[cid]['pond_in_count_acc'] = [0] * len(channel_data[cid]['rowcol'])
        channel_data[cid]['pond_in_count_acc_percent'] = [0.] * len(channel_data[cid]['rowcol'])

    # Loop for pond cells and track down to the channel
    for row in range(nrows):
        for col in range(ncols):
            pond_value = pond_rs.get_value_by_row_col(row, col)
            if pond_value is None or pond_value <= 0:
                continue
            flood_value = flood_rs.get_value_by_row_col(row, col)
            if flood_value is None or flood_value <= 0:
                continue
            wtsd_id = wtsd_rs.get_value_by_row_col(row, col)
            terminated = False
            currow = row
            curcol = col
            while not terminated:
                fd8 = d8_rs.get_value_by_row_col(currow, curcol)
                if fd8 is None or int(fd8) not in list(range(1, 9)):
                    terminated = True
                    continue
                fd8 = int(fd8)
                currow, curcol = D8Util.downstream_index(fd8, currow, curcol)
                if currow >= nrows or curcol >= ncols:
                    terminated = True
                    continue
                chan_value = chan_rs.get_value_by_row_col(currow, curcol)
                if chan_value is not None and chan_value > 0:
                    terminated = True
                    if [currow, curcol] not in channel_data[wtsd_id]['rowcol']:
                        print('Pond(%d, %d) terminates in channel %d '
                              'at (%d, %d), but the point is not in channel data!'
                              % (row, col, wtsd_id, currow, curcol))
                        continue
                    idx = channel_data[wtsd_id]['rowcol'].index([currow, curcol])
                    channel_data[wtsd_id]['pond_in_count'][idx] += 1

    for cid in channel_data:
        clen = len(channel_data[cid]['rowcol'])
        for i in range(clen):
            channel_data[cid]['pond_in_count_acc'][i] = channel_data[cid]['pond_in_count'][i]
            if i == 0:
                continue
            channel_data[cid]['pond_in_count_acc'][i] += channel_data[cid]['pond_in_count_acc'][
                i - 1]
        ctot = channel_data[cid]['pond_in_count_acc'][-1]
        if ctot == 0:
            continue
        for i in range(clen):
            channel_data[cid]['pond_in_count_acc_percent'][i] = \
                channel_data[cid]['pond_in_count_acc'][i] / ctot
        # print('Channel ID: %d, total upstream pond cells: %d' % (cid, ctot))
    # print(channel_data)

    # Output selected channel data
    ordered_channel_data = {k: v for k, v in sorted(channel_data.items())}
    json_data = json.dumps(ordered_channel_data, indent=4)
    with open(out_all_channel_data, 'w', encoding='utf-8') as f:
        f.write('%s' % json_data)
    selected_channel_data = OrderedDict()
    for k, v in ordered_channel_data.items():
        if v['pond_in_count_acc'][-1] > minpondcount:
            selected_channel_data[k] = v

    json_data = json.dumps(selected_channel_data, indent=4)
    with open(out_sel_channel_data, 'w', encoding='utf-8') as f:
        f.write('%s' % json_data)

    # Determine the coordinates of ponds
    pond_coors = list()
    for k, v in selected_channel_data.items():
        sel_idx = -1
        for idx, perc in enumerate(v['pond_in_count_acc_percent']):
            if perc >= maxaccpercent:
                sel_idx = idx
                break
        if sel_idx < 0:
            continue
        selrow, selcol = v['rowcol'][sel_idx]
        selx, sely = d8_rs.get_central_coors(selrow, selcol)
        pond_coors.append([selx, sely])
        print('Pond on Channel %d, row: %d, col: %d.' % (k, selrow, selcol))

    # Write output shapefile
    # 1. read outlet shapefile and get existing points
    driver = ogr.GetDriverByName('ESRI Shapefile')
    outlet_src = driver.Open(outlet_file, 0)  # 0 means read-only, 1 means writable
    # check to see if shapefile is found
    if outlet_src is None:
        return
    outlet_lyr = outlet_src.GetLayer(0)
    ptcounts = outlet_lyr.GetFeatureCount()
    layer_defs = outlet_lyr.GetLayerDefn()
    fld_count = layer_defs.GetFieldCount()
    id_idx = -1
    res_idx = -1
    for i in range(fld_count):
        if layer_defs.GetFieldDefn(i).GetName().upper() == 'ID':
            id_idx = i
        elif layer_defs.GetFieldDefn(i).GetName().upper() == 'RES':
            res_idx = i
    if id_idx < 0 or res_idx < 0:
        print('Please check the input outlet shapefile: %s, '
              'missing ID or RES field!' % os.path.basename(outlet_file))

    print('Original outlet shapefile has %d point(s).' % ptcounts)

    # create the data source, remove output shapefile first if it already exists
    if os.path.exists(out_file):
        driver.DeleteDataSource(out_file)
    out_driver = ogr.GetDriverByName('ESRI Shapefile')
    newout_src = out_driver.CreateDataSource(out_file)  # create data source/shapefile
    newout_lyr = newout_src.CreateLayer(FileClass.get_core_name_without_suffix(out_file),
                                        d8_rs.srs, ogr.wkbPoint)  # create the layer
    for i in range(fld_count):
        newout_lyr.CreateField(layer_defs.GetFieldDefn(i))
    newout_defn = newout_lyr.GetLayerDefn()

    # Add outlet points to the new output Layer
    pt_count = 0
    for outlet_pt in outlet_lyr:
        # Create output Feature
        newout_pt = ogr.Feature(newout_defn)
        # Add field values from input Layer
        for i in range(newout_defn.GetFieldCount()):
            newout_pt.SetField(newout_defn.GetFieldDefn(i).GetNameRef(),
                               outlet_pt.GetField(i))
        # reset ID
        newout_pt.SetField(newout_defn.GetFieldDefn(id_idx).GetNameRef(), pt_count)
        pt_count += 1
        # Set geometry as centroid
        geom = outlet_pt.GetGeometryRef()
        newout_pt.SetGeometry(geom.Clone())
        # Add new feature to output Layer
        newout_lyr.CreateFeature(newout_pt)
        newout_pt = None

    # Add pond points to the new output Layer
    for pondpt in pond_coors:
        curpt = ogr.Feature(newout_defn)
        for i in range(newout_defn.GetFieldCount()):
            if i == id_idx:
                curpt.SetField(newout_defn.GetFieldDefn(i).GetNameRef(), pt_count)
                pt_count += 1
            elif i == res_idx:
                curpt.SetField(newout_defn.GetFieldDefn(i).GetNameRef(), 2)
            else:
                curpt.SetField(newout_defn.GetFieldDefn(i).GetNameRef(), 0)

        # create the WKT for the feature using Python string formatting
        wkt = "POINT(%f %f)" % (pondpt[0], pondpt[1])
        # Create the point from the Well Known Txt
        point = ogr.CreateGeometryFromWkt(wkt)
        # Set the feature geometry using the point
        curpt.SetGeometry(point)
        # Create the feature in the layer (shapefile)
        newout_lyr.CreateFeature(curpt)
        # Dereference the feature
        curpt = None

    # Save and close DataSources
    outlet_src = None
    newout_src = None


if __name__ == '__main__':
    swatplus_prj_path = r'D:\data_m\SWATplus\zts20200612'
    pond_file = r'D:\data\zhongTianShe\landuse\pond_originid_25m_utm.tif'
    flood_file = swatplus_prj_path + os.sep + r'Watershed\Rasters\Landscape\Flood\invflood0_10.tif'
    dem_name = 'dem_zts_utm_25mclip'

    min_pond_cells = 20
    max_acc_percent = 0.8

    main(swatplus_prj_path, pond_file, flood_file, dem_name, min_pond_cells, max_acc_percent)
