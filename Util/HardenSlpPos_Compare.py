#! /usr/bin/env python
#coding=utf-8

from Util import *

def Comparison(baseF, compF, valueF, equalF, gdalType=gdal.GDT_Int16):
    baseR = ReadRaster(baseF)
    compR = ReadRaster(compF)
    valueR = ReadRaster(valueF)
    baseD = baseR.data
    compD = compR.data
    valueD = valueR.data
    temp = baseD == compD
    equalData = numpy.where(temp, baseD, baseR.noDataValue)
    ## grid in which compF is coincident with baseF
    #WriteGTiffFile(equalF, baseR.nRows, baseR.nCols, equalData, baseR.geotrans, baseR.srs, baseR.noDataValue, gdalType)
    countStatDict = {'RDG':[0,0,0,0,0],'SHD':[0,0,0,0,0],'BKS':[0,0,0,0,0],'FTS':[0,0,0,0,0],'VLY':[0,0,0,0,0]}
    maxSimiDict = {'RDG':[[],[],[],[],[]],'SHD':[[],[],[],[],[]],'BKS':[[],[],[],[],[]],'FTS':[[],[],[],[],[]],'VLY':[[],[],[],[],[]]}
    meanMaxSimiDict = {'RDG':[0,0,0,0,0],'SHD':[0,0,0,0,0],'BKS':[0,0,0,0,0],'FTS':[0,0,0,0,0],'VLY':[0,0,0,0,0]}
    maxMaxSimiDict = {'RDG':[0,0,0,0,0],'SHD':[0,0,0,0,0],'BKS':[0,0,0,0,0],'FTS':[0,0,0,0,0],'VLY':[0,0,0,0,0]}
    minMaxSimiDict = {'RDG':[0,0,0,0,0],'SHD':[0,0,0,0,0],'BKS':[0,0,0,0,0],'FTS':[0,0,0,0,0],'VLY':[0,0,0,0,0]}
    stdMaxSimiDict = {'RDG':[0,0,0,0,0],'SHD':[0,0,0,0,0],'BKS':[0,0,0,0,0],'FTS':[0,0,0,0,0],'VLY':[0,0,0,0,0]}
    posList = ['RDG', 'SHD', 'BKS', 'FTS', 'VLY']
    idxList = [1, 2, 4, 8, 16]
    # print baseR.noDataValue, compR.noDataValue
    for row in range(0, baseR.nRows):
        for col in range(0, baseR.nCols):
            if baseD[row][col] != baseR.noDataValue and compD[row][col] != compR.noDataValue:
                basePos = posList[idxList.index(baseD[row][col])]
                compPosIdx = idxList.index(compD[row][col])
                countStatDict.get(basePos)[compPosIdx] += 1;
                maxSimiDict.get(basePos)[compPosIdx].append(valueD[row][col])
    ## calculate statistics for maxSimiDict
    for pos in posList:
        for idx in range(0, len(posList)):
            if len(maxSimiDict.get(pos)[idx]) > 0:
                meanMaxSimiDict.get(pos)[idx] = numpy.mean(maxSimiDict.get(pos)[idx])
                maxMaxSimiDict.get(pos)[idx] = numpy.max(maxSimiDict.get(pos)[idx])
                minMaxSimiDict.get(pos)[idx] = numpy.min(maxSimiDict.get(pos)[idx])
                stdMaxSimiDict.get(pos)[idx] = numpy.std(maxSimiDict.get(pos)[idx])

    print countStatDict
    print meanMaxSimiDict
    print maxMaxSimiDict
    print minMaxSimiDict
    print stdMaxSimiDict
def DiffMaxSimi(baseF, compF, valueF, diffF, gdalType=gdal.GDT_Float32):
    baseR = ReadRaster(baseF)
    compR = ReadRaster(compF)
    valueR = ReadRaster(valueF)
    baseD = baseR.data
    compD = compR.data
    valueD = valueR.data
    temp = baseD != compD
    diffData = numpy.where(temp, valueD, valueR.noDataValue)
    WriteGTiffFile(diffF, baseR.nRows, baseR.nCols, diffData, baseR.geotrans, baseR.srs, valueR.noDataValue, gdalType)


if __name__ == '__main__':
    baseRaster = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\harden_qin2009.tif'
    compRaster = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\harden_proposed.tif'
    equalRaster = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\commonSlpPos.tif'

    baseMaxSimi = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\maxS_qin2009.tif'
    compMaxSimi = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\maxS_proposed.tif'
    diffMaxSimi = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\qin_based_maxS_diff.tif'

    Comparison(baseRaster, compRaster, baseMaxSimi, equalRaster)
    #Comparison(compRaster, baseRaster, compMaxSimi, equalRaster)
    #DiffMaxSimi(baseRaster, compRaster, baseMaxSimi, diffMaxSimi)