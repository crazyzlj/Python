#! /usr/bin/env python
#coding=utf-8
# Program: Fuzzy slope position extraction based on D-8 and D-infinity algorithms
# 
# Created By:  Liangjun Zhu
# Date From :  3/20/15
# Email     :  zlj@lreis.ac.cn
#

# Config
# This file contains all configuration for running the Fuzzy Slope Postion workflow.

## Stage 0: Overall setting
exeDir = r'E:\coding\Taudem5PCVS2010Soln_512\Taudem5PCVS2010\Release'  ## if the executable files' path is in the environmental path, this exeDir = None
inputProc = 8                                            ## parallel processor number
## Stage 1: Preprocessing from DEMsrc
FlowModel = 1                                            ## 0 represents D8 flow model, and 1 represent D-infinity model
#rootDir = r'E:\Anhui\FuzzySlpPosNew\D8'                     ## workspace
#rawdem = r'E:\Anhui\FuzzySlpPosNew\Input\dem10Buf.tif'   ## input dem, be caution! DEM file should have one cell buffer
#outlet = r'E:\Anhui\FuzzySlpPosNew\Input\outlet_10m.shp' ## input outlet shapefile, be caution! The outlet point should locate at least one cell inner the DEM boundary

rootDir = r'E:\data\liyang\fuzzyslppos\Dinf'  ## liyang DEm
rawdem = r'E:\data\liyang\fuzzyslppos\demBuf.tif'
outlet = r'E:\data\liyang\fuzzyslppos\outlet.shp'

centerweight = 0.4                                       ## Center Smoothing Weight, default is 0.4, for Peuker Douglas algorithm
sideweight = 0.1                                         ## Side Smoothing Weight, default is 0.1, for Peuker Douglas algorithm
diagonalweight = 0.05                                    ## Diagonal Smoothing Weight, default is 0.05, for Peuker Douglas algorithm
numthresh = 20                                           ## the number of steps to divide the search range into when looking for possible threshold values using drop analysis
logspace = 'true'                                        ## 'true' means use logarithmic spacing for threshold values, 'false' means linear spacing

D8StreamThreshold = 0                                    ## for D8 stream extraction from DEM, default is 0, which means the value is determined by drop analysis
negD8StreamThreshold = 0                                 ## for D8 ridge extraction from negative DEM, default is 0, which indicate that the value is equal to D8StreamThreshold

D8DownMethod = 'Surface'                                 ## for D8DistDownToStream, it can be Horizontal, Vertical, Pythagoras and Surface, the default is 'Surface'
D8StreamTag = 1                                          ## for D8DistDownToStream, it should be integer, the default is 1
D8UpMethod =  'Surface'                                  ## for D8DistUpToRidge, it can be Horizontal, Vertical, Pythagoras and Surface, the default is 'Surface'
D8UpStats = 'Average'                                    ## for D8DistUpToRidge, it can be Average, Maximum, Minimum

DinfStreamThreshold = 0                                  ## for Dinf stream extraction from DEM, default is 0, which means the value is equal to D8StreamThreshold
negDinfStreamThreshold = 0                               ## for Dinf ridge extraction from negative DEM, default is 0, which means the value is equal to DinfStreamThreshold

DinfDownStat = 'Average'                                 ## used for D-infinity distance down, Average, Maximum, Minimum, and Average is the default
DinfDownMethod = 'Surface'                               ## Horizontal, Vertical, Pythagoras, Surface, and Surface is the default
DinfDistDownWG = ''                                      ## weight grid, the default is none
propthresh = 0.1                                         ## The proportion threshold parameter where only grid cells that contribute flow with a proportion greater than this user specified threshold (t) is considered to be upslope of any given grid cell
DinfUpStat = 'Average'                                   ## same as DinfDownStat
DinfUpMethod = 'Surface'                                 ## same as DinfDownMethod

## Stage 2: Selection of Typical Locations





## Stage 3: Fuzzy slope position inference
CalSecHardSlpPos = True                                ## calculate second harden slope position or not
CalSPSI = True                                         ## calculate SPSI (Slope Position Sequence Index) or not, Be Caution, only when CalSecHardSlpPos is True, CalSPSI can be True
SPSImethod = 1                                       ## only when CalSPSI is True, the SPSImethod would be used. It can be 1,2,3

DistanceExponentForIDW = 8                              ## the default is 8




