#! /usr/bin/env python
#coding=utf-8
from Util import *
import numpy

##  Functions for Hillslope Delineating  ##
def isFirstStreamCell(StreamRaster, nodata, row, col, flow_dir):
    nrows,ncols = StreamRaster.shape
    if(StreamRaster[row][col] == nodata):
        return False
    else:
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ni = row + di
                nj = col + dj
                if ni < 0 or nj < 0 or ni >= nrows or nj >= ncols or flow_dir[ni][nj] <=0:
                    continue
                if downstream_index(flow_dir[ni][nj], ni, nj) == (row,col) and (StreamRaster[ni][nj] != nodata):
                    return False
        return True
def isStreamSegmentCell(StreamRaster, nodata, row, col, flow_dir):
    ## 1 means First cell, 2 means Finally cell, 3 means middle cells.
    nrows,ncols = StreamRaster.shape
    count = 0
    if StreamRaster[row][col] == nodata:
        return 0
    else:
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ni = row + di
                nj = col + dj
                if ni < 0 or nj < 0 or ni >= nrows or nj >= ncols or flow_dir[ni][nj] <=0:
                    continue
                if downstream_index(flow_dir[ni][nj], ni, nj) == (row,col) and (StreamRaster[ni][nj] == StreamRaster[row][col]):
                    count = count + 1
        if count >= 1:
            idx = downstream_index(flow_dir[row][col], row, col)
            if idx[0] >= nrows or idx[1] >= ncols or idx[0] <0 or idx[1] < 0 or StreamRaster[idx[0]][idx[1]] == nodata:
                return 2
            else:
                return 3
        else:
            return 1
def GetRillStartIdx(StreamLinks,nodata,FlowDir):
    # Get first cell index of each rill
    nrows,ncols = StreamLinks.shape
    countRill = 0
    countmid = 0
    countend = 0
    RillStartIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if (isStreamSegmentCell(StreamLinks,nodata,i,j,FlowDir) == 1):
                countRill = countRill + 1
                RillStartIdx.append((i,j))
            elif (isStreamSegmentCell(StreamLinks,nodata,i,j,FlowDir) == 3):
                countend = countend + 1
            elif (isStreamSegmentCell(StreamLinks,nodata,i,j,FlowDir) == 2):
                countmid = countmid + 1
                
    #print "Rill number is : %s,%s,%s" % (countRill,countmid,countend)
    return RillStartIdx

def fillUpstreamCells(flow_dir,stream,nodata,hillslp,value,row,col):
    nrows,ncols = flow_dir.shape
    for di in [-1,0,1]:
        for dj in [-1,0,1]:
            tempRow = di + row
            tempCol = dj + col
            if tempRow < 0 or tempCol < 0 or tempRow >= nrows or tempCol >= ncols:
                continue
            if downstream_index(flow_dir[tempRow][tempCol],tempRow,tempCol)==(row,col) and stream[tempRow][tempCol] == nodata:
                if hillslp[tempRow][tempCol] != 1:
                    hillslp[tempRow][tempCol] = value
                #print tempRow,tempCol
                fillUpstreamCells(flow_dir,stream,nodata,hillslp,value,tempRow,tempCol)  

