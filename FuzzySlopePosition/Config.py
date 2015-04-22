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

RdgTag = 1
ShdTag = 1
BksTag = 1
FtsTag = 1
VlyTag = 1
## default RPI value range for Ridge, Shoulder, Back, Foot and valley.
AutoTypLocExtraction = True                              ## when AutoTypLocExtraction is Ture, the program will use RPIrange only.
RdgExtractionInfo = [[RPI,0.99,1.0],[ProfC_mask,0.0,0.0],[HorizC_mask,0.0,0.0],[Slope,0.0,0.0]]                                                    
ShdExtractionInfo = [[RPI,0.8,0.95],[ProfC_mask,0.0,0.0],[HorizC_mask,0.0,0.0],[Slope,0.0,0.0]]
BksExtractionInfo = [[RPI,0.5,0.7],[ProfC_mask,0.0,0.0],[HorizC_mask,0.0,0.0],[Slope,0.0,0.0]]
FtsExtractionInfo = [[RPI,0.2,0.3],[ProfC_mask,0.0,0.0],[HorizC_mask,0.0,0.0],[Slope,0.0,0.0]]
VlyExtractionInfo = [[RPI,0.0,0.1],[ProfC_mask,0.0,0.0],[HorizC_mask,0.0,0.0],[Slope,0.0,0.0]]

## Stage 3: Fuzzy slope position inference
AssignedInfParams = False
# Default	w1	r1	k1	w2	r2	k2
# B         6	2	0.5	6	2	0.5
# S         6	2	0.5	1	0	1
# Z         1	0	1	6	2	0.5

RdgInferenceInfo = [[RPI,'S',0.04,2,0.5,1,0,1],[ProfC_mask,'Z',1,0,1,4.72,2,0.5],[HorizC_mask,'Z',1,0,1,4.69,2,0.5],[Slope,'B',0.18,2,0.5,0.18,2,0.5]]
ShdInferenceInfo = [[RPI,'B',0.1,2,0.5,0.1,2,0.5],[ProfC_mask,'B',3.41,2,0.5,3.41,2,0.5],[HorizC_mask,'B',3.4,2,0.5,3.4,2,0.5],[Slope,'B',0.18,2,0.5,0.18,2,0.5]]
BksInferenceInfo = [[RPI,'B',0.2,2,0.5,0.2,2,0.5],[ProfC_mask,'B',2.93,2,0.5,2.93,2,0.5],[HorizC_mask,'B',3.49,2,0.5,3.49,2,0.5]]
FtsInferenceInfo = [[RPI,'B',0.2,2,0.5,0.2,2,0.5],[ProfC_mask,'S',3.71,2,0.5,1,0,1],[HorizC_mask,'S',2.89,2,0.5,1,0,1],[Slope,'Z',1,0,1,0.176,2,0.5]]
VlyInferenceInfo = [[RPI,'Z',1,0,1,0.1,2,0.5],[ProfC_mask,'S',4.12,2,0.5,1,0,1],[HorizC_mask,'S',4.47,2,0.5,1,0,1],[Slope,'Z',1,0,1,0.087,2,0.5]]

CalSecHardSlpPos = True                                 ## calculate second harden slope position or not
CalSPSI = True                                          ## calculate SPSI (Slope Position Sequence Index) or not, Be Caution, only when CalSecHardSlpPos is True, CalSPSI can be True
SPSImethod = 1                                          ## only when CalSPSI is True, the SPSImethod would be used. It can be 1,2,3

DistanceExponentForIDW = 8                              ## the default is 8




