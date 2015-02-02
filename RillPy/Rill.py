#! /usr/bin/env python
#coding=utf-8
from Util import *
from Hillslope import *
import math,copy
def IdentifyRillRidges(HillslpFile,StreamFile,FlowDirFile,FlowAccFile,WatershedFile,DEMfil,RealRillFile,RillEdgeFile):
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
    RillEdge = RillEdge * -9999
    RealRill = numpy.ones((nrows,ncols))
    RealRill = RealRill * -9999
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
                RealRill[row][col] = 1
                #RealRill[row][col] = RillId
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
    #print Accum
    #print AccumAll
    WriteAscFile(RealRillFile, RealRill,ncols,nrows,geotrans,-9999)
    WriteAscFile(RillEdgeFile, RillEdge,ncols,nrows,geotrans,-9999)
def UpStreamCell(row,col,flowdir,stream,watershed,cWatershed,nodata,curBoundCells):
    nrows,ncols = flowdir.shape
    curUpCell = []
    for di in [-1,0,1]:
        for dj in [-1,0,1]:
            ci = row + di
            cj = col + dj
            if ci < 0 or cj < 0 or ci >= nrows or cj >= ncols:
                continue
            elif downstream_index(flowdir[ci][cj],ci,cj)==(row,col) and stream[ci][cj] == nodata and watershed[ci][cj] == cWatershed:
                curUpCell.append([ci,cj])
    if len(curUpCell) == 0:
        curBoundCells.append([row,col])
    else:
        for pt in curUpCell:
            cRow,cCol = pt
            UpStreamCell(cRow,cCol,flowdir,stream,watershed,cWatershed,nodata,curBoundCells)
def SingleDownstream(cell,flowdir,stream,nodata):
    curDownStream = []
    crow,ccol = cell
    curDownStream.append([crow,ccol])
    while stream[crow][ccol] == nodata :
        crow,ccol = downstream_index(flowdir[crow][ccol],crow,ccol)
        curDownStream.append([crow,ccol])
    return curDownStream
def UpStreamRoute(DEMfil,WatershedFile,HillslpFile,StreamFile,FlowDirFile,RillExtDir,UpStreamRouteFile,UpStreamRouteLenFile):
    stream = ReadRaster(StreamFile).data
    nrows,ncols = stream.shape
    nodata = ReadRaster(StreamFile).noDataValue
    geotrans = ReadRaster(StreamFile).geotrans
    hillslp = ReadRaster(HillslpFile).data
    flowdir = ReadRaster(FlowDirFile).data
    watershed = ReadRaster(WatershedFile).data
    demfil = ReadRaster(DEMfil).data
    UpStream = numpy.ones((nrows,ncols))
    UpStream = UpStream * -9999
    UpStreamShp = RillExtDir + os.sep + "UpStream.shp"
    
    StreamPts = []
    for i in range(nrows):
        for j in range(ncols):
            if(stream[i][j] != nodata):
                StreamPts.append((i,j))
    boundCells = []
    for pt in StreamPts:
        curBoundCells = []
        row,col = pt
        cWatershed = watershed[row][col]
        UpStreamCell(row,col,flowdir,stream,watershed,cWatershed,nodata,curBoundCells)
        boundCells.extend(curBoundCells)
    BoundRaster = numpy.ones((nrows,ncols))
    BoundRaster = BoundRaster * -9999
    segement_info = []
    segeLength_info = []
    # A list that will hold each of the Polyline objects
    for cell in boundCells:
        BoundRaster[cell[0]][cell[1]] = 1
        curSege = SingleDownstream(cell,flowdir,stream,nodata)
        curSegeLen = []
        curSegeLen.append(1)
        for i in range(1,len(curSege)):
            if flowdir[curSege[i][0]][curSege[i][1]] in [2,8,32,128]:
                curSegeLen.append(curSegeLen[i-1] + math.sqrt(2))
            else:
                curSegeLen.append(curSegeLen[i-1] + 1)
        segeLength_info.append(curSegeLen)
        segement_info.append(curSege)
    #print segement_info
    WriteAscFile(RillExtDir + os.sep + "BoundCell.asc", BoundRaster,ncols,nrows,geotrans,-9999)
    f = open(UpStreamRouteFile,'w')
    f.write(str(segement_info))
    f.close()
    f = open(UpStreamRouteLenFile,'w')
    f.write(str(segeLength_info))
    f.close()
    
    arcpy.gp.overwriteOutput = 1
    for grids in segement_info:
        for grid in grids:
            row = grid[0]
            col = grid[1]
            grid[0] = geotrans[0] + ( col + 0.5 ) * geotrans[1]
            grid[1] = geotrans[3] - ( row + 0.5 ) * geotrans[1]
    segements = []
    for segement in segement_info:
        # Create a Polyline object based on the array of points
        # Append to the list of Polyline objects
        segements.append(
            arcpy.Polyline(
                arcpy.Array([arcpy.Point(*coords) for coords in segement])))
    arcpy.CopyFeatures_management(segements, UpStreamShp)


