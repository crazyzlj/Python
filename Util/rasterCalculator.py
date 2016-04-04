from Util import *
def changeValue(orgF, newF, oldValue, newValue, gdalType=gdal.GDT_Float32):
    orgR = ReadRaster(orgF)
    orgData = orgR.data
    cols = orgR.nCols
    rows = orgR.nRows
    #print orgR.noDataValue
    for col in range(cols):
        for row in range(rows):
            curValue = orgData[row][col]
            if curValue in oldValue:
                idx = oldValue.index(curValue)
                orgData[row][col] = newValue[idx]
            if curValue == orgR.noDataValue:
                orgData[row][col] = -9999
    WriteGTiffFile(newF, orgR.nRows, orgR.nCols, orgData, orgR.geotrans, orgR.srs, -9999, gdalType)
def mode(vlist):
    if len(vlist) == 0:
        return None
    else:
        count_dict = {}
        for i in vlist:
            if count_dict.has_key(i):
                count_dict[i] += 1
            else:
                count_dict[i] = 1
        max_appear = 0
        for v in count_dict.values():
            if v > max_appear:
                max_appear = v
        if max_appear == 1:
            return None
        mode_list = []
        for k,v in count_dict.items():
            if v == max_appear:
                mode_list.append(k)
        return  mode_list
def eliminateNoData(orgF, eliValue, newF, gdalType = gdal.GDT_Float32):
    orgR = ReadRaster(orgF)
    orgData = orgR.data
    cols = orgR.nCols
    rows = orgR.nRows
    #print orgR.noDataValue
    count = 9999
    iter = 0
    while count > 0:
        count = 0
        for col in range(cols):
            for row in range(rows):
                if orgData[row][col] == eliValue:
                    count += 1
                    nbrValues = []
                    for dr in drow:
                        for dc in dcol:
                            if row+dr < rows and col+dc < cols and orgData[row+dr][col+dc] != orgR.noDataValue and orgData[row+dr][col+dc] != eliValue:
                                nbrValues.append(orgData[row+dr][col+dc])
                    modeValues = mode(nbrValues)
                    if len(nbrValues) == 1 or modeValues is None:
                        orgData[row][col] = nbrValues[0]
                    else:
                        orgData[row][col] = modeValues[0]
        iter += 1
        print "iterator number is: %d, total %d has been eliminated" % (iter, count)
    WriteGTiffFile(newF, orgR.nRows, orgR.nCols, orgData, orgR.geotrans, orgR.srs, -9999, gdalType)



if __name__ == '__main__':
    rawRaster = r'E:\data\zhongTianShe\soil_preprocess\soil_liyang_clip.tif'
    calRaster = r'E:\data\zhongTianShe\soil_preprocess\soil_liyang_clip_cal.tif'
    #langxi: [3,4,6,9,15]->[9,10,6,7,53]
    #guangde: [4,5,7,10,13,20,22]->[8,9,10,6,7,53,50]
    #liyang: [3,4,5,6,7,15,18,19,32]->[4,22,19,1,3,23,5,2,7]
    #orgValue = []
    #newValue = []
    #changeValue(rawRaster, calRaster, orgValue, newValue,gdal.GDT_Int16)
    mosaicF = r'E:\data\zhongTianShe\soil_preprocess\mosaic_mask.tif'
    mosaicFNew = r'E:\data\zhongTianShe\soil_preprocess\mosaic_new.tif'
    eliminateNoData(mosaicF, 0, mosaicFNew, gdal.GDT_Int16)