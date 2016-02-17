## Author: Liangjun Zhu
## Created on: 2014-11-9
## Version: 1.0
## Description: Normalize the input raster dataset to 0~100 or -50~50.
## Specifically, zero should be zero after normalizing.
import arcpy
from arcpy import env
env.workspace = r'E:\Anhui\PurposeSampling\DataPrepare'
arcpy.gp.overwriteOutput = 1
arcpy.CheckOutExtension("spatial")
inFile = "profc"
outFile = "profc_norm.asc"
temp = "temp"
Max = arcpy.GetRasterProperties_management(inFile,"MAXIMUM")
Min = arcpy.GetRasterProperties_management(inFile,"MINIMUM")
maxValue = float(Max.getOutput(0))
minValue = float(Min.getOutput(0))
value_range = maxValue - minValue
print maxValue,minValue,value_range
#Exec1 = "100.*(\"%s\" - %.10f)/%.10f" % (inFile, minValue, value_range)
Exec2 = "Con(\"%s\">0,\"%s\"*50./%.11f,Con(\"%s\"<0,(\"%s\"-(%.11f))*50./(%.11f),0))" % (inFile, inFile,maxValue, inFile, inFile, minValue, minValue)
#print Exec1
print Exec2
#arcpy.gp.RasterCalculator_sa(Exec1, temp)
arcpy.gp.RasterCalculator_sa(Exec2, temp)
arcpy.RasterToASCII_conversion(temp, outFile)
arcpy.Delete_management(temp)
print "Successful!"
