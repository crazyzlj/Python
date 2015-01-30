#! /usr/bin/env python
#coding=utf-8
from Util import *
from Hillslope import *


def IdentifyRillShoulderPts(Aspect,Slope,ProfC,alpha,beta,ShoulderPts):
    aspect = ReadRaster(Aspect).data
    nrows,ncols = aspect.shape
    nodata = ReadRaster(Aspect).noDataValue
    geotrans = ReadRaster(Aspect).geotrans
    slope = ReadRaster(Slope).data
    profc = ReadRaster(ProfC).data
    ShoulderPtsMtx = numpy.ones((nrows,ncols))
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
    WriteAscFile(ShoulderPts, ShoulderPtsMtx,ncols,nrows,geotrans,nodata)
            
def RillShoulderLine(Boundary,FlowDir,ShoulderPts,Shoulder):
    flowdir = ReadRaster(FlowDir).data
    nodata = ReadRaster(FlowDir).noDataValue
    geotrans = ReadRaster(FlowDir).geotrans
    boundary = ReadRaster(Boundary).data
    shoulderpts = ReadRaster(ShoulderPts).data
    nrows,ncols = flowdir.shape
    bndIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if boundary[i][j] != nodata:
                #print i,j
                bndIdx.append((i,j))
    iterate = 0
    changed = 0
    #while changed > 0 or iterate < 100:
        
    
    