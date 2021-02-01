# coding=utf-8
"""
Created on 2015-1-6

@author: Liangjun Zhu
@summary: Delineating and Extracting hillslopes and rill channel from DEM.
@param: 1.DEM          -- Original DEM in ARC/GRID filetype
        2.threshold    -- User defined accumulation threshold for stream extraction,
                          By default, threshold is 2% of the max accumulation.
        3.DepthofRill  -- Determine the min depth of stream to be an rill.
@requires  : ArcGIS 10.x, gdal
@references: 
@contract  : zlj@lreis.ac.cn
"""
from osgeo import gdal
from osgeo import osr
import numpy
import os
import arcpy
from arcpy import env

##  Const Variables Definition  ##
DIR_ITEMS = {1:(0,1),
             2:(1,1),
             4:(1,0),
             8:(1,-1),
             16:(0,-1),
             32:(-1,-1),
             64:(-1,0),
             128:(-1,1)}
DIR_VALUES = [1,2,4,8,16,32,64,128]
MINI_VALUE = 0.000001
##  End Const Variables Definition  ##

##  Define Utility Functions  ##
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
    return Raster(ysize, xsize, data, noDataValue, geotrans, srs) 

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
    
def WriteGTiffFile(filename, nRows, nCols, data, geotransform, srs, noDataValue, gdalType):
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    ds = driver.Create(filename, nCols, nRows, 1, gdalType)
    ds.SetGeoTransform(geotransform)
    ds.SetProjection(srs.ExportToWkt())
    ds.GetRasterBand(1).SetNoDataValue(noDataValue)
    ds.GetRasterBand(1).WriteArray(data)
    
    ds = None

def WriteGTiffFileByMask(filename, data, mask, gdalType):
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    ds = driver.Create(filename, mask.nCols, mask.nRows, 1, gdalType)
    ds.SetGeoTransform(mask.geotrans)
    ds.SetProjection(mask.srs.ExportToWkt())
    ds.GetRasterBand(1).SetNoDataValue(mask.noDataValue)
    ds.GetRasterBand(1).WriteArray(data)
    ds = None
def NashCoef(qObs, qSimu):
    n = len(qObs)
    ave = sum(qObs)/n
    a1 = 0
    a2 = 0
    for i in range(n):
        a1 = a1 + pow(qObs[i]-qSimu[i], 2)
        a2 = a2 + pow(qObs[i] - ave, 2)
    return 1 - a1/a2

def RMSE(list1, list2):
    n = len(list1)
    s = 0
    for i in range(n):
        s = s + pow(list1[i] - list2[i], 2)
    return math.sqrt(s/n)

def StdEv(list1):
    n = len(list1)
    av = sum(list1)/n
    s = 0
    for i in range(n):
        s = s + pow(list1[i] - av, 2)
    return math.sqrt(s/n)
##  End Utility Functions ##

##  Functions for Hillslope Delineating  ##
def downstream_index(DIR_VALUE, i, j):
    drow, dcol = DIR_ITEMS[DIR_VALUE]
    return i+drow, j+dcol

def isFirstStreamCell(StreamRaster, nodata, row, col, flow_dir):
    nrows,ncols = StreamRaster.shape
    if(StreamRaster[row][col] == nodata):
        return False
    else:
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ni = row + di
                nj = col + dj
                if ni < 0 or nj < 0 or ni >= nrows or nj >= ncols or flow_dir[ni][nj] <=0:
                    continue
                if downstream_index(flow_dir[ni][nj], ni, nj) == (row,col) and (StreamRaster[ni][nj] != nodata):
                    return False
        return True
def isStreamSegmentCell(StreamRaster, nodata, row, col, flow_dir):
    ## 1 means First cell, 2 means Finally cell, 3 means middle cells.
    nrows,ncols = StreamRaster.shape
    count = 0
    if StreamRaster[row][col] == nodata:
        return 0
    else:
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ni = row + di
                nj = col + dj
                if ni < 0 or nj < 0 or ni >= nrows or nj >= ncols or flow_dir[ni][nj] <=0:
                    continue
                if downstream_index(flow_dir[ni][nj], ni, nj) == (row,col) and (StreamRaster[ni][nj] == StreamRaster[row][col]):
                    count = count + 1
        if count >= 1:
            idx = downstream_index(flow_dir[row][col], row, col)
            if idx[0] >= nrows or idx[1] >= ncols or idx[0] <0 or idx[1] < 0 or StreamRaster[idx[0]][idx[1]] == nodata:
                return 2
            else:
                return 3
        else:
            return 1
    
