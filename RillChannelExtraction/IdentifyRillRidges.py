# coding=utf-8
from osgeo import gdal
from osgeo import osr
import numpy
import os
import arcpy
from arcpy import env

##  Const Variables Definition  ##
DIR_ITEMS = {1:(0,1),
             2:(1,1),
             4:(1,0),
             8:(1,-1),
             16:(0,-1),
             32:(-1,-1),
             64:(-1,0),
             128:(-1,1)}
DIR_VALUES = [1,2,4,8,16,32,64,128]
LEFT_DELATA = {2:(1,0),
               8:(0,-1),
               32:(-1,0),
               128:(0,1),
               1:(0,0),
               4:(0,0),
               16:(0,0),
               64:(0,0)}
RIGHT_DELATA = {2:(0,1),
               8:(1,0),
               32:(0,-1),
               128:(-1,0),
               1:(0,0),
               4:(0,0),
               16:(0,0),
               64:(0,0)}

MINI_VALUE = 0.000001
##  End Const Variables Definition  ##

##  Define Utility Functions  ##
class Raster:
    def __init__(self, nRows, nCols, data, noDataValue=None, geotransform=None, srs=None):
        self.nRows = nRows
        self.nCols = nCols
        self.data = data
        self.noDataValue = noDataValue
        self.geotrans = geotransform
        self.srs = srs
        
        self.dx = geotransform[1]
        self.xMin = geotransform[0]
        self.xMax = geotransform[0] + nCols*geotransform[1]
        self.yMax = geotransform[3]
        self.yMin = geotransform[3] + nRows*geotransform[5]

def ReadRaster(rasterFile):
    ds = gdal.Open(rasterFile)
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    xsize = band.XSize
    ysize = band.YSize
    
    noDataValue = band.GetNoDataValue()
    geotrans = ds.GetGeoTransform()
    
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    #print srs.ExportToProj4()
    if noDataValue is None:
        noDataValue = -9999
    return Raster(ysize, xsize, data, noDataValue, geotrans, srs) 

def WriteAscFile(filename, data, xsize, ysize, geotransform, noDataValue):
    header = """NCOLS %d
NROWS %d
XLLCENTER %f
YLLCENTER %f
CELLSIZE %f
NODATA_VALUE %f
""" % (xsize, ysize, geotransform[0] + 0.5*geotransform[1], geotransform[3]-(ysize-0.5)*geotransform[1], geotransform[1], noDataValue)
        
    f = open(filename, 'w')
    f.write(header)
    for i in range(0, ysize):
        for j in range(0, xsize):
            f.write(str(data[i][j]) + "\t")
        f.write("\n")
    f.close() 
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
def downstream_index(DIR_VALUE, i, j):
    drow, dcol = DIR_ITEMS[DIR_VALUE]
    return i+drow, j+dcol
    
def GetRillStartIdx(StreamLinkss,nodata,FlowDir):
    nrows,ncols = StreamLinkss.shape
    countRill = 0
    countmid = 0
    countend = 0
    RillStartIdx = []
    for i in range(nrows):
        for j in range(ncols):
            if (isStreamSegmentCell(StreamLinkss,nodata,i,j,FlowDir) == 1):
                countRill = countRill + 1
                RillStartIdx.append((i,j))
            elif (isStreamSegmentCell(StreamLinkss,nodata,i,j,FlowDir) == 3):
                countend = countend + 1
            elif (isStreamSegmentCell(StreamLinkss,nodata,i,j,FlowDir) == 2):
                countmid = countmid + 1
                
    print "Rill number is : %s,%s,%s" % (countRill,countmid,countend)
    return RillStartIdx

