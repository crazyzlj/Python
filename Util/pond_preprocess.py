from Util import *
from TauDEM import DinfUpDependence
import ogr
import subprocess
from shutil import rmtree
def pond_without_stream(orgF, v1, stream, v2, outF, gdalType=gdal.GDT_Float32):
    orgR = ReadRaster(orgF)
    orgD = orgR.data
    streamR = ReadRaster(stream)
    streamD = streamR.data
    srows = streamR.nRows
    scols = streamR.nCols
    rows = orgR.nRows
    cols = orgR.nCols
    #print streamR.noDataValue
    if srows == rows and scols == cols:
        destD = streamD[:][:]
        for row in range(rows):
            for col in range(cols):
                if streamD[row][col] != streamR.noDataValue and streamD[row][col] != v2 and orgD[row][col] == v1:
                    destD[row][col] = 1
                else:
                    destD[row][col] = streamR.noDataValue
        WriteGTiffFile(outF, rows, cols, destD, streamR.geotrans, streamR.srs, streamR.noDataValue, gdalType)
    else:
        print "raster size unmatched!"
        return
def GDAL_SWAP(inraster, inshape, fieldName):
    ds = ogr.Open(inshape)
    lyr = ds.GetLayer(0)
    lyr.ResetReading()
    ft = lyr.GetNextFeature()
    while ft:
        cur_field_name = ft.GetFieldAsString(fieldName)
        outraster = inraster.replace('.tif', '_%s.tif' % cur_field_name.replace(' ', '_'))
        subprocess.call(['gdalwarp', inraster, outraster, '-cutline', inshape,
                         '-crop_to_cutline', '-cwhere', "'%s'='%s'" % (fieldName, cur_field_name)])
        ft = lyr.GetNextFeature()
    ds = None
def Calculate_PND_FR(rs, subbasinShp, fieldName, tempDir, outCSV):
    ### stats = {subbasinID: [pondNum, pondSrcNum, subbasinNum]...}
    #GDAL_SWAP(pond, subbasinShp, fieldName)
    rmmkdir(tempDir)
    stats = {}
    ds = ogr.Open(subbasinShp)
    lyr = ds.GetLayer(0)
    lyr.ResetReading()
    ft = lyr.GetNextFeature()
    while ft:
        cur_field_name = ft.GetFieldAsString(fieldName)
        counts = []
        for r in rs:
            curFileName = r.split(os.sep)[-1]
            outraster = tempDir + os.sep + curFileName.replace('.tif','_%s.tif' % cur_field_name.replace(' ', '_'))
            subprocess.call(['gdalwarp', r, outraster, '-cutline', subbasinShp,
                             '-crop_to_cutline', '-cwhere', "'%s'='%s'" % (fieldName, cur_field_name), '-dstnodata', '-9999' ])
            counts.append(Counting(outraster))
        stats[cur_field_name] = counts
        ft = lyr.GetNextFeature()
    ds = None
    rmtree(tempDir,True)
    #stats = {'11': [39, 1327, 3025], '10': [5, 7, 2916], '13': [0, 0, 3202], '12': [155, 1528, 3181], '15': [68, 635, 12111], '14': [8, 295, 6426], '1': [43, 2218, 0], '3': [51, 2644, 7412], '2': [124, 1462, 8075], '5': [13, 38, 2580], '4': [0, 0, 5569], '7': [53, 171, 3551], '6': [0, 0, 1227], '9': [187, 2199, 3444], '8': [17, 24, 1056]}
    f = open(outCSV, 'w')
    f.write("subbsnID,pondNum,pondSrcNum,SubbsnNum\n")
    for sub in stats.keys():
        nums = stats[sub]
        catStr = sub + ','
        for num in nums:
            catStr += str(num) + ","
        catStr = catStr[0:len(catStr)-1]
        catStr += "\n"
        f.write(catStr)
    f.close()
    #print stats
if __name__ == '__main__':
    ORG_POND_PATH = r'E:\data\zhongTianShe\pond_preprocess'
    SWAT_PROJ_PATH = r'E:\data_m\QSWAT_projects\Done\basin5_unCali\basin5_unCali'
    DEM_NAME = 'dem_zts'
    PROC_NUM = 4
    MPI_PATH = None
    TauDEM_PATH = None
    UPAREA_THRESHOLD = 0.9

    POND_SRC = ORG_POND_PATH + os.sep + 'pond.tif'
    STREAM_SRC = SWAT_PROJ_PATH + os.sep + 'Source' + os.sep + DEM_NAME + 'src.tif'
    CUR_POND_PROCESS_PATH = SWAT_PROJ_PATH + os.sep + 'pond_preprocess'
    mkdir(CUR_POND_PROCESS_PATH)
    POND_WITHOUT_STREAM = CUR_POND_PROCESS_PATH + os.sep + 'pond_no_stream.tif'
    DINF_DIR = SWAT_PROJ_PATH + os.sep + 'Source' + os.sep + DEM_NAME + 'ang.tif'
    POND_UPAREA = CUR_POND_PROCESS_PATH + os.sep + 'pond_uparea.tif'
    POND_UPAREA_BINARY = CUR_POND_PROCESS_PATH + os.sep + 'pond_uparea_binary.tif'
    SUBBASIN = SWAT_PROJ_PATH + os.sep + 'Source' + os.sep + DEM_NAME + 'w.tif'
    SUBBASIN_SHP = SWAT_PROJ_PATH + os.sep + 'Source' + os.sep + DEM_NAME + 'wshed.shp'
    TEMPDIR = CUR_POND_PROCESS_PATH + os.sep + 'temp'
    PND_FR_CSV = CUR_POND_PROCESS_PATH + os.sep + 'pond_original.csv'
    ### begin to preprocessing pond related data
    ### 1. Eliminate stream grid which located in pond
    pond_without_stream(POND_SRC, 18, STREAM_SRC, 1, POND_WITHOUT_STREAM)
    ### 2. Invoke TauDEM function DinfUpDependence to calculate upstream sources
    DinfUpDependence(DINF_DIR, POND_WITHOUT_STREAM, POND_UPAREA, PROC_NUM, MPI_PATH, TauDEM_PATH)
    ### 3. Reclassify the POND_UPAREA according to a threshold, 0.9 by default
    Binarization(POND_UPAREA, POND_UPAREA_BINARY, UPAREA_THRESHOLD)
    ### 4. Calculate pond area, pond contributing area, and subbasin area
    Calculate_PND_FR([POND_WITHOUT_STREAM, POND_UPAREA_BINARY, SUBBASIN], SUBBASIN_SHP, 'subbasin', TEMPDIR, PND_FR_CSV)




