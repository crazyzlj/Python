#! /usr/bin/env python
#coding=utf-8
from Util import *
from Hillslope import *
from Subbasin import *
import os,sys

def IdentifyRillShoulderPts(Aspect,Slope,ProfC,alpha,beta,ShoulderPts):
    aspect = ReadRaster(Aspect).data
    nrows,ncols = aspect.shape
    nodata = ReadRaster(Aspect).noDataValue
    geotrans = ReadRaster(Aspect).geotrans
    slope = ReadRaster(Slope).data
    profc = ReadRaster(ProfC).data
    ShoulderPtsMtx = numpy.ones((nrows,ncols))
    if nodata != -9999:
        ShoulderPtsMtx = ShoulderPtsMtx * -9999
    else:
        ShoulderPtsMtx = ShoulderPtsMtx * nodata

    for i in range(nrows):
        for j in range(ncols):
            # North
            if (aspect[i][j] >= 0 and aspect[i][j] < 22.5) or (aspect[i][j] >= 337.5 and aspect[i][j] < 360):
                if not(i-1 < 0 or i+1 >= nrows):
                    if (slope[i][j]<slope[i-1][j]) and (slope[i+1][j]<slope[i][j]) and slope[i][j]>alpha and (slope[i-1][j]-slope[i+1][j] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Northeast
            if (aspect[i][j] >= 22.5 and aspect[i][j] < 67.5):
                if not(i-1 < 0 or i+1>nrows or j-1<0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i-1][j+1]) and (slope[i+1][j-1]<slope[i][j]) and slope[i][j]>alpha and (slope[i-1][j+1]-slope[i+1][j-1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # East
            if (aspect[i][j] >= 67.5 and aspect[i][j] < 112.5):
                if not(j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i][j+1]) and (slope[i][j-1]<slope[i][j]) and slope[i][j]>alpha and (slope[i][j+1]-slope[i][j-1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Southeast
            if (aspect[i][j] >= 112.5 and aspect[i][j] < 157.5):
                if not(i-1 < 0 or i+1 >= nrows or j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i+1][j+1]) and (slope[i-1][j-1]<slope[i][j]) and slope[i][j]>alpha and (slope[i+1][j+1]-slope[i-1][j-1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # South
            if (aspect[i][j] >= 157.5 and aspect[i][j] < 202.5):
                if not(i-1 < 0 or i+1 >= nrows):
                    if (slope[i][j]<slope[i+1][j]) and (slope[i-1][j]<slope[i][j]) and slope[i][j]>alpha and (slope[i+1][j]-slope[i-1][j] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Southwest
            if (aspect[i][j] >= 202.5 and aspect[i][j] < 247.5):
                if not(i-1 < 0 or i+1 >= nrows or j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i+1][j-1]) and (slope[i-1][j+1]<slope[i][j]) and slope[i][j]>alpha and (slope[i+1][j-1]-slope[i-1][j+1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # West
            if (aspect[i][j] >= 247.5 and aspect[i][j] < 292.5):
                if not(j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i][j-1]) and (slope[i][j+1]<slope[i][j]) and slope[i][j]>alpha and (slope[i][j-1]-slope[i][j+1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
            # Northwest
            if (aspect[i][j] >= 292.5 and aspect[i][j] < 337.5):
                if not(i-1 < 0 or i+1 >= nrows or j-1 < 0 or j+1 >= ncols):
                    if (slope[i][j]<slope[i-1][j-1]) and (slope[i+1][j+1]<slope[i][j]) and slope[i][j]>alpha and (slope[i-1][j-1]-slope[i+1][j+1] > beta) and profc[i][j]<0:
                        ShoulderPtsMtx[i][j] = 1
                        continue
    WriteAscFile(ShoulderPts, ShoulderPtsMtx,ncols,nrows,geotrans,-9999)
            
def RillShoulderSegement(Boundary,FlowDir,ShoulderPts,ShoulderFile):
    flowdir = ReadRaster(FlowDir).data
    flownodata = ReadRaster(FlowDir).noDataValue
    geotrans = ReadRaster(FlowDir).geotrans
    boundary = ReadRaster(Boundary).data
    shoulderpts = ReadRaster(ShoulderPts).data
    nrows,ncols = flowdir.shape
    nodata = ReadRaster(Boundary).noDataValue
    bndIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if boundary[i][j] != nodata:
                #print i,j
                bndIdx.append((i,j))
    iterate = 0
    changed = 1
    while not(changed == 0 or iterate > 150):
        print "iterate time:%s, changed num:%s, boundary num:%s" % (iterate,changed,len(bndIdx))
        changed = 0
        tempbndIdx = []
        for bnd in bndIdx:
            if shoulderpts[bnd[0]][bnd[1]] == 1:
                tempbndIdx.append((bnd[0],bnd[1]))
            else:
                row,col = downstream_index(flowdir[bnd[0]][bnd[1]], bnd[0],bnd[1])
                if row < 0 or row >= nrows or col < 0 or col >= ncols:
                    tempbndIdx.append((bnd[0],bnd[1]))
                else:
                    tempbndIdx.append((row,col))
                    changed = changed + 1
        tempbndIdx = list(set(tempbndIdx))
        bndIdx = tempbndIdx
        iterate = iterate + 1
    shoulder = numpy.ones((nrows,ncols))
    shoulder = shoulder * nodata
    for sd in bndIdx:
        shoulder[sd[0]][sd[1]] = 1
    WriteAscFile(ShoulderFile, shoulder,ncols,nrows,geotrans,nodata)

def RillShoulder(BasinFile,FlowDir,ShoulderPts,tempDir,ShoulderFile):
    UniqueBasinId = GetUniqueValues(BasinFile)
    print UniqueBasinId
    for BsnID in UniqueBasinId:
        tempBsnID = []
        tempBsnID.append(BsnID)
        BsnASC = tempDir + os.sep + "BsnID" + str(BsnID) + ".asc"
        ExtractBasinBoundary(BasinFile,tempBsnID,BsnASC)
        ShldASC = tempDir + os.sep + "Shld" + str(BsnID) + ".asc"
        RillShoulderSegement(BsnASC,FlowDir,ShoulderPts,ShldASC)
def Rectangle(row,col,side):
    GridIdxs = []
    if side/2 >= 1:
        for crow in range(row - side/2, row + side/2 + 1):
            for ccol in range(col - side/2, col + side/2 + 1):
                GridIdxs.append([crow,ccol])
    else:
        GridIdxs.append([row,col])
    return GridIdxs

def SnakeICC(RealrillFile1Final,side,BndPtsIdxFile,BndCellFile,SnakeICCFile):
    bndcells = ReadRaster(BndCellFile).data
    rillcells = ReadRaster(RealrillFile1Final).data
    nrows,ncols = bndcells.shape
    nodata = ReadRaster(BndCellFile).noDataValue
    geotrans = ReadRaster(BndCellFile).geotrans
    
    snakeicc = numpy.ones((nrows,ncols))
    snakeicc = snakeicc * -9999
#    for line in open(BndPtsIdxFile):
#        bnds = eval(line)
#        uniBnd = bnds[0]
#        for bnd in bnds:
#            if bnd[0] <= uniBnd[0] and bnd[1] <= uniBnd[1]:
#                uniBnd = bnd                
#        snakeicc[uniBnd[0]][uniBnd[1]] = 1
    for i in range(nrows):
        for j in range(ncols):
            if rillcells[i][j] != nodata:
                Idxs = Rectangle(i,j,side)
                for idx in Idxs:
                    crow,ccol = idx
                    if not(crow < 0 or crow >= nrows or ccol < 0 or ccol >= ncols ):
                        snakeicc[crow][ccol] = 1
    snakeicc = ExtractBoundary(snakeicc,nodata)
    WriteAscFile(SnakeICCFile, snakeicc,ncols,nrows,geotrans,-9999) 
