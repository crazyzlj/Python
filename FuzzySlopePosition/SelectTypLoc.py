#! /usr/bin/env python
#coding=utf-8

from Nomenclature import *
from Util import *
import TauDEM
from Config import *
def SelectTypLoc():
    if AutoTypLocExtraction:
        for param in TerrainAttrDict.iterkeys():
            if param != 'RPI':
                RdgExtractionInfo.append([param,0.0,0.0])                                                            
                ShdExtractionInfo.append([param,0.0,0.0])
                BksExtractionInfo.append([param,0.0,0.0])
                FtsExtractionInfo.append([param,0.0,0.0])
                VlyExtractionInfo.append([param,0.0,0.0])                
   
    TypLocItems = [["rdg",RdgExtConfig,RdgTyp, RdgTag,RdgExtractionInfo,DistanceExponentForIDW, RdgInf,RdgInfRecommend, RdgExtLog],\
                    ["shd",ShdExtConfig,ShdTyp, ShdTag,ShdExtractionInfo,DistanceExponentForIDW, ShdInf,ShdInfRecommend, ShdExtLog],\
                    ["bks",BksExtConfig,BksTyp, BksTag,BksExtractionInfo,DistanceExponentForIDW, BksInf,BksInfRecommend, BksExtLog],\
                    ["fts",FtsExtConfig,FtsTyp, FtsTag,FtsExtractionInfo,DistanceExponentForIDW, FtsInf,FtsInfRecommend, FtsExtLog],\
                    ["vly",VlyExtConfig,VlyTyp, VlyTag,VlyExtractionInfo,DistanceExponentForIDW, VlyInf,VlyInfRecommend, VlyExtLog]]
    
    for item in TypLocItems:
        ModifyConfFile = False        ## if user modified the configuration file
        if not AutoTypLocExtraction:  ## if user modified default parameters
            for param in item[4]:
                if param[0] != 'RPI':
                    if param[1] == 0.0 and param[2] == 0.0:
                        ModifyConfFile = True
        if AutoTypLocExtraction or not ModifyConfFile:
            ExtconfigInfo = open(item[1], 'w')
            ExtconfigInfo.write("ProtoTag\t%s\n" % str(item[3]))
            ExtconfigInfo.write("ParametersNUM\t%s\n" % str(len(item[4])))
            for param in item[4]:
                ExtconfigInfo.write("Parameters\t%s\t%s\t%s\t%s\n" % (param[0],TerrainAttrDict.get(param[0]),str(param[1]),str(param[2])))
            ExtconfigInfo.write("OUTPUT\t%s\n" % item[2])
            ExtconfigInfo.close()
        TauDEM.SelectTypLocSlpPos(item[1],item[7],inputProc,item[8],exeDir)
    print "Typical Locations Selected Done!"