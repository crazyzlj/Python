#! /usr/bin/env python
#coding=utf-8
# Program: Fuzzy slope position extraction based on D-8 and D-infinity algorithms
# 
# Created By:  Liangjun Zhu
# Date From :  3/20/15
# Email     :  zlj@lreis.ac.cn
#

from Nomenclature import *
from Config import *
from Util import *
import TauDEM
#from shutil import copy2
import time

# Stage 1: Preprocessing for Slope, Curvature, RPI
def PreProcessing(model):
    startT = time.time()
    logStatus = open(log_preproc, 'w')
    if model == 0:
        logStatus.write("Preprocessing based on D8 flow model.\n")
    elif model ==1:
        logStatus.write("Preprocessing based on D-infinity flow model.\n")
    logStatus.flush()
    logStatus.write("[Preprocessing] [1/11] Converting DEM file format to GeoTiff...\n")
    logStatus.flush()
    TIFF2GeoTIFF(rawdem, dem)
    logStatus.write("[Preprocessing] [2/11] Generating negative DEM file for ridge sources extraction...\n")
    logStatus.flush()
    NegativeDEM(dem,negDEM)
    logStatus.write("[Preprocessing] [3/11] Removing pits...\n")
    logStatus.flush()
    TauDEM.pitremove(rawdem,inputProc,demfil,exeDir)
    TauDEM.pitremove(negDEM,inputProc,negDEMfil,exeDir)
    logStatus.write("[Preprocessing] [4/11] Flow direction and slope in radian...\n")
    logStatus.flush()
    TauDEM.D8FlowDir(demfil,inputProc,D8FlowDir,D8Slp,exeDir)
    if model == 0:
        TauDEM.D8FlowDir(negDEMfil,inputProc,negD8FlowDir,negD8Slp,exeDir)
    if model == 1:
        TauDEM.DinfFlowDir(demfil,inputProc,DinfFlowDir,DinfSlp,exeDir)
        TauDEM.DinfFlowDir(negDEMfil,inputProc,negDinfFlowDir,negDinfSlp,exeDir)
    logStatus.write("[Preprocessing] [5/11] Flow accumulation with Peuker Douglas stream sources as weightgrid...\n")
    logStatus.flush()    
    TauDEM.PeukerDouglas(demfil,centerweight,sideweight,diagonalweight,inputProc,PkrDglStream,exeDir)
    TauDEM.PeukerDouglas(negDEMfil,centerweight,sideweight,diagonalweight,inputProc,negPkrDglStream,exeDir)
    if model == 0:
        TauDEM.AreaD8(negD8FlowDir,'',negPkrDglStream,'false',inputProc,negD8ContriArea,exeDir)
    TauDEM.AreaD8(D8FlowDir,outlet,PkrDglStream,'false',inputProc,D8ContriArea,exeDir)
    if model == 1:
        TauDEM.AreaDinf(DinfFlowDir,outlet,PkrDglStream,'false',inputProc,DinfContriArea,exeDir)
        TauDEM.AreaDinf(negDinfFlowDir,'',negPkrDglStream,'false',inputProc,negDinfContriArea,exeDir)
    if model ==0:
        logStatus.write("[Preprocessing] [6/11] Generating stream source raster based on Drop Analysis...\n")
    elif model == 1:
        logStatus.write("[Preprocessing] [6/11] Generating stream source raster based on Threshold derived from D8 flow model drop analysis or assigned...\n")
    logStatus.flush()
    
    ## both D8 and D-infinity need to run drop analysis
    maxAccum, minAccum, meanAccum, STDAccum = GetRasterStat(D8ContriArea) #print maxAccum, minAccum, meanAccum, STDAccum
    if meanAccum - STDAccum < 0:
        minthresh = meanAccum
    else:
        minthresh = meanAccum - STDAccum
    maxthresh = meanAccum + STDAccum
    TauDEM.DropAnalysis(demfil,D8FlowDir,D8ContriArea,D8ContriArea,outlet,minthresh,maxthresh,numthresh,logspace,inputProc,drpFile, exeDir)
    drpf = open(drpFile,"r")
    tempContents=drpf.read()
    (beg,d8drpThreshold)=tempContents.rsplit(' ',1)
    drpf.close()
    global D8StreamThreshold
    if D8StreamThreshold == 0:
        D8StreamThreshold = d8drpThreshold
    TauDEM.Threshold(D8ContriArea,'',D8StreamThreshold,inputProc,D8Stream,exeDir)
    if model == 1:
        global DinfStreamThreshold
        if DinfStreamThreshold == 0:
            DinfStreamThreshold = d8drpThreshold
        TauDEM.Threshold(DinfContriArea,'',DinfStreamThreshold,inputProc,DinfStream,exeDir)
    logStatus.write("[Preprocessing] [7/11] Delineating sub-basins...\n")
    logStatus.flush()
    TauDEM.StreamNet(demfil,D8FlowDir,D8ContriArea,D8Stream,outlet,'false',inputProc,D8StreamOrd,NetTree,NetCoord,D8StreamNet,SubBasin, exeDir)
    logStatus.write("[Preprocessing] [8/11] Generating ridge source raster based on threshold method...\n")
    logStatus.flush()
    if model == 0:
        global negD8StreamThreshold
        if negD8StreamThreshold == 0:
            negD8StreamThreshold = d8drpThreshold
        TauDEM.Threshold(negD8ContriArea,'',negD8StreamThreshold,inputProc,negD8Stream,exeDir)
    elif model ==1:
        global negDinfStreamThreshold
        if negDinfStreamThreshold == 0:
            negDinfStreamThreshold = DinfStreamThreshold
        TauDEM.Threshold(negDinfContriArea,'',negDinfStreamThreshold,inputProc,negDinfStream,exeDir)
    logStatus.write("[Preprocessing] [9/11] Calculating RPI(Relative Position Index)...\n")
    logStatus.flush()
    if model == 0:
        TauDEM.D8DistDownToStream(D8FlowDir,demfil,D8Stream,D8DistDown,D8DownMethod,D8StreamTag,inputProc,exeDir)
        TauDEM.D8DistUpToRidge(D8FlowDir,demfil,D8DistUp,D8UpMethod,D8UpStats,inputProc,negD8Stream,exeDir)
        TauDEM.SimpleCalculator(D8DistDown,D8DistUp,RPID8,4,inputProc,exeDir)
    elif model == 1:
        TauDEM.DinfDistDown(DinfFlowDir,demfil,DinfStream,DinfDownStat,DinfDownMethod,'false',DinfDistDownWG,inputProc,DinfDistDown,exeDir)
        TauDEM.DinfDistUpToRidge(DinfFlowDir,demfil,DinfSlp,propthresh,DinfUpStat,DinfUpMethod,'false',inputProc,DinfDistUp,negDinfStream,exeDir)
        TauDEM.SimpleCalculator(DinfDistDown, DinfDistUp, RPIDinf, 4,inputProc,exeDir)

    logStatus.write("[Preprocessing] [10/11] Calculating Plan Curvature and Profile Curvature...\n")
    logStatus.flush()
    TauDEM.Curvature(inputProc,demfil,prof=ProfC,horiz=HorizC,exeDir=exeDir)
    logStatus.write("[Preprocessing] [11/11] Clip parameter raster to Subbasin's boundary...\n")
    logStatus.flush()
    if model == 0:
        TauDEM.SimpleCalculator(D8Slp,SubBasin,Slope,5,inputProc,exeDir)
        TauDEM.SimpleCalculator(RPID8,SubBasin,RPI,5,inputProc,exeDir)
        TauDEM.SimpleCalculator(ProfC,SubBasin,ProfC_mask,5,inputProc,exeDir)
        TauDEM.SimpleCalculator(HorizC,SubBasin,HorizC_mask,5,inputProc,exeDir)
    elif model == 1:
        TauDEM.SimpleCalculator(DinfSlp,SubBasin,Slope,5,inputProc,exeDir)
        TauDEM.SimpleCalculator(RPIDinf,SubBasin,RPI,5,inputProc,exeDir)
        TauDEM.SimpleCalculator(ProfC,SubBasin,ProfC_mask,5,inputProc,exeDir)
        TauDEM.SimpleCalculator(HorizC,SubBasin,HorizC_mask,5,inputProc,exeDir)
    logStatus.write("[Preprocessing] Preprocessing succeed!\n")
    logStatus.flush()
    endT = time.time()
    cost = (endT - startT)/60.
    logStatus.write("Time consuming: %.1f min.\n" % cost)
    logStatus.flush()
    logStatus.close()
        
    
    