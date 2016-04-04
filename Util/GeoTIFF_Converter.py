#! /usr/bin/env python
#coding=utf-8

## GeoTIFF Converter
## Convert other grid format to GeoTIFF
## Any Grid format supported by GDAL is permitted
## Coded by Liangjun Zhu, 2015-11-29

from osgeo import gdal
from osgeo import osr
from osgeo import gdalconst
from gdalconst import *
import numpy

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

def Raster2GeoTIFF(tif,geotif, gdalType=gdal.GDT_Float32):
    print "Convering TIFF format to GeoTIFF..."
    rstFile = ReadRaster(tif)
    WriteGTiffFile(geotif, rstFile.nRows, rstFile.nCols, rstFile.data, rstFile.geotrans, rstFile.srs, rstFile.noDataValue, gdalType)
    print "Mission done!"
def GRID2ASC(tif,asc):
    print "Convering Raster format to ASC file..."
    rstFile = ReadRaster(tif)
    WriteAscFile(asc, rstFile.data, rstFile.nCols, rstFile.nRows, rstFile.geotrans, rstFile.noDataValue)
    print "Mission done!"
    

if __name__ == '__main__':
    rawDEM = r'E:\github-zlj\parallel_RPI_demo\data\testDEM.tif'
    GeoTiff  = r'E:\github-zlj\parallel_RPI_demo\data\DEM.tif'
    Raster2GeoTIFF(rawDEM, GeoTiff)
    ASC = r'E:\github-zlj\parallel_RPI_demo\data\DEM.asc'
    GRID2ASC(rawDEM, ASC)
