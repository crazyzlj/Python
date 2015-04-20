#! /usr/bin/env python
#coding=utf-8
# Program: Fuzzy slope position extraction based on D-8 and D-infinity algorithms
# 
# Created By:  Liangjun Zhu
# Date From :  3/20/15
# Email     :  zlj@lreis.ac.cn
#
# Nomenclature
# This file contains predefined filenames.
import os,sys
from Util import makeResultFolders
from Config import *

####  Stage 0: Overall setting  ####
PreDir, negDir, ParamDir,LogDir, TypLocDir, FSPDir = makeResultFolders(rootDir,FlowModel)
####  Stage 1: Preprocessing from DEMsrc  ####
dem = PreDir + os.sep + 'dem.tif'
demfil = PreDir + os.sep + 'demfil.tif'
log_preproc = LogDir + os.sep + 'log_preprocessing.txt'                   ## log file is used to record the process
HorizC = PreDir + os.sep + 'ProfC_o.tif'
ProfC = PreDir + os.sep + 'ProfC_o.tif'
## D8 flow model nomenclature
D8FlowDir = PreDir + os.sep + 'D8FlowDir.tif'
D8Slp = PreDir + os.sep + 'D8Slp.tif'
PkrDglStream = PreDir + os.sep + 'PkrDglStream.tif'
D8ContriArea = PreDir + os.sep + 'D8ContriArea.tif'
drpFile = PreDir + os.sep + 'drpFile.txt'
D8Stream = PreDir + os.sep + 'D8Stream.tif'
D8DistDown = PreDir + os.sep + 'D8DistDown.tif'
D8DistUp = PreDir + os.sep + 'D8DistUp.tif'
RPID8 = PreDir + os.sep + 'RPID8.tif'
D8StreamOrd = PreDir + os.sep + 'D8Streamord.tif'
NetTree = PreDir + os.sep + 'NetTree.txt'
NetCoord = PreDir + os.sep + 'NetCoord.txt'
D8StreamNet = PreDir + os.sep + 'D8StreamNet.shp'
SubBasin = PreDir + os.sep + 'Subbasins.tif'

negDEM = negDir + os.sep + 'negdem10Buf.tif'  ## Negative DEM for ridge extraction
negDEMfil = negDir + os.sep + 'negdemfil.tif'
negD8FlowDir = negDir + os.sep + 'negD8FlowDir.tif'
negD8Slp = negDir + os.sep + 'negD8Slp.tif'
negPkrDglStream = negDir + os.sep + 'negPkrDgl.tif'
negD8ContriArea = negDir + os.sep + 'negD8ContriArea.tif'
negOrd = negDir + os.sep + 'negOrd.tif'
negUpslpLongLen = negDir + os.sep + 'negUpslpLongLen.tif'
negUpslpTotalLen = negDir + os.sep + 'negUpslpTotalLen.tif'
negD8Stream  = negDir + os.sep + 'negD8Stream.tif'

#### D-infinity flow model nomenclature
negDinfFlowDir = negDir + os.sep + 'negDinfFlowDir.tif'
negDinfSlp = negDir + os.sep + 'negDinfSlp.tif'
negDinfContriArea = negDir + os.sep + 'negDinfContriArea.tif'
negDinfStream  = negDir + os.sep + 'negDinfStream.tif'

DinfFlowDir = PreDir + os.sep + 'DinfFlowDir.tif'
DinfSlp = PreDir + os.sep + 'DinfSlp.tif'
DinfContriArea = PreDir + os.sep + 'DinfContriArea.tif'
DinfStream = PreDir + os.sep + 'DinfStream.tif'
DinfDistDown = PreDir + os.sep + 'DinfDistDown.tif'
DinfDistUp = PreDir + os.sep + 'DinfDistUp.tif'
RPIDinf = PreDir + os.sep + 'RPIDinf.tif'

## Params files
Slope = ParamDir + os.sep + 'Slp.tif'
HorizC_mask = ParamDir + os.sep + 'HorizC.tif'
#PlanC_mask = ParamDir + os.sep + 'PlanC.tif'
ProfC_mask = ParamDir + os.sep + 'ProfC.tif'
RPI = ParamDir + os.sep + 'RPI.tif'