def fillUpstreamCells(flow_dir,stream,nodata,hillslp,value,row,col):
    nrows,ncols = flow_dir.shape
    for di in [-1,0,1]:
        for dj in [-1,0,1]:
            tempRow = di + row
            tempCol = dj + col
            if tempRow < 0 or tempCol < 0 or tempRow >= nrows or tempCol >= ncols:
                continue
            if downstream_index(flow_dir[tempRow][tempCol],tempRow,tempCol)==(row,col) and stream[tempRow][tempCol] == nodata:
                if hillslp[tempRow][tempCol] != 1:
                    hillslp[tempRow][tempCol] = value
                #print tempRow,tempCol
                fillUpstreamCells(flow_dir,stream,nodata,hillslp,value,tempRow,tempCol)  

def UtilHydroFiles(DEMsrc, folder):
    env.workspace = folder
    arcpy.gp.overwriteOutput = 1
    arcpy.CheckOutExtension("Spatial")
    ## Set the source dem with one cell buffer to 
    ## avoid NODATA around the edges
    dem_des = arcpy.gp.describe(DEMsrc)
    cellsize = max(dem_des.MeanCellWidth,dem_des.MeanCellHeight)
    extent_src = dem_des.Extent
    extent_buf = arcpy.Extent(dem_des.Extent.XMin - cellsize,dem_des.Extent.YMin - cellsize,dem_des.Extent.XMax + cellsize,dem_des.Extent.YMax + cellsize)
    env.extent = extent_buf
    env.cellSize = cellsize
    Exec = "Con(IsNull(\"%s\"),FocalStatistics(\"%s\", NbrRectangle(3, 3, \"CELL\"), \"MEAN\", \"DATA\"),\"%s\")" % (DEMsrc, DEMsrc, DEMsrc)
    arcpy.gp.RasterCalculator_sa(Exec, "DEMbuf")
    env.extent = dem_des.Extent
    DEMfil = arcpy.sa.Fill(DEMsrc)
    DEMfil.save("DEMfil")
    Flowdir = arcpy.sa.FlowDirection("DEMfil","NORMAL")
    Curvature = arcpy.sa.Curvature("DEMfil","","curvprof","curvplan")
    Curvature.save("curv")
    Flowdir.save("flowdir")
    FlowLen = arcpy.sa.FlowLength("flowdir","DOWNSTREAM")
    FlowLen.save("flowlen")
    FlowAcc = arcpy.sa.FlowAccumulation("flowdir","","FLOAT")
    FlowAcc.save("flowacc")
    Basin = arcpy.sa.Basin("flowdir")
    Basin.save("basin")
    arcpy.RasterToPolygon_conversion("basin","basin.shp","NO_SIMPLIFY","VALUE")
    
    DEMbuf = folder + os.sep + "DEMbuf"
    DEMfil = folder + os.sep + "DEMfil"
    FlowDirFile = folder + os.sep + "flowdir"
    FlowAccFile = folder + os.sep + "flowacc"
    CurvProfFile = folder + os.sep + "curvprof"
    CurvPlanFile = folder + os.sep + "curvplan"
    
    return (DEMbuf,DEMfil,FlowDirFile,FlowAccFile,CurvProfFile,CurvPlanFile)
    
##  End Define Utility Functions ##

