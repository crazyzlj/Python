#! /usr/bin/env python
#coding=utf-8
## Functional test!
##UpStreamShp = RillExtDir + os.sep + "UpStream.shp"
##arcpy.CreateFeatureclass_management(RillExtDir, "UpStream.shp", "POLYLINE", "", "DISABLED", "DISABLED", "")
##arcpy.Append_management(["north.shp", "south.shp", "east.shp", "west.shp"], UpStreamShp, "NO_TEST","","")
import math,copy
#Elev = [398.64911,395.37039,389.93884,382.65137,375.08615,368.56583,365.2388,363.12885,362.1973,361.80881]
#Elev = [383.33521,381.29871,377.68607,372.73752,366.91272,361.18701,356.59479,353.28427,349.79819,347.04926,344.62747,343.27286,341.56818,339.35349,335.77808,330.39804,323.68604,317.19299,312.7785,310.86328,310.17453,308.9617,308.42947,308.30804]
#
#Length = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
#k = []
#k2 = []
#for i in range(1,len(Elev)):
#    #print Elev[i]
#    tempk = math.atan((Elev[i]-Elev[i-1])/(Length[i]-Length[i-1]))*180./math.pi
#    if tempk < 0:
#        tempk = 180 + tempk
#    k.append(tempk)
#print k
#for i in range(1,len(k)):
#    tempk2 = math.atan((k[i]-k[i-1])/(Length[i+1]-Length[i]))*180./math.pi
#    if tempk2 < 0:
#        tempk2 = 180 + tempk2
#    k2.append(tempk2)
#print k2
#print len(k2),k2.index(max(k2))
#curRouteSOS = [57.239685,68.406319,60.301327,44.899513,57.68351,61.255352,28.919455,31.739635,47.483128,70.880402,74.572784,70.896515,46.440041]
#curRouteSlp = [6.942997,17.525024,25.871187,29.097631,33.821583,45.065792,52.355793,51.575272,47.721035,38.855087,26.716295,13.982291,6.188683]
#curRouteElev = [405.30917,404.47617,402.88577,400.73474,397.63855,393.18539,386.34515,378.82489,372.15216,366.53317,364.11539,362.88748,362.13895]
#lowerMaxSOS = max(curRouteSOS) * 0.9 #- 0.05 * (max(curRouteSOS) - min(curRouteSOS))
#MaxSlpIdx = curRouteSlp.index(max(curRouteSlp))
#MaxSOSIdx = curRouteSOS.index(max(curRouteSOS))
#temp = copy.copy(curRouteSOS)
#temp.sort()
#SecSOSIdx = curRouteSOS.index(temp[len(temp)-2])
#EdgeIdx = 0
#if MaxSlpIdx >= min(MaxSOSIdx,SecSOSIdx) and MaxSlpIdx <= max(MaxSOSIdx,SecSOSIdx):
#    for i in range(min(MaxSOSIdx,SecSOSIdx)+1): #,max(MaxSOSIdx,SecSOSIdx)):
#        if curRouteSlp[i] >= 20:
#            EdgeIdx = i
#            break
#for i in range(9):
#    if curRouteSOS[i] >= lowerMaxSOS and curRouteSlp[i] >= 20:
#        if EdgeIdx != 0:
#            EdgeIdx = min(EdgeIdx, i)
#        else:
#            EdgeIdx = i
#            print EdgeIdx
#            break

#MaxSOSIdx = curRouteSOS.index(max(curRouteSOS))
#tempSOS = copy.copy(curRouteSOS)
#tempSOS.sort()
#SecSOSIdx = curRouteSOS.index(tempSOS[len(tempSOS)-2])
#if len(curRouteElev) > 3:
#    if MaxSOSIdx in range(len(curRouteElev)-3,len(curRouteElev)):
#        MaxSOSIdx = curRouteSOS.index(tempSOS[len(tempSOS)-3])
#        SecSOSIdx = curRouteSOS.index(tempSOS[len(tempSOS)-2])
#        
#lowerMaxSOS = curRouteSOS[MaxSOSIdx] * 0.9 #- 0.05 * (max(curRouteSOS) - min(curRouteSOS))
#MaxSlpIdx = curRouteSlp.index(max(curRouteSlp))
#EdgeIdx = 9999
#if MaxSlpIdx >= min(MaxSOSIdx,SecSOSIdx) and MaxSlpIdx <= max(MaxSOSIdx,SecSOSIdx):
#    for i in range(min(MaxSOSIdx,SecSOSIdx)+1): #,max(MaxSOSIdx,SecSOSIdx)):
#        if curRouteSlp[i] >= 20:
#            EdgeIdx = i
#            break
#for i in range(11):
#    if curRouteSOS[i] >= lowerMaxSOS and curRouteSlp[i] >= 20:
#        if EdgeIdx != 9999:
#            EdgeIdx = min(EdgeIdx, i)
#            break
#        else:
#            EdgeIdx = i
#            break
#print EdgeIdx


