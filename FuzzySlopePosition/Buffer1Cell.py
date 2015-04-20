#! /usr/bin/env python
#coding=utf-8

import os,sys
import arcpy
from arcpy import env

def Buffer1Cell(DEMsrc, DEMbuf, folder):
    env.workspace = folder
    arcpy.gp.overwriteOutput = 1
    arcpy.CheckOutExtension("Spatial")

    print "   --- DEM buffer 1 cell..."
    dem_des = arcpy.gp.describe(DEMsrc)
    cellsize = max(dem_des.MeanCellWidth,dem_des.MeanCellHeight)
    extent_src = dem_des.Extent
    extent_buf = arcpy.Extent(dem_des.Extent.XMin - cellsize,dem_des.Extent.YMin - cellsize,dem_des.Extent.XMax + cellsize,dem_des.Extent.YMax + cellsize)
    env.extent = extent_buf
    env.cellSize = cellsize
    Exec = "Con(IsNull(\"%s\"),FocalStatistics(\"%s\", NbrRectangle(3, 3, \"CELL\"), \"MEAN\", \"DATA\"),\"%s\")" % (DEMsrc, DEMsrc, DEMsrc)
    arcpy.gp.RasterCalculator_sa(Exec, DEMbuf)
if __name__ == '__main__':
    folder = r'E:\data\liyang\fuzzyslppos' 
    DEMsrc = folder + os.sep + 'dem.tif'
    DEMbuf = folder + os.sep + 'demB.tif'
    Buffer1Cell(DEMsrc, DEMbuf, folder)
    
