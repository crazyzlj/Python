#! /usr/bin/env python
#coding=utf-8

import os,sys
from osgeo import gdal
from osgeo import osr
from gdalconst import *
import numpy

def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
def mkdir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
def makeResultFolders(rootdir,model,preprocess):
    print "Making results' folders..."
    if not os.path.isdir(rootdir):
        if rootdir != "":
            mkdir(rootdir)
        else:
            rootdir = currentPath() + os.sep + "FuzzySlpPos"
            mkdir(rootdir)
    
    if model == 0:
        PreprocessDir = rootdir + os.sep + "D8preDir"
        negDEMDir = rootdir + os.sep + "negD8Dir"
    else:
        PreprocessDir = rootdir + os.sep + "DinfpreDir"
        negDEMDir = rootdir + os.sep + "negDinfDir"
    ParamDir = rootdir + os.sep + "Params" ## contains RPI,Curvature,Slope etc.
    logDir = rootdir + os.sep + "Log"
    outputDir = rootdir + os.sep + "FuzzySlpPos"
    TypLocDir = rootdir + os.sep + "TypLoc"
    ConfDir = rootdir + os.sep + "Config"
    if preprocess:
        mkdir(PreprocessDir)
        mkdir(negDEMDir)
    mkdir(ParamDir)
    mkdir(outputDir)
    mkdir(logDir)
    mkdir(TypLocDir)
    mkdir(ConfDir)
    return (PreprocessDir,negDEMDir, ParamDir,logDir, TypLocDir,ConfDir,outputDir)

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

def TIFF2GeoTIFF(tif,geotif, gdalType=gdal.GDT_Float32):
    print "Convering TIFF format to GeoTIFF..."
    rstFile = ReadRaster(tif)
    WriteGTiffFile(geotif, rstFile.nRows, rstFile.nCols, rstFile.data, rstFile.geotrans, rstFile.srs, rstFile.noDataValue, gdalType)

def GetRasterStat(rasterFile):
    dataset = gdal.Open(rasterFile,GA_ReadOnly)
    if not dataset is None:
        band = dataset.GetRasterBand(1)
        max = band.GetMaximum()
        min = band.GetMinimum()
        if max is None or min is None:
            (min,max) = band.ComputeRasterMinMax(1)
        mean, std = band.ComputeBandStats()
        band = None
        dataset = None
        return (max,min,mean,std)
    dataset = None

def RPICal(distDown, distUp, RPI):
    down = ReadRaster(distDown)
    up = ReadRaster(distUp)
    temp = down.data < 0
    rpiData = numpy.where(temp,down.noDataValue,down.data / (down.data + up.data))
    WriteGTiffFile(RPI, down.nRows, down.nCols, rpiData, down.geotrans, down.srs, down.noDataValue, gdal.GDT_Float32)
    
def NegativeDEM(DEM, negDEM):
    origin = ReadRaster(DEM)
    max = numpy.max(origin.data)
    temp = origin.data < 0
    neg = numpy.where(temp,origin.noDataValue,max - origin.data)
    WriteGTiffFile(negDEM, origin.nRows, origin.nCols, neg, origin.geotrans, origin.srs, origin.noDataValue, gdal.GDT_Float32)