#lists = [[[55, 62], [56, 62], [57, 62], [58, 62], [59, 63], [60, 64]], [[58, 63], [59, 64], [60, 64]], [[57, 63], [58, 64], [59, 64], [60, 64]], [[56, 63], [57, 64], [58, 64], [59, 64], [60, 64]], [[51, 59], [52, 60], [53, 61], [54, 62], [55, 63], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]], [[43, 60], [44, 60], [45, 60], [46, 60], [47, 60], [48, 60], [49, 60], [50, 60], [51, 60], [52, 61], [53, 62], [54, 63], [55, 64], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]], [[45, 61], [46, 61], [47, 61], [48, 61], [49, 60], [50, 60], [51, 60], [52, 61], [53, 62], [54, 63], [55, 64], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]], [[37, 60], [38, 60], [39, 61], [40, 61], [41, 61], [42, 61], [43, 61], [44, 61], [45, 62], [46, 62], [47, 62], [48, 61], [49, 60], [50, 60], [51, 60], [52, 61], [53, 62], [54, 63], [55, 64], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]]]
##print lists
#f = open(r'e:\test.txt','w')
#for list in lists:
#    ##print list
#    f.write(str(list))
#    f.write('\n')
#f.close()
#count = 0
#for line in open(r'e:\test.txt'):
#    count = count + 1
#    s = eval(line)
#    print len(s)
#print count


#    annotation from Rill.Shoulderpts
#    f = open(UpStreamRouteFile,'r')
#    segement_info = eval(f.readline())
#    f.close()
#    f = open(UpStreamRouteLenFile,'r')
#    segementLen_info = eval(f.readline())
#    f.close()
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

def isAdjacent(ptStd,ptEnd):
    flag = 0
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            crow = ptStd[0]+i
            ccol = ptStd[1]+j
            if [crow,ccol] == ptEnd:
                flag = 1
                return True
    if flag == 0:
        return False
def MakePairs(fstpt,interpPt):
    tempseq = copy.copy(interpPt)
    print tempseq
    pairPts = []
    prev = []
    currcell = fstpt
    while len(tempseq) > 0:
        nextcell = []
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                di = currcell[0] + i
                dj = currcell[1] + j
                if [di,dj] != currcell and [di,dj] in tempseq:
                    nextcell.append([di,dj])
        if nextcell != [] and prev != [] and prev in nextcell:
            nextcell.remove(prev)
        if nextcell == [] or nextcell == None:
            if currcell in tempseq:
                tempseq.remove(currcell)
            if prev in tempseq:
                tempseq.remove(prev)
            prev = []
            if len(tempseq) > 0:
                currcell = tempseq[0]
            else:
                break
        elif len(nextcell) >= 1:
            pairPts.append([currcell,nextcell[0]])
            prev = currcell
            currcell = nextcell[0]
    return pairPts

def InterpLine(ptStd,ptEnd):
    Srow,Scol = ptStd
    Erow,Ecol = ptEnd
    Sr = min(Srow,Erow)
    Er = max(Srow,Erow)
    Sc = min(Scol,Ecol)
    Ec = max(Scol,Ecol)
    Idxs = []
    if isAdjacent(ptStd,ptEnd):
        return Idxs
    elif Srow == Erow:
        for i in range(Sc + 1,Ec):
            Idxs.append([Srow,i])
    elif Scol == Ecol:
        for i in range(Sr + 1,Er):
            Idxs.append([i,Scol])
    else:
        for i in range(Sc + 1,Ec):
            #crow = int(round((float(Erow-Srow)/float(Ecol-Scol))*(i - Scol)))
            crow = int(round(float(Erow-Srow)/float(Ecol-Scol)*(i - Scol)+Srow))
            Idxs.append([crow,i])
        for j in range(Sr + 1,Er):
            ccol = int(round(float(Ecol-Scol)/float(Erow-Srow)*(j - Srow) + Scol))
            Idxs.append([j,ccol])
    uniqueIdxs = []
    for idx in Idxs:
        if idx not in uniqueIdxs:
            uniqueIdxs.append(idx)
    uniqueIdxs.sort()
    return uniqueIdxs
idxs = InterpLine([3,3],[3,6])
idxs.append([3,6])
temppair = MakePairs([3,3],idxs)

#idxs = list(set(idxs))
print temppair

#from Util import *
#
#raster = ReadRaster(r'E:\MasterBNU\RillMorphology\20150130\2Rill\SnakeICC1.asc').data
#nrows,ncols = raster.shape
#geotrans = ReadRaster(r'E:\MasterBNU\RillMorphology\20150130\2Rill\SnakeICC1.asc').geotrans
#raster = thin(raster,geotrans,r'E:\MasterBNU\RillMorphology\20150130\0Temp')
#WriteAscFile(r'E:\MasterBNU\RillMorphology\20150130\2Rill\SnakeICC11.asc', raster,ncols,nrows,geotrans,-9999) 