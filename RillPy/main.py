#! /usr/bin/env python
#coding=utf-8
"""
@Created   : 2015-1-6
@Revised   : 2015-1-28 Divided into seperate files for better version control
          
@author    : Liangjun Zhu
@summary   : Delineating and Extracting hillslopes and real rill from DEM.
@param     : DEMsrc, rootdir, streamTHR
@requires  : ArcGIS 10.x, gdal, Scipy
@references: Detail information will be found in README.txt.
@contract  : zlj@lreis.ac.cn
"""
import os
import Util
import Subbasin
import Hillslope
import Rill
import ShoulderLine

if __name__ == '__main__':
    ## Input params
    DEMsrc = r'E:\MasterBNU\RillMorphology\test\testdem'
    rootdir = r'E:\MasterBNU\RillMorphology\20150130'
    streamTHR = 0.01

    ## Run algorithms
    tempDir,PreprocessDir,RillExtDir,StatsDir = Util.makeResultFolders(rootdir)
#    DEMbuf,DEMfil,SlopeFile,SOSFile,AspectFile,FlowDirFile,FlowAccFile,CurvProfFile,CurvPlanFile = Util.UtilHydroFiles(DEMsrc, PreprocessDir)
#    StreamFile,StreamOrderFile,WatershedFile = Subbasin.GenerateStreamNetByTHR(DEMbuf,FlowDirFile,FlowAccFile,streamTHR,tempDir)
#    Subbasin.RillIndexCalc(StreamOrderFile,DEMbuf,tempDir,StatsDir)

    HillslpFile = RillExtDir + os.sep + "HillSlp.asc"
    #Hillslope.DelineateHillslopes(StreamFile,FlowDirFile,HillslpFile)    

    DEMfil = PreprocessDir + os.sep + "DEMfil"
    StreamFile = tempDir + os.sep + "StreamLinks"
    WatershedFile = tempDir + os.sep + "watershed"
    AspectFile = PreprocessDir + os.sep + "aspect"
    SlopeFile = PreprocessDir + os.sep + "slope"
    SOSFile = PreprocessDir + os.sep + "sos"
    CurvProfFile = PreprocessDir + os.sep + "curvprof"
    FlowDirFile = PreprocessDir + os.sep + "flowdir"
    FlowAccFile = PreprocessDir + os.sep + "flowacc"
    UpStreamRouteFile = RillExtDir + os.sep + "UpstreamRoute.txt"
    UpStreamRouteShp = RillExtDir + os.sep + "UpstreamRoute.shp"
    ShoulderptsFile = RillExtDir + os.sep + "Shoulderpts.asc"
    RealrillFile1 = RillExtDir + os.sep + "Realrill1.asc"
    RealrillFile2 = RillExtDir + os.sep + "Realrill2.asc"
    RillEdgeFile = RillExtDir + os.sep + "RealEdge.asc"
    RealRillFinal = RillExtDir + os.sep + "RealRill.asc"
    RillStFile = RillExtDir + os.sep + "RealRillFinal.asc"
    OrderStFile = RillExtDir + os.sep + "RillOrderFinal.asc"
    FinalWtdFile = RillExtDir + os.sep + "WatershedFinal.asc"
    HillslpFinalFile = RillExtDir + os.sep + "HillslpFinal.asc"
    UpStreamRouteFinalFile = RillExtDir + os.sep + "UpstreamRouteFinal.txt"
    UpStreamRouteFinalShp = RillExtDir + os.sep + "UpstreamRouteFinal.shp"
    ShoulderptsFinalFile = RillExtDir + os.sep + "ShoulderptsFinal.asc"
    RealrillFile1Final = RillExtDir + os.sep + "Realrill1final.asc"
    ShoulderptsFinalEli = RillExtDir + os.sep + "ShoulderptsFinalEli.asc"
    #Rill.UpStreamRoute(DEMfil,WatershedFile,HillslpFile,StreamFile,FlowDirFile,RillExtDir,UpStreamRouteFile,UpStreamRouteShp)
    #Rill.Shoulderpts(UpStreamRouteFile,DEMfil,SlopeFile,SOSFile,RillExtDir,ShoulderptsFile,RealrillFile1)
    #Rill.IdentifyRillRidges(HillslpFile,StreamFile,FlowDirFile,FlowAccFile,WatershedFile,DEMfil,RealrillFile2,RillEdgeFile)
    #Rill.RelinkRealRill(RealrillFile1,RealrillFile2,StreamFile,FlowDirFile,RealRillFinal)
    #Rill.SimplifyByRillOrder(RealRillFinal,FlowDirFile,tempDir,5,RillStFile,OrderStFile)
    #Subbasin.GenerateWatershedByStream(RillStFile,FlowDirFile, tempDir, FinalWtdFile)
    #Hillslope.DelineateHillslopes(RillStFile,FlowDirFile,HillslpFinalFile)
    #Rill.UpStreamRoute(DEMfil,FinalWtdFile,HillslpFinalFile,RillStFile,FlowDirFile,RillExtDir,UpStreamRouteFinalFile,UpStreamRouteFinalShp)
    #Rill.Shoulderpts(UpStreamRouteFinalFile,DEMfil,SlopeFile,SOSFile,RillExtDir,ShoulderptsFinalFile,RealrillFile1Final)
    Util.RemoveLessPts(ShoulderptsFinalFile,5,ShoulderptsFinalEli)
       
    ## Snake model to generate continuous shoulder lines
    #alpha = 25
    #beta = 5
    #ShoulderPtsOrig = RillExtDir + os.sep + "ShoulderPtsOrig.asc"
    #ShoulderLine.IdentifyRillShoulderPts(AspectFile,SlopeFile,CurvProfFile,alpha,beta,ShoulderPtsOrig)
    #num = 50
    #ShoulderPts = RillExtDir + os.sep + "ShoulderPts.asc"
    #Util.RemoveLessPts(ShoulderPtsOrig,num,ShoulderPts)
    #Basin = PreprocessDir + os.sep + "basin"
    #Watershed = tempDir + os.sep + "watershed"
    #basinID = [1,4,25,26]
    #BasinBoundary = PreprocessDir + os.sep + "basinBounday.asc"
    #Subbasin.ExtractBasinBoundary(Basin,basinID,BasinBoundary)
    #Shoulder = RillExtDir + os.sep + "Shoulder.asc"
    #ShoulderLine.RillShoulderSegement(BasinBoundary,FlowDirFile,ShoulderPts,Shoulder)
    #ShoulderLine.RillShoulder(Watershed,FlowDirFile,ShoulderPts,tempDir,Shoulder)