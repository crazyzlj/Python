from Util import *
def valuesByCell(baseF, compF):
    baseR = ReadRaster(baseF)
    compR = ReadRaster(compF)
    baseD = baseR.data
    compD = compR.data
    rows = baseR.nRows
    cols = baseR.nCols
    baseL = []
    compL = []
    for row in range(rows):
        for col in range(cols):
            baseV = baseD[row][col]
            compV = compD[row][col]
            if baseV != baseR.noDataValue or compV != compR.noDataValue:
                if baseV > ZERO and compV > ZERO:
                    baseL.append(baseV)
                    compL.append(compV)
    return (baseL, compL)

if __name__ == '__main__':
    FileName = 'VlyInf.tif'
    baseF = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareWithQin2009\basedOriginRPI\withoutElev\FuzzySlpPos\%s' % FileName
    compF = r'E:\data_m\AutoFuzSlpPos\C&G_zhu_2016\CompareWithQin2009\Qin_2009_version2\FuzzySlpPos\%s' % FileName
    baseL, compL = valuesByCell(baseF, compF)
    print baseL
    print compL
