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
def ExtractRasterByMultiPolygon(shpFile, filedName, originRasterFile, bufferSize, outPath):
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
            rasterFile = outPath + os.sep + name + '.tif'
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
    MultiPolyShp = r'E:\test\poly.shp'
    FieldName = "name" ## Field used to name raster files
    RasterFile = r'F:\5Z43_pit.tif'
    BufferSize = 10    ## By default, every single polygon will buffer a distance of 10*cellsize
    ## output
    outDir = r'E:\test\output'
    ## run
    ExtractRasterByMultiPolygon(MultiPolyShp, FieldName, RasterFile, BufferSize, outDir)