#! /usr/bin/env python
#coding=utf-8

## Function List:
## 1. currentPath() return the path of your script
## 2. mkdir(dir) Make directory if not exists.
## 3. rmmkdir(dir) If dir is not exists, then make it, else remove and remake it.
## 4. ReadRaster(file) Read raster formatted file using GDAL, return the Raster object.
## 5. WriteGTiffFile() Write GTIFF formatted raster file.
## 6. WriteAscFile() Write ArcInfo ASCII file.
## 7. Raster2GeoTIFF() Convert all GDAL supportted raster file to GTIFF format.
## 8. Feet2Meter() Convert feet unit to meter, both for XYZ coordinate.
## 9. RasterStatistics() Return max,min,mean,std
## 10. slopeTrans() Transfer radian to degree.
## 11. WriteLog(logfile, contentlist) Write log file.
## 12. WriteLineShp(lineList,outShp) Export ESRI Shapefile -- Line feature

import os,sys,platform
from osgeo import gdal
from osgeo import osr
from osgeo import ogr
from osgeo import gdalconst
from gdalconst import *
import numpy
import math
from shutil import rmtree
import subprocess

sysstr = platform.system()
if sysstr == "Windows":
    LF = '\r'
elif sysstr == "Linux":
    LF = '\n'
def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
def mkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
def rmmkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    else:
        rmtree(dir,True)
        os.mkdir(dir)

ZERO = 1e-6
DELTA = 0.000001
def FloatEqual(a, b):
    return abs(a - b) < DELTA

class Raster:
    def __init__(self, nRows, nCols, data, noDataValue=None, geotransform=None, srs=None):
        self.nRows = nRows
        self.nCols = nCols
        self.data = data
        self.noDataValue = noDataValue
        self.geotrans = geotransform
        self.srs = srs
        self.dx = geotransform[1]
        self.xMin = geotransform[0]
        self.xMax = geotransform[0] + nCols*geotransform[1]
        self.yMax = geotransform[3]
        self.yMin = geotransform[3] + nRows*geotransform[5]

def ReadRaster(rasterFile):
    ds = gdal.Open(rasterFile)
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    xsize = band.XSize
    ysize = band.YSize

    noDataValue = band.GetNoDataValue()
    geotrans = ds.GetGeoTransform()

    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    #print srs.ExportToProj4()
    if noDataValue is None:
        noDataValue = -9999
    band = None
    ds = None
    return Raster(ysize, xsize, data, noDataValue, geotrans, srs)

def WriteGTiffFile(filename, nRows, nCols, data, geotransform, srs, noDataValue, gdalType):
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    ds = driver.Create(filename, nCols, nRows, 1, gdalType)
    ds.SetGeoTransform(geotransform)
    ds.SetProjection(srs.ExportToWkt())
    ds.GetRasterBand(1).SetNoDataValue(noDataValue)
    ds.GetRasterBand(1).WriteArray(data)
    ds = None
def WriteAscFile(filename, data, xsize, ysize, geotransform, noDataValue):
    header = """NCOLS %d
NROWS %d
XLLCENTER %f
YLLCENTER %f
CELLSIZE %f
NODATA_VALUE %f
""" % (xsize, ysize, geotransform[0] + 0.5*geotransform[1], geotransform[3]-(ysize-0.5)*geotransform[1], geotransform[1], noDataValue)

    f = open(filename, 'w')
    f.write(header)
    for i in range(0, ysize):
        for j in range(0, xsize):
            f.write(str(data[i][j]) + "\t")
        f.write("\n")
    f.close()
def Raster2GeoTIFF(tif, geotif, gdalType=gdal.GDT_Float32):
    #print "Convering Raster format to GeoTIFF..."
    rstFile = ReadRaster(tif)
    WriteGTiffFile(geotif, rstFile.nRows, rstFile.nCols, rstFile.data, rstFile.geotrans, rstFile.srs, rstFile.noDataValue, gdalType)
def Raster2Asc(rasterF, ascF):
    rasterR = ReadRaster(rasterF)
    WriteAscFile(ascF, rasterR.data, rasterR.nCols, rasterR.nRows, rasterR.geotrans, rasterR.noDataValue)
