###ExtractMultiValuesToPoints
###Output: Point shapefile with one single year's precipitation data
###In all, 25 files will be created and also 25 csv files will be generated.
###Author: Zhu Liangjun
###Date:2012/12/14
import os,sys,arcpy,string
from arcpy.sa import *
from arcpy import env
arcpy.gp.overwriteOutput = 1

os.chdir(r'd:\test')
sourcePoint = "point.shp"
for dirs in os.listdir("."):
    if os.path.isdir(dirs):
        print dirs
        arcpy.Copy_management(sourcePoint,dirs+"\\"+str(dirs)+".shp")
        env.workspace = dirs
        inPointFeatures = dirs+"\\"+str(dirs)+".shp"
        inRasterList = []
        for rasterFile in arcpy.ListRasters("*","GRID"):
            inRasterList.append([dirs+"\\"+str(rasterFile),str(rasterFile)])
        print inRasterList
        try:
            arcpy.CheckOutExtension("Spatial")
            ExtractMultiValuesToPoints(inPointFeatures, inRasterList, "NONE")
            fields = arcpy.gp.listFields(inPointFeatures)
            fieldList = []
            for field in fields:
                #print field.name
                fieldList.append(str(field.name))
            print fieldList
            arcpy.ExportXYv_stats(inPointFeatures,fieldList,"COMMA",dirs+"\\"+str(dirs)+".csv","ADD_FIELD_NAMES")
        except:
            print arcpy.gp.GetMessages()
cmd = 'mkdir "csv"\\'
os.system(cmd)
os.chdir(r'd:\test')
for resultDir in os.listdir("."):
    if os.path.isdir(resultDir):
        print resultDir
        for refile in os.listdir(resultDir):
            if (os.path.splitext(refile)[1][1:].lower()=='csv'):
                print refile
                cmd='move "'+resultDir+'\\'+refile+'" "csv\\"'
                print cmd
                os.system(cmd)