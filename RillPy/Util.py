# coding=utf-8
from osgeo import gdal
from osgeo import osr
import os
import sys
import math
import arcpy
from arcpy import env
import numpy

sys.setrecursionlimit(1000000)  ## to avoid the error: maximum recursion depth exceeded in cmp
##  Const Variables Definition  ##
DIR_ITEMS = {1  : (0, 1),
             2  : (1, 1),
             4  : (1, 0),
             8  : (1, -1),
             16 : (0, -1),
             32 : (-1, -1),
             64 : (-1, 0),
             128: (-1, 1)}
DIR_VALUES = [1, 2, 4, 8, 16, 32, 64, 128]
MINI_VALUE = 0.000001
LEFT_DELATA = {2  : (1, 0),
               8  : (0, -1),
               32 : (-1, 0),
               128: (0, 1),
               1  : (0, 0),
               4  : (0, 0),
               16 : (0, 0),
               64 : (0, 0)}
RIGHT_DELATA = {2  : (0, 1),
                8  : (1, 0),
                32 : (0, -1),
                128: (-1, 0),
                1  : (0, 0),
                4  : (0, 0),
                16 : (0, 0),
                64 : (0, 0)}


##  End Const Variables Definition  ##

##  Define Utility Functions  ##
def downstream_index(DIR_VALUE, i, j):
    drow, dcol = DIR_ITEMS[DIR_VALUE]
    return i + drow, j + dcol


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
        self.xMax = geotransform[0] + nCols * geotransform[1]
        self.yMax = geotransform[3]
        self.yMin = geotransform[3] + nRows * geotransform[5]


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
    # print srs.ExportToProj4()
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
""" % (xsize, ysize, geotransform[0] + 0.5 * geotransform[1], geotransform[3] - (ysize - 0.5) * geotransform[1],
       geotransform[1], noDataValue)

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
    ave = sum(qObs) / n
    a1 = 0
    a2 = 0
    for i in range(n):
        a1 = a1 + pow(qObs[i] - qSimu[i], 2)
        a2 = a2 + pow(qObs[i] - ave, 2)
    return 1 - a1 / a2


def RMSE(list1, list2):
    n = len(list1)
    s = 0
    for i in range(n):
        s = s + pow(list1[i] - list2[i], 2)
    return math.sqrt(s / n)


def StdEv(list1):
    n = len(list1)
    av = sum(list1) / n
    s = 0
    for i in range(n):
        s = s + pow(list1[i] - av, 2)
    return math.sqrt(s / n)


def ContinuousGRID(raster, i, j, idx):
    nrows, ncols = raster.shape
    value = raster[i][j]
    # idx = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if i + di >= 0 and i + di < nrows and j + dj >= 0 and j + dj < ncols:
                if raster[i + di][j + dj] == value and not (di == dj and di == 0):
                    if not idx.__contains__((i + di, j + dj)):
                        idx.append((i + di, j + dj))
                        ContinuousGRID(raster, i + di, j + dj, idx)
                        # idx = list(set(idx))
                        # return idx


def RemoveLessPts(RasterFile, num, OutputRaster):
    raster = ReadRaster(RasterFile).data
    nrows, ncols = raster.shape
    nodata = ReadRaster(RasterFile).noDataValue
    geotrans = ReadRaster(RasterFile).geotrans
    for i in range(nrows):
        for j in range(ncols):
            if raster[i][j] == 1:
                tempIdx = []
                ContinuousGRID(raster, i, j, tempIdx)
                tempIdx = list(set(tempIdx))
                count = tempIdx.__len__()
                for rc in tempIdx:
                    raster[rc[0]][rc[1]] = count
    for i in range(nrows):
        for j in range(ncols):
            if raster[i][j] <= int(num):
                raster[i][j] = nodata
            else:
                raster[i][j] = 1
    WriteAscFile(OutputRaster, raster, ncols, nrows, geotrans, nodata)


def RemoveLessPtsMtx(raster, nodata, num):
    nrows, ncols = raster.shape
    for i in range(nrows):
        for j in range(ncols):
            if raster[i][j] == 1:
                tempIdx = []
                ContinuousGRID(raster, i, j, tempIdx)
                tempIdx = list(set(tempIdx))
                count = tempIdx.__len__()
                for rc in tempIdx:
                    raster[rc[0]][rc[1]] = count
    for i in range(nrows):
        for j in range(ncols):
            if raster[i][j] <= int(num):
                raster[i][j] = nodata
            else:
                raster[i][j] = 1
    return raster


def GRID2ASC(GRID, ASC):
    grid = ReadRaster(GRID).data
    nodata = ReadRaster(GRID).noDataValue
    # print nodata
    geotrans = ReadRaster(GRID).geotrans
    nrows, ncols = grid.shape
    temp = numpy.ones((nrows, ncols))
    temp = temp * -9999
    for i in range(nrows):
        for j in range(ncols):
            if grid[i][j] != nodata:
                temp[i][j] = grid[i][j]
    WriteAscFile(ASC, temp, ncols, nrows, geotrans, -9999.0)


def GetUniqueValues(RasterFile):
    raster = ReadRaster(RasterFile).data
    nodata = ReadRaster(RasterFile).noDataValue
    # geotrans = ReadRaster(RasterFile).geotrans
    nrows, ncols = raster.shape
    value = []
    for i in range(nrows):
        for j in range(ncols):
            if raster[i][j] != nodata:
                if not (raster[i][j] in value):
                    value.append(raster[i][j])
    value = list(set(value))
    return value


##  End Utility Functions ##

## DEM Preprocessing  ##
def UtilHydroFiles(DEMsrc, folder):
    print "Calculating fundamental hydrological parameters from DEM..."
    env.workspace = folder
    arcpy.gp.overwriteOutput = 1
    arcpy.CheckOutExtension("Spatial")
    ## Set the source dem with one cell buffer to 
    ## avoid NODATA around the edges
    print "   --- DEM buffer 1 cell..."
    dem_des = arcpy.gp.describe(DEMsrc)
    cellsize = max(dem_des.MeanCellWidth, dem_des.MeanCellHeight)
    extent_src = dem_des.Extent
    extent_buf = arcpy.Extent(dem_des.Extent.XMin - cellsize, dem_des.Extent.YMin - cellsize,
                              dem_des.Extent.XMax + cellsize, dem_des.Extent.YMax + cellsize)
    env.extent = extent_buf
    env.cellSize = cellsize
    Exec = "Con(IsNull(\"%s\"),FocalStatistics(\"%s\", NbrRectangle(3, 3, \"CELL\"), \"MEAN\", \"DATA\"),\"%s\")" % (
    DEMsrc, DEMsrc, DEMsrc)
    arcpy.gp.RasterCalculator_sa(Exec, "DEMbuf")
    print "   --- fill depression..."
    env.extent = dem_des.Extent
    DEMfil = arcpy.sa.Fill(DEMsrc)
    DEMfil.save("DEMfil")
    print "   --- calculating aspect, slope, curvature, flow direction, flow accumulation, basin..."
    Aspect = arcpy.sa.Aspect("DEMfil")
    Slope = arcpy.sa.Slope("DEMfil", "DEGREE")

    Flowdir = arcpy.sa.FlowDirection("DEMfil", "NORMAL")
    Curvature = arcpy.sa.Curvature("DEMfil", "", "curvprof", "curvplan")
    Curvature.save("curv")
    Slope.save("slope")
    Aspect.save("aspect")
    Flowdir.save("flowdir")
    SOS = arcpy.sa.Slope("slope", "DEGREE")
    SOS.save("sos")
    FlowLen = arcpy.sa.FlowLength("flowdir", "DOWNSTREAM")
    FlowLen.save("flowlen")
    FlowAcc = arcpy.sa.FlowAccumulation("flowdir", "", "FLOAT")
    FlowAcc.save("flowacc")
    Basin = arcpy.sa.Basin("flowdir")
    Basin.save("basin")
    arcpy.RasterToPolygon_conversion("basin", "basin.shp", "NO_SIMPLIFY", "VALUE")

    DEMbuf = folder + os.sep + "DEMbuf"
    DEMfil = folder + os.sep + "DEMfil"
    SlopeFile = folder + os.sep + "slope"
    SOSFile = folder + os.sep + "sos"
    AspectFile = folder + os.sep + "aspect"
    FlowDirFile = folder + os.sep + "flowdir"
    FlowAccFile = folder + os.sep + "flowacc"
    CurvProfFile = folder + os.sep + "curvprof"
    CurvPlanFile = folder + os.sep + "curvplan"

    return (DEMbuf, DEMfil, SlopeFile, SOSFile, AspectFile, FlowDirFile, FlowAccFile, CurvProfFile, CurvPlanFile)


## End DEM Preprocessing ##

## Folder and file Functions ##
def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


def mkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def makeResultFolders(rootdir):
    print "Making results' folders..."
    if not os.path.isdir(rootdir):
        if rootdir != "":
            mkdir(rootdir)
        else:
            rootdir = currentPath() + os.sep + "RillPyResults"
            mkdir(rootdir)
    PreprocessDir = rootdir + os.sep + "1Preprocess"
    tempDir = rootdir + os.sep + "0Temp"
    RillExtDir = rootdir + os.sep + "2Rill"
    StatsDir = rootdir + os.sep + "3Stats"
    mkdir(PreprocessDir)
    mkdir(tempDir)
    mkdir(RillExtDir)
    mkdir(StatsDir)
    return (tempDir, PreprocessDir, RillExtDir, StatsDir)
    ## End Folder and file Functions ##
