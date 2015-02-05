#! /usr/bin/env python
#coding=utf-8
import os,numpy
import arcpy
from arcpy import env

from Util import *
from ShoulderLine import *

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
    

def basinIDIdx(basinID,value):
    flag = 0
    for basins in basinID:
        if value in basins:
            flag = 1
            return basinID.index(basins) + 1
    if flag == 0:
        return -9999
            

def ExtractBasinBoundary(Basin,ShoulderPts,FlowDirFile,basinID,BasinBoundary,tempDir):
    basin = ReadRaster(Basin).data
    flowdir = ReadRaster(FlowDirFile).data
    shoulderpts = ReadRaster(ShoulderPts).data 
    nodata = ReadRaster(Basin).noDataValue
    #print nodata
    geotrans = ReadRaster(Basin).geotrans
    nrows,ncols = basin.shape
    Boundary = numpy.ones((nrows,ncols))
    Boundary = Boundary * nodata
    
    for i in range(nrows):
        for j in range(ncols):
            if basin[i][j] != nodata:
                basin[i][j] = basinIDIdx(basinID,basin[i][j])
    for i in range(nrows):
        for j in range(ncols):
            if isEdge(basin,i,j,nodata):
                Boundary[i][j] = basin[i][j]
    ## find the unique values of boundary
    values = []
    for i in range(nrows):
        for j in range(ncols):
            if Boundary[i][j] != nodata:
                if not (Boundary[i][j] in values):
                    values.append(Boundary[i][j])
    values = list(set(values))
    finalBound = numpy.ones((nrows,ncols))
    finalBound = finalBound * nodata
    finalbndcell = []
    #for value in values:
    tempBound = numpy.ones((nrows,ncols))
    tempBound = tempBound * nodata
    for i in range(nrows):
        for j in range(ncols):
            if Boundary[i][j] == 1:
                tempBound[i][j] = 1
    
    GTPairNum,tempBound = simplifyBoundary(tempBound,nodata,geotrans)
    print "Greater than 2 near cells Num:%s" % GTPairNum
    while GTPairNum != 0:
        GTPairNum,tempBound = simplifyBoundary(tempBound,nodata,geotrans)
    #WriteAscFile(r'E:\MasterBNU\RillMorphology\20150130\2Rill\SnakeICC0.asc', tempBound,ncols,nrows,geotrans,nodata)
    #while DangleNum != 0 or GTPairNum != 0:
    #    DangleNum,tempBound = EliminateDanglePoint(tempBound,nodata)
    #    GTPairNum,tempBound = simplifyBoundary(tempBound,nodata)
    #    print "DangleNum:%s" % DangleNum
    tempBound = SnakeCreep(tempBound,shoulderpts,flowdir,nodata,100,geotrans,tempDir)
#    for i in range(nrows):
#        for j in range(ncols):
#            if tempBound[i][j] != nodata:
#                finalbndcell.append([i,j])
#    for cell in finalbndcell:
#        finalBound[cell[0]][cell[1]] = 1
#    num,Boundary = simplifyBoundary(Boundary,nodata)
#    print num
#    while num != 0:
#        num,Boundary = simplifyBoundary(Boundary,nodata)
    WriteAscFile(BasinBoundary, tempBound,ncols,nrows,geotrans,nodata)
    