##  Define key functions to Calculate Rill Network  ##
def GenerateNetworkFormDEM(DEMbuf,FlowDirFile,FlowAccFile,threshold,folder):
    env.workspace = folder
    arcpy.gp.overwriteOutput = 1
    arcpy.CheckOutExtension("Spatial")

    if float(threshold) < MINI_VALUE:
        threshold = float(str(arcpy.GetRasterProperties_management(FlowAccFile,"MAXIMUM"))) / 100
    Exec = "Con(\"%s\" > %s,1)" % (FlowAccFile, threshold)
    arcpy.gp.RasterCalculator_sa(Exec, "streamnet")
    Stream_shp = "streamnet.shp"
    arcpy.sa.StreamToFeature("streamnet",FlowDirFile,Stream_shp,"NO_SIMPLIFY")
    StreamLinks = arcpy.sa.StreamLink("streamnet",FlowDirFile)
    StreamLinks.save("streamlinks")
    StreamLinks_shp = "streamnet.shp"
    arcpy.sa.StreamToFeature("streamlinks",FlowDirFile,StreamLinks_shp,"NO_SIMPLIFY")
    StreamOrder = arcpy.sa.StreamOrder("streamnet",FlowDirFile,"STRAHLER")
    StreamOrder.save("streamorder")
    StreamOrder_shp = "StreamOrder.shp"
    arcpy.sa.StreamToFeature("streamorder",FlowDirFile,StreamOrder_shp,"NO_SIMPLIFY")
    arcpy.FeatureVerticesToPoints_management(StreamOrder_shp,"StreamNDsStart.shp","START")
    arcpy.FeatureVerticesToPoints_management(StreamOrder_shp,"StreamNDsEnd.shp","END")
    arcpy.AddXY_management("StreamNDsStart.shp")
    arcpy.AddXY_management("StreamNDsEnd.shp")
    arcpy.sa.ExtractValuesToPoints("StreamNDsStart.shp",DEMbuf,"StreamNDsElevStart.shp","NONE", "VALUE_ONLY")
    arcpy.sa.ExtractValuesToPoints("StreamNDsEnd.shp",DEMbuf,"StreamNDsElevEnd.shp","NONE", "VALUE_ONLY")
    Watershed = arcpy.sa.Watershed(FlowDirFile,"streamlinks","VALUE")
    Watershed.save("watershed")
    arcpy.RasterToPolygon_conversion("watershed","Watershed.shp","NO_SIMPLIFY","VALUE")
    WatershedFile = folder + os.sep + "watershed"
    StreamFile = folder + os.sep + "streamlinks"
    return (StreamFile,WatershedFile)
def GetRillStartIdx(StreamLinks,nodata,FlowDir):
    nrows,ncols = StreamLinks.shape
    countRill = 0
    countmid = 0
    countend = 0
    RillStartIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if (isStreamSegmentCell(StreamLinks,nodata,i,j,FlowDir) == 1):
                countRill = countRill + 1
                RillStartIdx.append((i,j))
            elif (isStreamSegmentCell(StreamLinks,nodata,i,j,FlowDir) == 3):
                countend = countend + 1
            elif (isStreamSegmentCell(StreamLinks,nodata,i,j,FlowDir) == 2):
                countmid = countmid + 1
                
    print "Rill number is : %s,%s,%s" % (countRill,countmid,countend)
    return RillStartIdx