def Shoulderpts(UpStreamRouteFile,UpStreamRouteLenFile,DEMfil,SlopeFile,SOSFile,RillExtDir,ShoulderptsFile,RealrillFile):
    f = open(UpStreamRouteFile,'r')
    segement_info = eval(f.readline())
    f.close()
    f = open(UpStreamRouteLenFile,'r')
    segementLen_info = eval(f.readline())
    f.close()
    
    dem = ReadRaster(DEMfil).data
    slope = ReadRaster(SlopeFile).data
    sos = ReadRaster(SOSFile).data
    nrows,ncols = sos.shape
    nodata = ReadRaster(SOSFile).noDataValue
    geotrans = ReadRaster(SOSFile).geotrans
    
    shoulderpts = numpy.ones((nrows,ncols))
    shoulderpts = shoulderpts * -9999
    RealRill = numpy.ones((nrows,ncols))
    RealRill = RealRill * -9999
    
    RouteSOS = []
    RouteElev = []
    RouteSlp = []
    for grids in segement_info:
        curRouteElev = []
        curRouteSlp = []
        curRouteSOS = []
        for grid in grids:
            ci,cj = grid
            curRouteElev.append(dem[ci][cj])
            curRouteSlp.append(slope[ci][cj])
            curRouteSOS.append(sos[ci][cj])
        if len(curRouteElev) >= 2 and max(curRouteElev) - min(curRouteElev) >= 10:
            MaxSOSIdx = curRouteSOS.index(max(curRouteSOS))
            tempSOS = copy.copy(curRouteSOS)
            tempSOS.sort()
            SecSOSIdx = curRouteSOS.index(tempSOS[len(tempSOS)-2])
            if len(curRouteElev) > 3:
                if MaxSOSIdx in range(len(curRouteElev)-3,len(curRouteElev)):
                    MaxSOSIdx = curRouteSOS.index(tempSOS[len(tempSOS)-3])
                    SecSOSIdx = curRouteSOS.index(tempSOS[len(tempSOS)-2])
                    
            lowerMaxSOS = curRouteSOS[MaxSOSIdx] * 0.85 #- 0.05 * (max(curRouteSOS) - min(curRouteSOS))
            MaxSlpIdx = curRouteSlp.index(max(curRouteSlp))
            EdgeIdx = 9999
            if MaxSlpIdx >= min(MaxSOSIdx,SecSOSIdx) and MaxSlpIdx <= max(MaxSOSIdx,SecSOSIdx):
                for i in range(min(MaxSOSIdx,SecSOSIdx)+1): #,max(MaxSOSIdx,SecSOSIdx)):
                    if curRouteSlp[i] >= 20:
                        EdgeIdx = i
                        break
            for i in range(len(grids)):
                if curRouteSOS[i] >= lowerMaxSOS and curRouteSlp[i] >= 20:
                    if EdgeIdx != 9999:
                        EdgeIdx = min(EdgeIdx, i)
                        break
                    else:
                        EdgeIdx = i
                        break
            if EdgeIdx != 9999:
                crow,ccol = grids[EdgeIdx]
                shoulderpts[crow][ccol] = 1
                Srow,Scol = grids[len(grids)-1]
                RealRill[Srow][Scol] = 1

                    
#            RouteElev.append(curRouteElev)
#            RouteSlp.append(curRouteSlp)
#            RouteSOS.append(curRouteSOS)
            
#    SOSRoute = RillExtDir + os.sep + "RouteSOS.txt"
#    SlpRoute = RillExtDir + os.sep + "RouteSlp.txt"
#    ElevRoute = RillExtDir + os.sep + "RouteElev.txt"
#    f = open(SOSRoute,'w')
#    for sos in RouteSOS:
#        f.write(str(sos))
#    f.close()
#    f = open(SlpRoute,'w')
#    for slp in RouteSlp:
#        f.write(str(slp))
#    f.close()
#    f = open(ElevRoute,'w')
#    for elev in RouteElev:
#        f.write(str(elev))
#    f.close()
    
    
    WriteAscFile(RealrillFile, RealRill,ncols,nrows,geotrans,-9999)
    WriteAscFile(ShoulderptsFile, shoulderpts,ncols,nrows,geotrans,-9999)
    
def RelinkRealRill(RealrillFile1,RealrillFile2,StreamFile,FlowDirFile,RealRillFinal):
    rill1 = ReadRaster(RealrillFile1).data
    rill2 = ReadRaster(RealrillFile2).data
    stream = ReadRaster(StreamFile).data
    flowdir = ReadRaster(FlowDirFile).data
    nrows,ncols = stream.shape
    nodata = ReadRaster(StreamFile).noDataValue
    geotrans = ReadRaster(StreamFile).geotrans
    tempRill = numpy.ones((nrows,ncols))
    tempRill = tempRill * -9999
    for i in range(1,nrows - 1):
        for j in range(1,ncols - 1):
            if rill1[i][j] == 1 or rill2[i][j] == 1:
                tempRill[i][j] = 1
    RemoveLessPtsMtx(tempRill,-9999,2)
    RealRill = numpy.copy(tempRill)
    for i in range(1,nrows - 1):
        for j in range(1,ncols - 1):
            if tempRill[i][j] == 1:
                count = 0
                while count <= 5:
                    crow, ccol = downstream_index(flowdir[i][j],i,j)
                    if not (crow < 1 or crow >= nrows - 2 or ccol < 1 or ccol >= ncols - 2):
                        if tempRill[crow][ccol] != 1:
                            RealRill[crow][ccol] = 1
                            i,j = crow,ccol
                            count = count + 1
                        else:
                            break
                    else:
                        break
    WriteAscFile(RealRillFinal, RealRill,ncols,nrows,geotrans,-9999)