#    ## Executable files' path
#    if platform.system() == "Windows":
#        exeDir = rootDir + os.sep + 'ExecWIN'
#    elif platform.system() == "Linux":
#        exeDir = rootDir + os.sep + 'ExecLINUX'

####   Stage 2: Selection of Typical Locations  ####

RdgTyp0 = TypLocDir + os.sep + "RdgTyp.tif"
ShdTyp0 = TypLocDir + os.sep + "ShdTyp.tif"
BksTyp0 = TypLocDir + os.sep + "BksTyp.tif"
FtsTyp0 = TypLocDir + os.sep + "FtsTyp.tif"
VlyTyp0 = TypLocDir + os.sep + "VlyTyp.tif"

RdgTyp = TypLocDir + os.sep + "RdgTyp1.tif"
ShdTyp = TypLocDir + os.sep + "ShdTyp1.tif"
BksTyp = TypLocDir + os.sep + "BksTyp1.tif"
FtsTyp = TypLocDir + os.sep + "FtsTyp1.tif"
VlyTyp = TypLocDir + os.sep + "VlyTyp1.tif"



####   Stage 3: Fuzzy slope position inference  ####

RdgConfig = TypLocDir + os.sep + "RdgConfig.dat"
ShdConfig = TypLocDir + os.sep + "ShdConfig.dat"
BksConfig = TypLocDir + os.sep + "BksConfig.dat"
FtsConfig = TypLocDir + os.sep + "FtsConfig.dat"
VlyConfig = TypLocDir + os.sep + "VlyConfig.dat"

RdgInf = FSPDir + os.sep + "RdgInf.tif"
ShdInf = FSPDir + os.sep + "ShdInf.tif"
BksInf = FSPDir + os.sep + "BksInf.tif"
FtsInf = FSPDir + os.sep + "FtsInf.tif"
VlyInf = FSPDir + os.sep + "VlyInf.tif"

RdgTag = 1
ShdTag = 1
BksTag = 1
FtsTag = 1
VlyTag = 1
# Default	w1	r1	k1	w2	r2	k2
# B         6	2	0.5	6	2	0.5
# S         6	2	0.5	1	0	1
# Z         1	0	1	6	2	0.5
RdgInferenceInfo = [[RPI,'S',0.04,2,0.5,1,0,1],[ProfC_mask,'Z',1,0,1,4.72,2,0.5],[HorizC_mask,'Z',1,0,1,4.69,2,0.5],[Slope,'B',0.18,2,0.5,0.18,2,0.5]]
ShdInferenceInfo = [[RPI,'B',0.1,2,0.5,0.1,2,0.5],[ProfC_mask,'B',3.41,2,0.5,3.41,2,0.5],[HorizC_mask,'B',3.4,2,0.5,3.4,2,0.5],[Slope,'B',0.18,2,0.5,0.18,2,0.5]]
BksInferenceInfo = [[RPI,'B',0.2,2,0.5,0.2,2,0.5],[ProfC_mask,'B',2.93,2,0.5,2.93,2,0.5],[HorizC_mask,'B',3.49,2,0.5,3.49,2,0.5]]
FtsInferenceInfo = [[RPI,'B',0.2,2,0.5,0.2,2,0.5],[ProfC_mask,'S',3.71,2,0.5,1,0,1],[HorizC_mask,'S',2.89,2,0.5,1,0,1],[Slope,'Z',1,0,1,0.176,2,0.5]]
VlyInferenceInfo = [[RPI,'Z',1,0,1,0.1,2,0.5],[ProfC_mask,'S',4.12,2,0.5,1,0,1],[HorizC_mask,'S',4.47,2,0.5,1,0,1],[Slope,'Z',1,0,1,0.087,2,0.5]]

HardenSlpPos = FSPDir + os.sep + "HardenSlpPos.tif"
MaxSimilarity = FSPDir + os.sep + "MaxSimilarity.tif"

SecHardenSlpPos = FSPDir + os.sep + "SecHardenSlpPos.tif"
SecMaxSimilarity = FSPDir + os.sep + "SecMaxSimilarity.tif"
    
SPSIfile = FSPDir + os.sep + "SPSI.tif"
