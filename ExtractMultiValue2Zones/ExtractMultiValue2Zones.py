"""
Tool Name: MultiValue2Zones
Source Code: MultiValue2Zones.py
Version: v1.0 based on ArcGIS 10.x
Author: Liangjun Zhu
Contact: crazyzlj@gmail.com
Start Date: 2012/12/14
Revised Date : 2015/1/16

This script will statistic the value of given rasters within the
zones of another polygon shapefile and report the results to a
CSV file.
This script can calculate values included "MEAN","MAJORITY",
"MAXIMUM","MEDIAN","MINIMUM","MINORITY","RANGE","STD","SUM",
"VARIETY". Each raster's value will be appended to the origin
shapefile's attribute table and named by the corresponding
raster's name.
"""
################### Imports ########################
import os,sys,arcpy,string
from arcpy.sa import *
from arcpy.management import *
from arcpy import env

#################### Inputs ########################
def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
def setupMultiVal2Poly():
    
	## The default set is: 1. DEM in workspace\\DEM; 2. params layers in workspace\\params; 
	## 3. Reclassify DEM for statistics zones ##
	
    demfolder = currentPath() + "\\DEM"
    paramfolder = currentPath() + "\\params"
    resultfolder = currentPath() + "\\results"
    #print resultfolder
    if not os.path.exists(resultfolder):
        os.mkdir(resultfolder)
    if os.path.exists(demfolder):
        arcpy.env.workspace = demfolder
    else:
        print "Please make a 'DEM' folder which contains the DEM file."
        raw_input()
        exit()
    arcpy.gp.overwriteOutput = 1
    arcpy.CheckOutExtension("Spatial")    
    if arcpy.ListRasters("*","ALL") == []:
        print "Please check the DEM folder to make sure the existence of DEM raster file."
        raw_input()
        exit()  
    else:
        cls = range(0,8100,100)
        classifyIdx = []
        for i in range(len(cls)-1):
            classifyIdx.append([cls[i],cls[i+1],i])
        #classifyIdx.append([7000,8000,len(cls)])
        print "The reclassification of DEM is :"
        print classifyIdx
           
        for DEMfile in arcpy.ListRasters("*","ALL"):
            print "Reclassify the DEM raster..."
            outReclass = Reclassify(DEMfile, "Value",RemapRange(classifyIdx))
            DEMcls = resultfolder + "\\DEMcls"
            outReclass.save(DEMcls)
            DEMclsShp = resultfolder + "\\DEMcls.shp"
            arcpy.RasterToPolygon_conversion(DEMcls, DEMclsShp, "NO_SIMPLIFY","VALUE")
            DEMclsDis = resultfolder + "\\DEMclsDis.shp"
            arcpy.Dissolve_management(DEMclsShp,DEMclsDis,"GRIDCODE","","MULTI_PART","")
            #break

    OriginShp = DEMclsDis
    ZoneField = "GRIDCODE"
    IgnoreNodata = "DATA"
    SummarizeVal = ["MEAN","MAJORITY","MAXIMUM","MEDIAN","MINIMUM","RANGE","STD","SUM","VARIETY"]
    JoinType = ""
    RasterFolder = paramfolder
    outFolder = resultfolder
	## End the default setting ##
	
	## If you want to use this tool in Arctoolbox, the code above should be replaced by below ##
	OriginShp = arcpy.GetParameterAsText(0)
    ZoneField = arcpy.GetParameterAsText(1)
    IgnoreNodata = arcpy.GetParameterAsText(2)
    SummarizeVal = arcpy.GetParameterAsText(3)
    JoinType = arcpy.GetParameterAsText(4)
    RasterFolder = arcpy.GetParameterAsText(5)
    outFolder = arcpy.GetParameterAsText(6)
    outFileName = arcpy.GetParameterAsText(7)
	## End of code for Arctoolbox's input information ##
    arcpy.gp.overwriteOutput = 1
    for SummVal in SummarizeVal:
        print "Calculating the Index of %s..." % SummVal
        MultiVal2Poly(OriginShp,ZoneField,IgnoreNodata,SummVal,JoinType,RasterFolder,outFolder,SummVal)
    print "All mission done sucessfully!"
    
################### Functions ######################

