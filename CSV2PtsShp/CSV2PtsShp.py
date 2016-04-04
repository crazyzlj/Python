#! /usr/bin/env python
#coding=utf-8
## Author : Liangjun Zhu
## Email : crazyzlj@gmail.com
## Date : 2015-1-23
## Usage : Convert a .csv filetype points file to a vector shapefile
##         put this .py file in the same folder, input the file name and 
##         x,y column name.
import os,sys
import arcpy
from arcpy import env

def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def CSV2PtsShp(CSVFile,X,Y):
    env.workspace = os.path.dirname(CSVFile)
    PtsShp = os.path.basename(CSVFile)
    PtsShp = PtsShp.split('.')[-2] + ".shp"
    print PtsShp
    try:
        arcpy.MakeXYEventLayer_management(CSVFile,X,Y,"tempLayer","","")
        arcpy.CopyFeatures_management("tempLayer",PtsShp)
    except:
        print arcpy.GetMessages()
        arcpy.AddMessage(arcpy.GetMessages())
    
    print os.path.dirname(CSVFile)
    print "%s Convert to Shp Done!" % CSVFile

if __name__ == '__main__':
    CSVName = "designed_samples.csv"
    XName = "RecommendedX"
    YName = "RecommendedY"
    currFolder = currentPath()
    CSVFile = currFolder + os.sep + CSVName
    CSV2PtsShp(CSVFile,XName,YName)
    