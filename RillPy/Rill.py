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
    #print Accum
    #print AccumAll
    WriteAscFile(folder + os.sep + "RealRill.asc", RealRill,ncols,nrows,geotrans,-9999)
    WriteAscFile(folder + os.sep + "RillEdge.asc", RillEdge,ncols,nrows,geotrans,-9999)
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
                
def UpStreamRoute(WatershedFile,HillslpFile,StreamFile,FlowDirFile,RillExtDir):
    stream = ReadRaster(StreamFile).data
    nrows,ncols = stream.shape
    nodata = ReadRaster(StreamFile).noDataValue
    geotrans = ReadRaster(StreamFile).geotrans
    hillslp = ReadRaster(HillslpFile).data
    flowdir = ReadRaster(FlowDirFile).data
    watershed = ReadRaster(WatershedFile).data

    UpStream = numpy.ones((nrows,ncols))
    UpStream = UpStream * -9999
    UpStreamShp = RillExtDir + os.sep + "UpStream.shp"
    
    segement_info = []
    # A list that will hold each of the Polyline objects
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
    for cell in boundCells:
        BoundRaster[cell[0]][cell[1]] = 1
    WriteAscFile(RillExtDir + os.sep + "BoundCell.asc", BoundRaster,ncols,nrows,geotrans,-9999)
#        tempSegements = []
#        cRow,cCol = pt
#        tempSegement = [[cRow,cCol]]
#        for di in [-1,0,1]:
#            for dj in [-1,0,1]:
#                ci = cRow + di
#                cj = cCol + dj
#                if ci < 0 or cj < 0 or ci >= nrows or cj >= ncols:
#                    continue
#                if downstream_index(flowdir[ci][cj],ci,cj)==(cRow,cCol) and stream[ci][cj] == nodata:
#                    curSege = tempSegement
#                    curSege.append([ci,cj])
#                    SingleUpStream(curSege,ci,cj,flowdir,stream,hillslp,watershed,hillslp[ci][cj],watershed[ci][cj],nodata)
#                    tempSegements.append(curSege)
#                    break
#        segement_info.extend(tempSegements)
#    print segement_info
#    for grids in segement_info:
#        for grid in grids:
#            row = grid[0]
#            col = grid[1]
#            grid[0] = geotrans[0] + ( col + 0.5 ) * geotrans[1]
#            grid[1] = geotrans[3] - ( row - 0.5 ) * geotrans[1]
#    segements = []
#    for segement in segement_info:
#        # Create a Polyline object based on the array of points
#        # Append to the list of Polyline objects
#        segements.append(
#            arcpy.Polyline(
#                arcpy.Array([arcpy.Point(*coords) for coords in segement])))
#    arcpy.CopyFeatures_management(segements, UpStreamShp)