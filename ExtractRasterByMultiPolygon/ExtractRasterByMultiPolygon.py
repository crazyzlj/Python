#! /usr/bin/env python
# coding=utf-8
# Function  :  Extract Raster By Mask of MultPolygon Shapefile.
# Created By:  Liangjun Zhu
# Date      :  1/23/16
# Email     :  zlj@lreis.ac.cn
#
import os
import arcpy
from arcpy import env

def ListFieldValues(fileLayer, fName):
    fields = arcpy.gp.listFields(fileLayer)
    fieldValues = []
    flag = False
    for field in fields:
        if str(field.name) == fName:
            flag = True
    if flag:
        rowCursor = arcpy.SearchCursor(fileLayer)
        for row in rowCursor:
            fieldValues.append(row.getValue(fName))
    return (fieldValues, flag)
def ExtractRasterByMultiPolygon(shpFile, filedName, originRasterFile, bufferSize, suffix, outPath):
    ## Set environment settings
    if not os.path.isdir(outPath):  ## if outPath is not exist, then build it.
        if outPath != "":
            os.mkdir(outPath)
    env.workspace = outPath
    ## Split polygon by fieldName
    polyNames, flag = ListFieldValues(shpFile, filedName)
    if(flag):
        arcpy.gp.overwriteOutput = 1
        ## Get the cellsize of originRasterFile
        cellSizeResult = arcpy.GetRasterProperties_management(originRasterFile, "CELLSIZEX")
        cellSize = cellSizeResult.getOutput(0)
        bufferDistance = float(cellSize) * bufferSize
        arcpy.Split_analysis(shpFile, shpFile, filedName, outPath)
        polyFiles = []
        polyBufferFiles = []
        polyFinalFiles = []
        rasterFiles = []
        for name in polyNames:
            polyFile = outPath + os.sep + name + '.shp'
            polyBufferFile = outPath + os.sep + name + '_buf.shp'
            polyFinalFile = outPath + os.sep + name + '_final.shp'
            if suffix is None:
                rasterFile = outPath + os.sep + name + '.tif'
            else:
                rasterFile = outPath + os.sep + name + suffix + '.tif'
            polyFiles.append(polyFile)
            polyBufferFiles.append(polyBufferFile)
            rasterFiles.append(rasterFile)
            polyFinalFiles.append(polyFinalFile)
            arcpy.Buffer_analysis(polyFile, polyBufferFile, bufferDistance, "OUTSIDE_ONLY")
            arcpy.Merge_management([polyFile, polyBufferFile], polyFinalFile)

        if arcpy.CheckOutExtension("Spatial") == "CheckedOut":
            for i in range(0,len(polyBufferFiles)):
                tempRaster = arcpy.sa.ExtractByMask(originRasterFile, polyFinalFiles[i])
                tempRaster.save(rasterFiles[i])
    else:
        print "The %s is not exist in %s" % (filedName, shpFile)
        return None

if __name__ == '__main__':
    ## input
    MultiPolyShp = r'D:\data\GLake\basins.shp'
    FieldName = "Code" ## Field used to name raster files
    RasterFile = r'D:\data\GLake\glake_id.tif'
    #RasterFile = r'D:\data\GLake\srtm_tp.tif'
    BufferSize = 20    ## By default, every single polygon will buffer a distance of 10*cellsize
    suffix = "_ID"     ## If no suffix, set as None
    ## output
    outDir = r'D:\data\GLake\GLoutput'
    ## run
    ExtractRasterByMultiPolygon(MultiPolyShp, FieldName, RasterFile, BufferSize, suffix, outDir)