def DelineateHillslopes(StreamFile,FlowDirFile,HillslpFile):
    print "Delineating hillslopes by watershed..."
    StreamLinks = ReadRaster(StreamFile).data
    nodata = ReadRaster(StreamFile).noDataValue
    geotrans = ReadRaster(StreamFile).geotrans
    FlowDir = ReadRaster(FlowDirFile).data
    nrows,ncols = StreamLinks.shape
    count = 0
    SourcePtsIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if(isFirstStreamCell(StreamLinks,nodata,i,j,FlowDir)):
                count = count +1
                SourcePtsIdx.append((i,j))
                
    #print "Headwater point:%s" % count
    #test = GetRillStartIdx(StreamLinks,nodata,FlowDir)
    HillslopeMtx = numpy.ones((nrows,ncols))
    if nodata != -9999:
        HillslopeMtx = HillslopeMtx * -9999
    else:
        HillslopeMtx = HillslopeMtx * nodata
    

    for SourcePt in SourcePtsIdx:
        #print SourcePt
        cRow,cCol = SourcePt
        for di in [-1,0,1]:
            for dj in [-1,0,1]:
                ci = cRow + di
                cj = cCol + dj
                if ci < 0 or cj < 0 or ci >= nrows or cj >= ncols:
                    continue
                if downstream_index(FlowDir[ci][cj],ci,cj)==(cRow,cCol):
                    HillslopeMtx[ci][cj] = 0
                    fillUpstreamCells(FlowDir,StreamLinks,nodata,HillslopeMtx,0,ci,cj)          
        previous = SourcePt
        current = downstream_index(FlowDir[cRow][cCol],cRow,cCol)
        
        while not(current[0] < 0 or current[1] < 0 or current[0] >= nrows or current[1] >= ncols):      
            CurRow = current[0]
            CurCol = current[1]
            StreamLinkValue = StreamLinks[CurRow][CurCol]
            DirIdx = DIR_VALUES.index(FlowDir[CurRow][CurCol])
            if DirIdx <= 7:
                Clockwise = range(DirIdx + 1, 8)
            for i in range(DirIdx):
                Clockwise.append(i)
            CounterClock = list(reversed(Clockwise))
            if isStreamSegmentCell(StreamLinks,nodata,CurRow,CurCol,FlowDir) == 1:
                Clockwise = Clockwise[0:4]
                CounterClock = CounterClock[0:4]
            if isStreamSegmentCell(StreamLinks,nodata,CurRow,CurCol,FlowDir) == 2:
                DirIdx = DIR_VALUES.index(FlowDir[previous[0]][previous[1]])
                Clockwise = range(DirIdx + 1, 8)
                for i in range(DirIdx):
                    Clockwise.append(i)
                CounterClock = list(reversed(Clockwise))
                Clockwise = Clockwise[0:4]
                CounterClock = CounterClock[0:4]
            for Dir in Clockwise:
                temprow = CurRow + DIR_ITEMS[DIR_VALUES[Dir]][0]
                tempcol = CurCol + DIR_ITEMS[DIR_VALUES[Dir]][1]
                if temprow < 0 or tempcol < 0 or temprow >= nrows or tempcol >= ncols:
                    continue
                if downstream_index(FlowDir[temprow][tempcol],temprow,tempcol) == (CurRow,CurCol):
                    if StreamLinks[temprow][tempcol] == StreamLinkValue:
                        break
                    elif StreamLinks[temprow][tempcol] != nodata:
                        continue
                    else:
                        HillslopeMtx[temprow][tempcol] = 1
                        fillUpstreamCells(FlowDir,StreamLinks,nodata,HillslopeMtx,1,temprow,tempcol)
            for Dir in CounterClock:
                temprow = CurRow + DIR_ITEMS[DIR_VALUES[Dir]][0]
                tempcol = CurCol + DIR_ITEMS[DIR_VALUES[Dir]][1]
                if temprow < 0 or tempcol < 0 or temprow >= nrows or tempcol >= ncols:
                    continue
                if downstream_index(FlowDir[temprow][tempcol],temprow,tempcol) == (CurRow,CurCol):
                    if StreamLinks[temprow][tempcol] == StreamLinkValue:
                        break
                    elif StreamLinks[temprow][tempcol] != nodata:
                        continue
                    elif HillslopeMtx[temprow][tempcol] != 1:
                        HillslopeMtx[temprow][tempcol] = 2
                        fillUpstreamCells(FlowDir,StreamLinks,nodata,HillslopeMtx,2,temprow,tempcol)
            previous = current
            current = downstream_index(FlowDir[CurRow][CurCol],CurRow,CurCol)
    WriteAscFile(HillslpFile, HillslopeMtx,ncols,nrows,geotrans,-9999)