def Feet2Meter(feetF, meterF, ZFlag = True, gdalType=gdal.GDT_Float32):
    feetR = ReadRaster(feetF)
    if ZFlag:
        ## first, convert elevation
        feetR.data *= 0.3048
    ## second, convert geotransform information
    ## but, current version did not consider the transformation of Coordinate System
    ## therefore, this function is only suited for raster with unknown Coordinate System!
    geoInfo = feetR.geotrans
    #print geoInfo
    ## xMin, dx, 0, yMax, 0, negative dx
    newgeotrans = (feetR.geotrans[0] * 0.3048, feetR.geotrans[1] * 0.3048, 0, feetR.geotrans[3] * 0.3048, 0, feetR.geotrans[5] * 0.3048)
    #print newgeotrans
    WriteGTiffFile(meterF, feetR.nRows, feetR.nCols, feetR.data, newgeotrans, feetR.srs, feetR.noDataValue, gdalType)
def slopeTrans(tanslp,slp):
    origin = ReadRaster(tanslp)
    temp = origin.data == origin.noDataValue
    slpdata = numpy.where(temp,origin.noDataValue,numpy.arctan(origin.data) * 180. / numpy.pi)
    WriteGTiffFile(slp, origin.nRows, origin.nCols, slpdata, origin.geotrans, origin.srs, origin.noDataValue, gdal.GDT_Float32)
def Binarization(orgF, destF, threshold):
    orgR = ReadRaster(orgF)
    orgD = orgR.data
    temp = orgD > threshold
    destD = numpy.where(temp,1,orgR.noDataValue)
    WriteGTiffFile(destF, orgR.nRows, orgR.nCols, destD, orgR.geotrans, orgR.srs, orgR.noDataValue, gdal.GDT_Float32)
def Counting(orgF):
    orgR = ReadRaster(orgF)
    temp = orgR.data != orgR.noDataValue
    return numpy.sum(temp)
def RasterStatistics(rasterFile):
    ds = gdal.Open(rasterFile)
    band = ds.GetRasterBand(1)
    min,max,mean,std = band.ComputeStatistics(False)
    return (min,max,mean,std)

def WriteLog(logfile, contentlist):
    if os.path.exists(logfile):
        logStatus = open(logfile, 'a')
    else:
        logStatus = open(logfile, 'w')
    for content in contentlist:
        logStatus.write("%s\n" % content)
    logStatus.flush()
    logStatus.close()

## D8 flow directions in TauDEM, value(DELTA_row, DELTA_col)
DIR_ITEMS = {1:(0,1),
             2:(-1,1),
             3:(-1,0),
             4:(-1,-1),
             5:(0,-1),
             6:(1,-1),
             7:(1,0),
             8:(1,1)}
DIR_VALUES = [1,2,3,4,5,6,7,8]
## corresponding to ArcGIS
## DIR_VALUES = [1,128,64,32,16,8,4,2]
drow = [0,-1,-1,-1, 0, 1,1,1] ## row, not include itself
dcol = [1, 1, 0,-1,-1,-1,0,1] ## col


## find downslope coordinate for D8 and D-inf flow models
def downstream_index(DIR_VALUE, i, j):
    drow, dcol = DIR_ITEMS[DIR_VALUE]
    return i+drow, j+dcol
# D-inf flow model
e = 0
ne = math.pi * 0.25
n  = math.pi * 0.5
nw = math.pi * 0.75
w  = math.pi
sw = math.pi * 1.25
s  = math.pi * 1.5
se = math.pi * 1.75
angleList = [e, ne, n, nw, w, sw, s, se]

def CheckOrtho(a):
    if FloatEqual(a, e):
        return 1
    elif FloatEqual(a, ne):
        return 2
    elif FloatEqual(a, n):
        return 3
    elif FloatEqual(a, nw):
        return 4
    elif FloatEqual(a, w):
        return 5
    elif FloatEqual(a, sw):
        return 6
    elif FloatEqual(a, s):
        return 7
    elif FloatEqual(a, se):
        return 8
    else:
        return 0

def AssignDirCode(a):
    d = CheckOrtho(a)
    if d != 0:
        down = [d]
        return down
    else:
        if a < ne: ## 129 = 1+128
            down = [1,2]
        elif a < n: ## 192 = 128+64
            down = [2,3]
        elif a < nw: ## 96 = 64+32
            down = [3,4]
        elif a < w: ## 48 = 32+16
            down = [4,5]
        elif a < sw: ## 24 = 16+8
            down = [5,6]
        elif a < s: ## 12 = 8+4
            down = [6,7]
        elif a < se: ## 6 = 4+2
            down = [7,8]
        else: ## 3 = 2+1
            down = [8,1]
        return down

