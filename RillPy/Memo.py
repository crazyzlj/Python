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


lists = [[[55, 62], [56, 62], [57, 62], [58, 62], [59, 63], [60, 64]], [[58, 63], [59, 64], [60, 64]], [[57, 63], [58, 64], [59, 64], [60, 64]], [[56, 63], [57, 64], [58, 64], [59, 64], [60, 64]], [[51, 59], [52, 60], [53, 61], [54, 62], [55, 63], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]], [[43, 60], [44, 60], [45, 60], [46, 60], [47, 60], [48, 60], [49, 60], [50, 60], [51, 60], [52, 61], [53, 62], [54, 63], [55, 64], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]], [[45, 61], [46, 61], [47, 61], [48, 61], [49, 60], [50, 60], [51, 60], [52, 61], [53, 62], [54, 63], [55, 64], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]], [[37, 60], [38, 60], [39, 61], [40, 61], [41, 61], [42, 61], [43, 61], [44, 61], [45, 62], [46, 62], [47, 62], [48, 61], [49, 60], [50, 60], [51, 60], [52, 61], [53, 62], [54, 63], [55, 64], [56, 64], [57, 64], [58, 64], [59, 64], [60, 64]]]
#print lists
f = open(r'e:\test.txt','w')
for list in lists:
    ##print list
    f.write(str(list))
    f.write('\n')
f.close()
count = 0
for line in open(r'e:\test.txt'):
    count = count + 1
    s = eval(line)
    print len(s)
print count