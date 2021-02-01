# coding=utf-8

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
def Comparison2(baseF, compF, valueF, equalF, gdalType=gdal.GDT_Int16):
    baseR = ReadRaster(baseF)
    compR = ReadRaster(compF)
    baseD = baseR.data
    compD = compR.data
    temp = baseD == compD
    equalData = numpy.where(temp, baseD, baseR.noDataValue)
    ## grid in which compF is coincident with baseF
    WriteGTiffFile(equalF, baseR.nRows, baseR.nCols, equalData, baseR.geotrans, baseR.srs, baseR.noDataValue, gdalType)
    rngNum = len(valueF)
    countList = []
    idxList = []
    countStatDict = {}
    for i in range(rngNum):
        countList.append(0)
        idxList.append(i)
    for i in range(rngNum):
        countStatDict[i] = countList[:]

    for row in range(baseR.nRows):
        for col in range(baseR.nCols):
            if baseD[row][col] != baseR.noDataValue and compD[row][col] != compR.noDataValue:
                baseV = baseD[row][col]
                compV = compD[row][col]
                countStatDict.get(int(baseV))[int(compV)] += 1
    print countStatDict

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
def reClassify(baseF, destF,subValues,  gdalType=gdal.GDT_Float32):
    baseR = ReadRaster(baseF)
    baseD = baseR.data
    rows = baseR.nRows
    cols = baseR.nCols
    destD = baseD
    for row in range(rows):
        for col in range(cols):
            baseV = baseD[row][col]
            if baseV != baseR.noDataValue:
                for rng in subValues:
                    if rng[1] == 1:
                        if baseV >= rng[0] and baseV <= rng[1]:
                            destD[row][col] = subValues.index(rng)
                    else:
                        if baseV >= rng[0] and baseV < rng[1]:
                            destD[row][col] = subValues.index(rng)
    WriteGTiffFile(destF, baseR.nRows, baseR.nCols, destD, baseR.geotrans, baseR.srs, baseR.noDataValue, gdalType)


if __name__ == '__main__':
    # baseRaster = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\harden_qin2009.tif'
    # compRaster = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\harden_proposed.tif'
    # equalRaster = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\commonSlpPos.tif'
    #
    # baseMaxSimi = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\maxS_qin2009.tif'
    # compMaxSimi = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\maxS_proposed.tif'
    # diffMaxSimi = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareData\qin_based_maxS_diff.tif'

    #Comparison(baseRaster, compRaster, baseMaxSimi, equalRaster)
    #Comparison(compRaster, baseRaster, compMaxSimi, equalRaster)
    #DiffMaxSimi(baseRaster, compRaster, baseMaxSimi, diffMaxSimi)

    FileName = ['RdgInf.tif','ShdInf.tif','BksInf.tif','FtsInf.tif','VlyInf.tif']
    for filename in FileName:
        compF = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareWithQin2009\basedOriginRPI\FuzzySlpPos\%s' % filename
        baseF = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareWithQin2009\Qin_2009_version2\FuzzySlpPos\%s' % filename
        workspace = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareWithQin2009\comparison\qin_as_base'
        subSection = [[0.8,1],[0.6,0.8],[0.4,0.6],[0.2,0.4],[0,0.2]]
        ##             0         1         2          3        4
        baseDestF = workspace + '\\base_' + filename
        reClassify(baseF, baseDestF, subSection)
        compDestF = workspace + '\\comp_' + filename
        reClassify(compF, compDestF, subSection)
        equalF = workspace + '\\equal_' + filename
        Comparison2(baseDestF, compDestF, subSection, equalF)