def ListFields(FileLayer):
    fields = arcpy.gp.listFields(FileLayer)
    fieldList = []
    for field in fields:
        fieldList.append([str(field.name),str(field.type)])
    return fieldList
def AddCalDelField(ShpFile,AddName,CalName,FieldDataType):
    arcpy.AddField_management(ShpFile,AddName,FieldDataType)
    arcpy.CalculateField_management(ShpFile,AddName,"!"+CalName+"!","PYTHON")
    arcpy.DeleteField_management(ShpFile,CalName)
def SaveShpAsCSV(ShpFile,OutDir,OutputName):
    fields = arcpy.gp.listFields(ShpFile)
    fieldList2 = []
    for field in fields:
        if field.name != "Shape":
            fieldList2.append(str(field.name))
    #print fieldList2
    try:
        if not os.path.exists(OutDir+"\\"+OutputName+".csv"):
            arcpy.ExportXYv_stats(ShpFile,fieldList2,"COMMA",OutDir+"\\"+OutputName+".csv","ADD_FIELD_NAMES")
        else:
            os.remove(OutDir+"\\"+OutputName+".csv")
            arcpy.ExportXYv_stats(ShpFile,fieldList2,"COMMA",OutDir+"\\"+OutputName+".csv","ADD_FIELD_NAMES")
    except:
        errorStr =  arcpy.gp.GetMessages()
def MultiVal2Poly(OriginShp,ZoneField,IgnoreNodata,SummarizeVal,JoinType,RasterFolder,outFolder,outFileName):
    if outFolder == "":
        outFolder == RasterFolder
    if os.path.exists(RasterFolder):
        arcpy.env.workspace = RasterFolder
    else:
        print "Please make a 'params' folder which contains the parameter files."
        raw_input()
        exit()
    arcpy.Copy_management(OriginShp,"p.shp")
    DropFields = ["ZonSAT_OID","ZonSAT_STU","ZonSAT_ZON","ZonSAT_GRI","ZonSAT_COU","ZonSAT_ARE"]
    if arcpy.ListRasters("*","ALL") == []:
        print "Please check the DEM folder to make sure the existence of DEM raster file."
        raw_input()
        exit()        
    for rasterFile in arcpy.ListRasters("*","ALL"):
        print "    Handing the %s parameter raster " % rasterFile
        zoneShp = "p.shp"
        curFileName = os.path.splitext(rasterFile)[0]
        try:
            arcpy.CheckOutExtension("Spatial")
            ZonSAT = ZonalStatisticsAsTable(zoneShp,ZoneField,rasterFile,"ZonSAT.dbf",IgnoreNodata,SummarizeVal)
            arcpy.MakeFeatureLayer_management(zoneShp,"tempLayer")
            arcpy.AddJoin_management("tempLayer",ZoneField,"ZonSAT.dbf",ZoneField,JoinType)
            arcpy.CopyFeatures_management("tempLayer",curFileName)
            curFileNameShp = curFileName+".shp"
            arcpy.Delete_management("ZonSAT.dbf")
        except:
            arcpy.gp.GetMessages()
        try:
            AddCalDelField(curFileNameShp,curFileName,"ZonSAT_"+SummarizeVal[0:3],"DOUBLE")
            arcpy.DeleteField_management(curFileNameShp,DropFields)
            for field in ListFields(curFileNameShp):
                #print field
                if not(field[0]=="FID" or field[0]=="Shape" or field[0]==curFileName):
                    if field[0][2:] == "GRIDCODE":
                        AddCalDelField(curFileNameShp,field[0][2:],field[0],"INTEGER")
                    else:
                        AddCalDelField(curFileNameShp,field[0][2:],field[0],field[1])
            #print "ZonSAT_"+SummarizeVal[0:3]
            arcpy.Delete_management(zoneShp)
            arcpy.Copy_management(curFileNameShp,"p.shp")
            arcpy.Delete_management(curFileNameShp)
        except:
            arcpy.gp.GetMessages()
    arcpy.Copy_management("p.shp",outFolder+"\\"+outFileName+".shp")
    arcpy.Delete_management("p.shp")
    print "  Saving the Attribute table to CSV file..."
    SaveShpAsCSV(outFolder+"\\"+outFileName+".shp",outFolder,outFileName)

if __name__ == '__main__':
    setupMultiVal2Poly()
    raw_input()
    exit()