def downstream_index_dinf(dinfDir, i, j):
    downDirs = AssignDirCode(dinfDir)
    #print dinfDir,i,j,downDirs
    downCoors = []
    for dir in downDirs:
        row, col = downstream_index(dir, i, j)
        downCoors.append([row, col])
    return downCoors

## Export ESRI Shapefile -- Line feature
def WriteLineShp(lineList,outShp):
    print "Write line shapefile: %s" % outShp
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if driver is None:
        print "ESRI Shapefile driver not available."
        sys.exit(1)
    if os.path.exists(outShp):
        driver.DeleteDataSource(outShp)
    ds = driver.CreateDataSource(outShp.rpartition(os.sep)[0])
    if ds is None:
        print "ERROR Output: Creation of output file failed."
        sys.exit(1)
    lyr = ds.CreateLayer(outShp.rpartition(os.sep)[2].split('.')[0],None,ogr.wkbLineString)
#    for field in fields:
#        fieldDefn = ogr.FieldDefn(field,ogr.OFTString)
#        fieldDefn.SetWidth(255)
#        lyr.CreateField(fieldDefn)
    for l in lineList:
#        defn = lyr.GetLayerDefn()
#        featureFields = ogr.Feature(defn)
#        for field in fields:
#            featureFields.SetField(field,"test")
        line = ogr.Geometry(ogr.wkbLineString)
        for i in l:
            line.AddPoint(i[0],i[1])
        templine = ogr.CreateGeometryFromJson(line.ExportToJson())
        feature = ogr.Feature(lyr.GetLayerDefn())
        feature.SetGeometry(templine)
        lyr.CreateFeature(feature)
        feature.Destroy()
    ds.Destroy()
def SplitRasters(rs, splitShp, fieldName, tempDir):
    rmmkdir(tempDir)
    ds = ogr.Open(splitShp)
    lyr = ds.GetLayer(0)
    lyr.ResetReading()
    ft = lyr.GetNextFeature()
    while ft:
        cur_field_name = ft.GetFieldAsString(fieldName)
        for r in rs:
            curFileName = r.split(os.sep)[-1]
            outraster = tempDir + os.sep + curFileName.replace('.tif','_%s.tif' % cur_field_name.replace(' ', '_'))
            subprocess.call(['gdalwarp', r, outraster, '-cutline', splitShp,
                             '-crop_to_cutline', '-cwhere', "'%s'='%s'" % (fieldName, cur_field_name), '-dstnodata', '-9999'])
        ft = lyr.GetNextFeature()
    ds = None
    #rmtree(tempDir,True)

## test code ##
if __name__ == '__main__':
    # tanslp = r'C:\Users\ZhuLJ\Desktop\test\DinfSlp.tif'
    # slp = r'C:\Users\ZhuLJ\Desktop\test\Slp.tif'
    # slopeTrans(tanslp,slp)
    #feetF = r'E:\data\PleasantValley\Fuzzy_slope_position_qin2009\feet_asc\vly1_ed_1.asc'
    #meterF = r'E:\data\PleasantValley\Fuzzy_slope_position_qin2009\meter_tif\vlyInf_meter_qin.tif'
    #Raster2GeoTIFF(, )
    #Raster2Asc(meterF, r'E:\data\PleasantValley\PleasantVly-DEM-version\pvDEM_meter_from_3dr.asc')
    #Feet2Meter(feetF, meterF, False)
    #file = r'E:\data_m\QSWAT_projects\Done\baseSim_unCali\baseSim_unCali\pond_preprocess\temp\pond_no_stream_1.tif'
    #print Counting(file)
    dem = r'E:\data_m\FieldPartition\dianbu\Source\dem_3wtsdfel.tif'
    stream = r'E:\data_m\FieldPartition\dianbu\Source\dem_3wtsdsrc.tif'
    flowdir = r'E:\data_m\FieldPartition\dianbu\Source\dem_3wtsdp.tif'
    landuse = r'E:\data\Dianbu\temp\landuse_3wtsd.tif'
    subbsn_shp = r'E:\data\Dianbu\subbasin\3wtsds_merge.shp'
    field = 'wtsd'
    outdir = r'E:\data\Dianbu\patch_partition'
    SplitRasters([dem,stream,flowdir,landuse],subbsn_shp,field,outdir)
