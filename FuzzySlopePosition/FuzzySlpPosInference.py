#! /usr/bin/env python
#coding=utf-8

from Nomenclature import *
from Util import *
import TauDEM
from Config import *
def FuzzySlpPosInference():
    RPIExtInfo = [RdgExtractionInfo[0],ShdExtractionInfo[0],BksExtractionInfo[0],FtsExtractionInfo[0],VlyExtractionInfo[0]]
    tempw = RPIExtInfo[0][2] - RPIExtInfo[1][2]
    RdgInferenceInfo.append(['RPI','S',tempw,2,0.5,1,0,1]) # Ridge:S: w1 = Rdg.max – Shd.max
    tempw = max(RPIExtInfo[1][1]-RPIExtInfo[2][2],RPIExtInfo[0][1]-RPIExtInfo[1][2])
    ShdInferenceInfo.append(['RPI','B',tempw,2,0.5,tempw,2,0.5]) # Shoulder slope:B: w1 = w2 = max(Shd.min – Bks.max, Rdg.min – Shd.max)
    tempw = max(RPIExtInfo[2][1]-RPIExtInfo[3][2],RPIExtInfo[1][1]-RPIExtInfo[2][2])
    BksInferenceInfo.append(['RPI','B',tempw,2,0.5,tempw,2,0.5]) # Back slope:B: w1 = w2 = max(Bks.min – Fts.max, Shd.min – Bks.max)
    tempw = max(RPIExtInfo[3][1]-RPIExtInfo[4][2],RPIExtInfo[2][1]-RPIExtInfo[3][2])
    FtsInferenceInfo.append(['RPI','B',tempw,2,0.5,tempw,2,0.5]) # Foot slope:B: w1 = w2 = max(Fts.min – Vly.max, Bks.min – Fts.max)
    tempw = RPIExtInfo[3][1] - RPIExtInfo[4][2]
    VlyInferenceInfo.append(['RPI','Z',1,0,1,tempw,2,0.5]) # Valley:Z: w2 = Fts.min – Vly.max = 0.1

    SlpPosItems = [[RdgInfConfig,RdgTyp, RdgTag, RdgInferenceInfo,DistanceExponentForIDW, RdgInf, RdgInfRecommend],\
                    [ShdInfConfig,ShdTyp, ShdTag, ShdInferenceInfo,DistanceExponentForIDW, ShdInf, ShdInfRecommend],\
                    [BksInfConfig,BksTyp, BksTag, BksInferenceInfo,DistanceExponentForIDW, BksInf,BksInfRecommend],\
                    [FtsInfConfig,FtsTyp,FtsTag, FtsInferenceInfo,DistanceExponentForIDW, FtsInf,FtsInfRecommend],\
                    [VlyInfConfig,VlyTyp, VlyTag, VlyInferenceInfo,DistanceExponentForIDW, VlyInf,VlyInfRecommend]]
    

                    
    for SlpPosItem in SlpPosItems:
        ModifyInfConfFile = False  ## modify the configuration file
        if not AutoInfParams:     ## if not use automatically recommended parameters
            for param in SlpPosItem[3]:
                if param[0] != 'RPI':
                    if param[1] == 'B' and param[2] == 6 and param[3] == 2 and param[4] == 0.5 and param[5] == 6 and param[6] == 2 and param[7] == 0.5:
                        ModifyInfConfFile = True
                    elif param[1] == 'S' and param[2] == 6 and param[3] == 2 and param[4] == 0.5 and param[5] == 1 and param[6] == 0 and param[7] == 1:
                        ModifyInfConfFile = True
                    elif param[1] == 'Z' and param[2] == 1 and param[3] == 0 and param[4] == 1 and param[5] == 6 and param[6] == 2 and param[7] == 0.5:
                        ModifyInfConfFile = True
            if not ModifyInfConfFile:
                configInfo = open(SlpPosItem[0], 'w')
                configInfo.write("PrototypeGRID\t%s\n" % SlpPosItem[1])
                configInfo.write("ProtoTag\t%s\n" % str(SlpPosItem[2]))
                configInfo.write("ParametersNUM\t%s\n" % str(len(SlpPosItem[3])))
                for param in SlpPosItem[3]:
                    configInfo.write("Parameters\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (TerrainAttrDict.get(param[0]),param[1],str(param[2]),str(param[3]),str(param[4]),str(param[5]),str(param[6]),str(param[7])))
                configInfo.write("DistanceExponentForIDW\t%s\n" % str(SlpPosItem[4]))
                configInfo.write("OUTPUT\t%s\n" % SlpPosItem[5])
                configInfo.flush()
                configInfo.close()
        else:
            paramsConfList = []
            for line in open(SlpPosItem[6]):
                paramsConfList.append(line)
            configInfo = open(SlpPosItem[0], 'w')
            configInfo.write("PrototypeGRID\t%s\n" % SlpPosItem[1])
            configInfo.write("ProtoTag\t%s\n" % str(SlpPosItem[2]))
            configInfo.write("ParametersNUM\t%s\n" % str(len(paramsConfList)+1))
            for param in SlpPosItem[3]:
                if param[0] == 'RPI':
                    configInfo.write("Parameters\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (TerrainAttrDict.get(param[0]),param[1],str(param[2]),str(param[3]),str(param[4]),str(param[5]),str(param[6]),str(param[7])))
            for paramline in paramsConfList:
                configInfo.write("%s" % paramline)
            configInfo.write("DistanceExponentForIDW\t%s\n" % str(SlpPosItem[4]))
            configInfo.write("OUTPUT\t%s\n" % SlpPosItem[5])
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
    
