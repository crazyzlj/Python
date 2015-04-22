#! /usr/bin/env python
#coding=utf-8

from Nomenclature import *
from Config import *
from Util import *
import TauDEM

def SelectTypLoc():
    TypLocItems = [["rdg",RdgExtConfig,RdgTyp, RdgTag,RdgExtractionInfo,DistanceExponentForIDW, BksInf,RdgInfConfig],\
                    ["shd",ShdExtConfig,ShdTyp, ShdTag,ShdExtractionInfo,DistanceExponentForIDW, BksInf,ShdInfConfig],\
                    ["bks",BksExtConfig,BksTyp, BksTag,BksExtractionInfo,DistanceExponentForIDW, BksInf,BksInfConfig],\
                    ["fts",FtsExtConfig,FtsTyp, FtsTag,FtsExtractionInfo,DistanceExponentForIDW, FtsInf,FtsInfConfig],\
                    ["vly",VlyExtConfig,VlyTyp, VlyTag,VlyExtractionInfo,DistanceExponentForIDW, VlyInf,VlyInfConfig]]
    for item in TypLocItems:
        ExtconfigInfo = open(item[1], 'w')
        ExtconfigInfo.write("ProtoTag\t%s\n" % str(item[3]))
        ExtconfigInfo.write("ParametersNUM\t%s\n" % str(len(item[4]))
        for param in item[4]:
            ExtconfigInfo.write("Parameters\t%s\t%s\t%s\n" % (param[0],str(param[1]),str(param[2])))
        ExtconfigInfo.write("OUTPUT\t%s\n" % item[2])
        ExtconfigInfo.close()
        TauDEM.SelectTypLocSlpPos(AutoTypLocExtraction,item[1],item[7],inputProc,exeDir)
        paramsConfList = []
        for line in open(item[7]):
            paramsConfList.append(line)

        configInfo = open(item[7], 'w')
        configInfo.write("PrototypeGRID\t%s\n" % item[2])
        configInfo.write("ProtoTag\t%s\n" % str(item[3]))
        configInfo.write("ParametersNUM\t%s\n" % str(len(paramsConfList)))
        for paramline in paramsConfList:
            configInfo.write("%s\n" % paramline)
        configInfo.write("DistanceExponentForIDW\t%s\n" % str(item[5]))
        configInfo.write("OUTPUT\t%s\n" % item[6])
        configInfo.close()
        
    print "Typical Locations Selected Done!"