def DelineateHillslopes(StreamFile,FlowDirFile,HillslpFile):
    StreamLinks = ReadRaster(StreamFile).data
    nodata = ReadRaster(StreamFile).noDataValue
    geotrans = ReadRaster(StreamFile).geotrans
    FlowDir = ReadRaster(FlowDirFile).data
    nrows,ncols = StreamLinks.shape
    count = 0
    SourcePtsIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if(isFirstStreamCell(StreamLinks,nodata,i,j,FlowDir)):
                count = count +1
                SourcePtsIdx.append((i,j))
                
    print "Headwater point:%s" % count
    test = GetRillStartIdx(StreamLinks,nodata,FlowDir)
    HillslopeMtx = numpy.ones((nrows,ncols))
    HillslopeMtx = HillslopeMtx * nodata
    
    for SourcePt in SourcePtsIdx:
        #print SourcePt
        cRow,cCol = SourcePt
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ci = cRow + di
                cj = cCol + dj
                if ci < 0 or cj < 0 or ci >= nrows or cj >= ncols:
                    continue
                if downstream_index(FlowDir[ci][cj],ci,cj)==(cRow,cCol):
                    HillslopeMtx[ci][cj] = 0
                    fillUpstreamCells(FlowDir,StreamLinks,nodata,HillslopeMtx,0,ci,cj)          
        previous = SourcePt
        current = downstream_index(FlowDir[cRow][cCol],cRow,cCol)
        
        while not(current[0] < 0 or current[1] < 0 or current[0] >= nrows or current[1] >= ncols):      
            CurRow = current[0]
            CurCol = current[1]
            StreamLinkValue = StreamLinks[CurRow][CurCol]
            DirIdx = DIR_VALUES.index(FlowDir[CurRow][CurCol])
            if DirIdx <= 7:
                Clockwise = range(DirIdx + 1, 8)
            for i in range(DirIdx):
                Clockwise.append(i)
            CounterClock = list(reversed(Clockwise))
            if isStreamSegmentCell(StreamLinks,nodata,CurRow,CurCol,FlowDir) == 1:
                Clockwise = Clockwise[0:4]
                CounterClock = CounterClock[0:4]
            if isStreamSegmentCell(StreamLinks,nodata,CurRow,CurCol,FlowDir) == 2:
                DirIdx = DIR_VALUES.index(FlowDir[previous[0]][previous[1]])
                Clockwise = range(DirIdx + 1, 8)
                for i in range(DirIdx):
                    Clockwise.append(i)
                CounterClock = list(reversed(Clockwise))
                Clockwise = Clockwise[0:4]
                CounterClock = CounterClock[0:4]
            for Dir in Clockwise:
                temprow = CurRow + DIR_ITEMS[DIR_VALUES[Dir]][0]
                tempcol = CurCol + DIR_ITEMS[DIR_VALUES[Dir]][1]
                if temprow < 0 or tempcol < 0 or temprow >= nrows or tempcol >= ncols:
                    continue
                if downstream_index(FlowDir[temprow][tempcol],temprow,tempcol) == (CurRow,CurCol):
                    if StreamLinks[temprow][tempcol] == StreamLinkValue:
                        break
                    elif StreamLinks[temprow][tempcol] != nodata:
                        continue
                    else:
                        HillslopeMtx[temprow][tempcol] = 1
                        fillUpstreamCells(FlowDir,StreamLinks,nodata,HillslopeMtx,1,temprow,tempcol)
            for Dir in CounterClock:
                temprow = CurRow + DIR_ITEMS[DIR_VALUES[Dir]][0]
                tempcol = CurCol + DIR_ITEMS[DIR_VALUES[Dir]][1]
                if temprow < 0 or tempcol < 0 or temprow >= nrows or tempcol >= ncols:
                    continue
                if downstream_index(FlowDir[temprow][tempcol],temprow,tempcol) == (CurRow,CurCol):
                    if StreamLinks[temprow][tempcol] == StreamLinkValue:
                        break
                    elif StreamLinks[temprow][tempcol] != nodata:
                        continue
                    elif HillslopeMtx[temprow][tempcol] != 1:
                        HillslopeMtx[temprow][tempcol] = 2
                        fillUpstreamCells(FlowDir,StreamLinks,nodata,HillslopeMtx,2,temprow,tempcol)
            previous = current
            current = downstream_index(FlowDir[CurRow][CurCol],CurRow,CurCol)
    WriteAscFile(HillslpFile, HillslopeMtx,ncols,nrows,geotrans,nodata)
    
##  End Define key functions to Calculate Rill Network  ##
if __name__ == '__main__':
    ## Input params
    DEMsrc = r'E:\MasterBNU\RillMorphology\test\testdem'
    folder = r'E:\MasterBNU\RillMorphology\test\Extract2\1percent'
    threshold = 0
    #folder = r'E:\MasterBNU\RillMorphology\test\ExtractRills'
    #StreamFile = folder + os.sep + "streamlinks"
    #FlowDirFile = folder + os.sep + "flowdir"
    ## Output params
    HillslpFile = folder + os.sep + "HillSlp.asc"
    
    ## Run algorithms
    DEMbuf,DEMfil,FlowDirFile,FlowAccFile,CurvProfFile,CurvPlanFile = UtilHydroFiles(DEMsrc, folder)
    StreamFile,WatershedFile = GenerateNetworkFormDEM(DEMbuf,FlowDirFile,FlowAccFile,threshold,folder)
    DelineateHillslopes(StreamFile,FlowDirFile,HillslpFile)