def IdentifyRillRidges(HillslpFile,StreamFile,FlowDirFile,FlowAccFile,WatershedFile,DEMfil,folder):
#    header = "RillID,NodeID,DEM_R,DEM_L,CurvProf_R,CurvProf_L,CurvPlan_R,CurvPlan_L"
#    f = open(ProfileStats, 'w')
#    f.write(header)
#    f.close()
    StreamLinks = ReadRaster(StreamFile).data
    nrows,ncols = StreamLinks.shape
    nodata = ReadRaster(StreamFile).noDataValue
    geotrans = ReadRaster(StreamFile).geotrans
    Hillslp = ReadRaster(HillslpFile).data
    FlowDir = ReadRaster(FlowDirFile).data
    FlowAcc = ReadRaster(FlowAccFile).data
    Watershed = ReadRaster(WatershedFile).data
    #CurvProf = ReadRaster(CurvProfFile).data
    #CurvPlan = ReadRaster(CurvPlanFile).data
    DEM = ReadRaster(DEMfil).data
    RillStartIdx = GetRillStartIdx(StreamLinks,nodata,FlowDir)
    RillProfInfo = []
    RillEdge = numpy.ones((nrows,ncols))
    RillEdge = RillEdge * nodata
    RealRill = numpy.ones((nrows,ncols))
    RealRill = RealRill * nodata
    Accum = []
    AccumAll = []
    for rillIdx in RillStartIdx:
        row = rillIdx[0]
        col = rillIdx[1]
        print row,col
        RillId = StreamLinks[row][col]
        # Begin with the second cell
        row,col = downstream_index(FlowDir[row][col],row,col)
        NodeId = 0
        DEML = []
        DEMR = []
        DEMProf = []        
        while not(row <0 or col <0 or row >= nrows or col >= ncols) and StreamLinks[row][col] == RillId and Watershed[row][col] == RillId:
            DirIdx = DIR_VALUES.index(FlowDir[row][col])
            AccumAll.append(FlowAcc[row][col])
            DirIdxL = (DirIdx - 2) if (DirIdx - 2) >= 0 else DirIdx + 6
            DirIdxR = (DirIdx + 2) if (DirIdx + 2) <= 7 else DirIdx - 6
            deltaL = DIR_ITEMS[DIR_VALUES[DirIdxL]]
            deltaR = DIR_ITEMS[DIR_VALUES[DirIdxR]]
            ModifyL = LEFT_DELATA[DIR_VALUES[DirIdxL]]
            ModifyR = RIGHT_DELATA[DIR_VALUES[DirIdxL]]
            DEML.append(DEM[row][col])
            DEMR.append(DEM[row][col])
            temprowL = row + deltaL[0]
            tempcolL = col + deltaL[1]
            temprowR = row + deltaR[0]
            tempcolR = col + deltaR[1]
#            temprowL = row + deltaL[0] + ModifyL[0]
#            tempcolL = col + deltaL[1] + ModifyL[1]
#            temprowR = row + deltaR[0] + ModifyR[0]
#            tempcolR = col + deltaR[1] + ModifyR[1]
#
            while not(temprowL <0 or tempcolL <0 or temprowL >= nrows or tempcolL >= ncols) and StreamLinks[temprowL][tempcolL] == nodata and Watershed[temprowL][tempcolL] == RillId and Hillslp[temprowL][tempcolL] == 2:
                DEML.append(DEM[temprowL][tempcolL])
                temprowL = temprowL + deltaL[0]
                tempcolL = tempcolL + deltaL[1]
            while not(temprowR <0 or tempcolR <0 or temprowR >= nrows or tempcolR >= ncols) and StreamLinks[temprowR][tempcolR] == nodata and Watershed[temprowR][tempcolR] == RillId and Hillslp[temprowR][tempcolR] == 1:
                DEMR.append(DEM[temprowR][tempcolR])
                temprowR = temprowR + deltaR[0]
                tempcolR = tempcolR + deltaR[1]
            if ((max(DEML) - DEML[0] >= 10) or (max(DEMR) - DEMR[0] >= 10)) and geotrans[1] * (len(DEML) + len(DEMR) - 1) >= 10:
                DEMProf = list(reversed(DEMR)) + DEML[1:]
            if DEMProf != []:
                RillProfInfo.append([RillId,NodeId,DEMProf])
                RealRill[row][col] = RillId
                RillEdge[row][col] = RillId
                RillEdge[temprowR - deltaR[0]][tempcolR - deltaR[1]] = RillId
                RillEdge[temprowL - deltaL[0]][tempcolL - deltaL[1]] = RillId
                Accum.append(FlowAcc[row][col])
 
            row,col = downstream_index(FlowDir[row][col],row,col)
            NodeId = NodeId + 1
            DEML = []
            DEMR = []
            DEMProf = []            
#    for i in RillProfInfo:
#        print i
    Accum.sort()
    AccumAll.sort()
    print Accum
    print AccumAll
    WriteAscFile(folder + os.sep + "RealRill.asc", RealRill,ncols,nrows,geotrans,nodata)
    WriteAscFile(folder + os.sep + "RillEdge.asc", RillEdge,ncols,nrows,geotrans,nodata)

if __name__ == '__main__':
    ## Input params
    
    folder = r'E:\MasterBNU\RillMorphology\test\Extract2'
    DEMfil = folder + os.sep + "DEMfil"
    StreamFile = folder + os.sep + "StreamLinks"
    WatershedFile = folder + os.sep + "watershed"
    FlowDirFile = folder + os.sep + "flowdir"
    FlowAccFile = folder + os.sep + "flowacc"
    #CurvProfFile = folder + os.sep + "curvprof"
    #CurvPlanFile = folder + os.sep + "curvplan"
    HillslpFile = folder + os.sep + "HillSlp.asc"
    #ProfileStats = folder + os.sep + "ProfileStats.txt"
    IdentifyRillRidges(HillslpFile,StreamFile,FlowDirFile,FlowAccFile,WatershedFile,DEMfil,folder)
    
