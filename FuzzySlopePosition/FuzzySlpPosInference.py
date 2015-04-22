#! /usr/bin/env python
#coding=utf-8
from Nomenclature import *
from Config import *
from Util import *
import TauDEM

def FuzzySlpPosInference():
    
    SlpPosItems = [[RdgInfConfig,RdgTyp, RdgTag, RdgInferenceInfo,DistanceExponentForIDW, RdgInf],\
                    [ShdInfConfig,ShdTyp, ShdTag, ShdInferenceInfo,DistanceExponentForIDW, ShdInf],\
                    [BksInfConfig,BksTyp, BksTag, BksInferenceInfo,DistanceExponentForIDW, BksInf],\
                    [FtsInfConfig,FtsTyp,FtsTag, FtsInferenceInfo,DistanceExponentForIDW, FtsInf],\
                    [VlyInfConfig,VlyTyp, VlyTag, VlyInferenceInfo,DistanceExponentForIDW, VlyInf]]
    for SlpPosItem in SlpPosItems:
        if AssignedInfParams:
            configInfo = open(SlpPosItem[0], 'w')
            configInfo.write("PrototypeGRID\t%s\n" % SlpPosItem[1])
            configInfo.write("ProtoTag\t%s\n" % str(SlpPosItem[2]))
            configInfo.write("ParametersNUM\t%s\n" % str(len(SlpPosItem[3])))
            for param in SlpPosItem[3]:
                configInfo.write("Parameters\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (param[0],param[1],str(param[2]),str(param[3]),str(param[4]),str(param[5]),str(param[6]),str(param[7])))
            configInfo.write("DistanceExponentForIDW\t%s\n" % str(SlpPosItem[4]))
            configInfo.write("OUTPUT\t%s\n" % SlpPosItem[5])
            configInfo.flush()
            configInfo.close()
        TauDEM.FuzzySlpPosInference(SlpPosItem[0],inputProc,exeDir)

    if not CalSecHardSlpPos:
        global SecHardenSlpPos
        SecHardenSlpPos=None
        global SecMaxSimilarity
        SecMaxSimilarity=None
        if not CalSPSI:
            global SPSIfile
            SPSIfile=None
    TauDEM.HardenSlpPos(RdgInf,ShdInf,BksInf,FtsInf,VlyInf,inputProc,HardenSlpPos,MaxSimilarity,sechard=SecHardenSlpPos,secsimi=SecMaxSimilarity,spsim=SPSImethod,spsi=SPSIfile,exeDir=exeDir)
    
