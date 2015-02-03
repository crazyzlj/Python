#! /usr/bin/env python
#coding=utf-8
import os,numpy
import arcpy
from arcpy import env

from Util import *

def GenerateStreamNetByTHR(DEMbuf,FlowDirFile,FlowAccFile,threshold,folder):
    print "Generating initial stream network according to threshold of flow accumulation..."
    env.workspace = folder
    arcpy.gp.overwriteOutput = 1
    arcpy.CheckOutExtension("Spatial")
    threshold = float(threshold)
    maxAcc = float(str(arcpy.GetRasterProperties_management(FlowAccFile,"MAXIMUM")))
    if threshold < MINI_VALUE:
        threshold = maxAcc / 100
    elif threshold >= MINI_VALUE and threshold <= 1:
        threshold = maxAcc * threshold
    elif threshold > 1:
        threshold = threshold
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
    StreamOrderFile = folder + os.sep + "StreamOrder.shp"
    arcpy.sa.StreamToFeature("streamorder",FlowDirFile,StreamOrderFile,"NO_SIMPLIFY")
    Watershed = arcpy.sa.Watershed(FlowDirFile,"streamlinks","VALUE")
    Watershed.save("watershed")
    arcpy.RasterToPolygon_conversion("watershed","Watershed.shp","NO_SIMPLIFY","VALUE")
    WatershedFile = folder + os.sep + "watershed"
    StreamFile = folder + os.sep + "streamlinks"
    return (StreamFile,StreamOrderFile,WatershedFile)
def RillIndexCalc(StreamOrderFile,DEMbuf,tempDir,StatsDir):
    print "Calculating rill indexes..."
    #input StreamOrderFile and DEMbuf,output CSV files.
    env.workspace = tempDir
    arcpy.gp.overwriteOutput = 1
    arcpy.CheckOutExtension("Spatial")
    dem_des = arcpy.gp.describe(DEMbuf)
    env.extent = dem_des.Extent
    arcpy.FeatureVerticesToPoints_management(StreamOrderFile,"StreamNDsStart.shp","START")
    arcpy.FeatureVerticesToPoints_management(StreamOrderFile,"StreamNDsEnd.shp","END")
    arcpy.AddXY_management("StreamNDsStart.shp")
    arcpy.AddXY_management("StreamNDsEnd.shp")
    arcpy.sa.ExtractValuesToPoints("StreamNDsStart.shp",DEMbuf,"StreamNDsElevStart.shp","NONE", "VALUE_ONLY")
    arcpy.sa.ExtractValuesToPoints("StreamNDsEnd.shp",DEMbuf,"StreamNDsElevEnd.shp","NONE", "VALUE_ONLY")
    
def GenerateWatershedByStream(StreamFile,FlowDirFile, tempDir, WatershedFile):
    print "Regenerating watershed by real rill network..."
    arcpy.CheckOutExtension("spatial")
    arcpy.gp.overwriteOutput = 1
    
    tempStream = tempDir + os.sep + "StmNet"
    arcpy.ASCIIToRaster_conversion(StreamFile, tempStream,"INTEGER")    
    Watershed = arcpy.sa.Watershed(FlowDirFile,tempStream,"VALUE")
    tempWtshd = tempDir + os.sep + "WtShd"
    Watershed.save(tempWtshd)
    GRID2ASC(tempWtshd,WatershedFile)
    
def isEdge(raster,row,col,nodata):
    nrows,ncols = raster.shape
    if (row == 0 or row == nrows-1 or col == 0 or col == ncols-1) and raster[row][col] != nodata:
        return True
    elif raster[row][col] == nodata:
        return False
    else:
        count = 0
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ni = row + di
                nj = col + dj
                if raster[ni][nj] == nodata:
                    count = count + 1
        if count > 0:
            return True
        else:
            return False
    
def ExtractBasinBoundary(Basin,basinID,BasinBoundary):
    basin = ReadRaster(Basin).data
    nodata = ReadRaster(Basin).noDataValue
    #print nodata
    geotrans = ReadRaster(Basin).geotrans
    nrows,ncols = basin.shape
    Boundary = numpy.ones((nrows,ncols))
    if nodata != -9999:
        Boundary = Boundary * -9999
    else:
        Boundary = Boundary * nodata
    
    for i in range(nrows):
        for j in range(ncols):
            if basin[i][j] in basinID:
                #count = count + 1
                basin[i][j] = 1
            else:
                basin[i][j] = nodata
    for i in range(nrows):
        for j in range(ncols):
            if isEdge(basin,i,j,nodata):
                Boundary[i][j] = 1
    WriteAscFile(BasinBoundary, Boundary,ncols,nrows,geotrans,-9999)
    