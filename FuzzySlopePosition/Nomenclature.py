#! /usr/bin/env python
#coding=utf-8

# This file contains predefined filenames.
import os,sys
from Util import makeResultFolders
from Config import *
####  Stage 0: Overall setting  ####
PreDir, negDir, ParamDir,LogDir, TypLocDir, ConfDir, FSPDir = makeResultFolders(rootDir,FlowModel,preprocess)
####  Stage 1: Preprocessing from DEMsrc  ####
dem = PreDir + os.sep + 'dem.tif'
demfil = PreDir + os.sep + 'demfil.tif'
log_preproc = LogDir + os.sep + 'log_preprocessing.txt'                   ## log file is used to record the process
HorizC = PreDir + os.sep + 'HorizC_o.tif'
ProfC = PreDir + os.sep + 'ProfC_o.tif'
## D8 flow model nomenclature
D8FlowDir = PreDir + os.sep + 'D8FlowDir.tif'
D8Slp = PreDir + os.sep + 'D8Slp.tif'
PkrDglStream = PreDir + os.sep + 'PkrDglStream.tif'
outletM = PreDir + os.sep + 'outletM.shp'
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
ProfC_mask = ParamDir + os.sep + 'ProfC.tif'
RPI = ParamDir + os.sep + 'RPI.tif'


#    ## Executable files' path
#    if platform.system() == "Windows":
#        exeDir = rootDir + os.sep + 'ExecWIN'
#    elif platform.system() == "Linux":
#        exeDir = rootDir + os.sep + 'ExecLINUX'

####   Stage 2: Selection of Typical Locations  ####

RdgExtConfig = ConfDir + os.sep + "RdgExtConfig.dat"
ShdExtConfig = ConfDir + os.sep + "ShdExtConfig.dat"
BksExtConfig = ConfDir + os.sep + "BksExtConfig.dat"
FtsExtConfig = ConfDir + os.sep + "FtsExtConfig.dat"
VlyExtConfig = ConfDir + os.sep + "VlyExtConfig.dat"
if ExtLog:
    RdgExtLog = LogDir + os.sep + "RdgExtLog.dat"
    ShdExtLog = LogDir + os.sep + "ShdExtLog.dat"
    BksExtLog = LogDir + os.sep + "BksExtLog.dat"
    FtsExtLog = LogDir + os.sep + "FtsExtLog.dat"
    VlyExtLog = LogDir + os.sep + "VlyExtLog.dat"
else:
    RdgExtLog = None
    ShdExtLog = None
    BksExtLog = None
    FtsExtLog = None
    VlyExtLog = None
    

RdgTyp = TypLocDir + os.sep + "RdgTyp.tif"
ShdTyp = TypLocDir + os.sep + "ShdTyp.tif"
BksTyp = TypLocDir + os.sep + "BksTyp.tif"
FtsTyp = TypLocDir + os.sep + "FtsTyp.tif"
VlyTyp = TypLocDir + os.sep + "VlyTyp.tif"

RdgInfRecommend = ConfDir + os.sep + "RdgInfRecommend.dat"
ShdInfRecommend = ConfDir + os.sep + "ShdInfRecommend.dat"
BksInfRecommend = ConfDir + os.sep + "BksInfRecommend.dat"
FtsInfRecommend = ConfDir + os.sep + "FtsInfRecommend.dat"
VlyInfRecommend = ConfDir + os.sep + "VlyInfRecommend.dat"


####   Stage 3: Fuzzy slope position inference  ####

RdgInfConfig = ConfDir + os.sep + "RdgInfConfig.dat"
ShdInfConfig = ConfDir + os.sep + "ShdInfConfig.dat"
BksInfConfig = ConfDir + os.sep + "BksInfConfig.dat"
FtsInfConfig = ConfDir + os.sep + "FtsInfConfig.dat"
VlyInfConfig = ConfDir + os.sep + "VlyInfConfig.dat"

RdgInf = FSPDir + os.sep + "RdgInf.tif"
ShdInf = FSPDir + os.sep + "ShdInf.tif"
BksInf = FSPDir + os.sep + "BksInf.tif"
FtsInf = FSPDir + os.sep + "FtsInf.tif"
VlyInf = FSPDir + os.sep + "VlyInf.tif"

HardenSlpPos = FSPDir + os.sep + "HardenSlpPos.tif"
MaxSimilarity = FSPDir + os.sep + "MaxSimilarity.tif"

SecHardenSlpPos = FSPDir + os.sep + "SecHardenSlpPos.tif"
SecMaxSimilarity = FSPDir + os.sep + "SecMaxSimilarity.tif"
    
SPSIfile = FSPDir + os.sep + "SPSI.tif"


