#! /usr/bin/env python
#coding=utf-8
from Util import *
from Hillslope import *

def IdentifyRillRidges(HillslpFile,StreamFile,FlowDirFile,FlowAccFile,WatershedFile,DEMfil,folder):
#    header = "RillID,NodeID,DEM_R,DEM_L,CurvProf_R,CurvProf_L,CurvPlan_R,CurvPlan_L"
#    f = open(ProfileStats, 'w')
#    f.write(header)
#    f.close()
    StreamLinks = ReadRaster(StreamFile).data
    nrows,ncols = StreamLinks.shape
    nodata = ReadRaster(StreamFile).noDataValue
    geotrans = ReadRaster(StreamFile).geotrans
    Hillslp = ReadRaster(HillslpFile).data
    FlowDir = ReadRaster(FlowDirFile).data
    FlowAcc = ReadRaster(FlowAccFile).data
    Watershed = ReadRaster(WatershedFile).data
    #CurvProf = ReadRaster(CurvProfFile).data
    #CurvPlan = ReadRaster(CurvPlanFile).data
    DEM = ReadRaster(DEMfil).data
    RillStartIdx = GetRillStartIdx(StreamLinks,nodata,FlowDir)
    RillProfInfo = []
    RillEdge = numpy.ones((nrows,ncols))
    RillEdge = RillEdge * nodata
    RealRill = numpy.ones((nrows,ncols))
    RealRill = RealRill * nodata
    Accum = []
    AccumAll = []
    for rillIdx in RillStartIdx:
        row = rillIdx[0]
        col = rillIdx[1]
        print row,col
        RillId = StreamLinks[row][col]
        # Begin with the second cell
        row,col = downstream_index(FlowDir[row][col],row,col)
        NodeId = 0
        DEML = []
        DEMR = []
        DEMProf = []        
        while not(row <0 or col <0 or row >= nrows or col >= ncols) and StreamLinks[row][col] == RillId and Watershed[row][col] == RillId:
            DirIdx = DIR_VALUES.index(FlowDir[row][col])
            AccumAll.append(FlowAcc[row][col])
            DirIdxL = (DirIdx - 2) if (DirIdx - 2) >= 0 else DirIdx + 6
            DirIdxR = (DirIdx + 2) if (DirIdx + 2) <= 7 else DirIdx - 6
            deltaL = DIR_ITEMS[DIR_VALUES[DirIdxL]]
            deltaR = DIR_ITEMS[DIR_VALUES[DirIdxR]]
            ModifyL = LEFT_DELATA[DIR_VALUES[DirIdxL]]
            ModifyR = RIGHT_DELATA[DIR_VALUES[DirIdxL]]
            DEML.append(DEM[row][col])
            DEMR.append(DEM[row][col])
            temprowL = row + deltaL[0]
            tempcolL = col + deltaL[1]
            temprowR = row + deltaR[0]
            tempcolR = col + deltaR[1]
#            temprowL = row + deltaL[0] + ModifyL[0]
#            tempcolL = col + deltaL[1] + ModifyL[1]
#            temprowR = row + deltaR[0] + ModifyR[0]
#            tempcolR = col + deltaR[1] + ModifyR[1]
#
            while not(temprowL <0 or tempcolL <0 or temprowL >= nrows or tempcolL >= ncols) and StreamLinks[temprowL][tempcolL] == nodata and Watershed[temprowL][tempcolL] == RillId and Hillslp[temprowL][tempcolL] == 2:
                DEML.append(DEM[temprowL][tempcolL])
                temprowL = temprowL + deltaL[0]
                tempcolL = tempcolL + deltaL[1]
            while not(temprowR <0 or tempcolR <0 or temprowR >= nrows or tempcolR >= ncols) and StreamLinks[temprowR][tempcolR] == nodata and Watershed[temprowR][tempcolR] == RillId and Hillslp[temprowR][tempcolR] == 1:
                DEMR.append(DEM[temprowR][tempcolR])
                temprowR = temprowR + deltaR[0]
                tempcolR = tempcolR + deltaR[1]
            if ((max(DEML) - DEML[0] >= 10) or (max(DEMR) - DEMR[0] >= 10)) and geotrans[1] * (len(DEML) + len(DEMR) - 1) >= 10:
                DEMProf = list(reversed(DEMR)) + DEML[1:]
            if DEMProf != []:
                RillProfInfo.append([RillId,NodeId,DEMProf])
                RealRill[row][col] = RillId
                RillEdge[row][col] = RillId
                RillEdge[temprowR - deltaR[0]][tempcolR - deltaR[1]] = RillId
                RillEdge[temprowL - deltaL[0]][tempcolL - deltaL[1]] = RillId
                Accum.append(FlowAcc[row][col])
 
            row,col = downstream_index(FlowDir[row][col],row,col)
            NodeId = NodeId + 1
            DEML = []
            DEMR = []
            DEMProf = []            
#    for i in RillProfInfo:
#        print i
    Accum.sort()
    AccumAll.sort()
    print Accum
    print AccumAll
    WriteAscFile(folder + os.sep + "RealRill.asc", RealRill,ncols,nrows,geotrans,nodata)
    WriteAscFile(folder + os.sep + "RillEdge.asc", RillEdge,ncols,nrows,geotrans,nodata)

    
    
