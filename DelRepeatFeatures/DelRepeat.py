# -*- coding:utf8 -*-
#-------------------------------------------------------------------------------
# Name:        DelRepeat
# Description: 
#
# Created:     2013-3-29
# Author:      gjl
# Contact:     gjl
#-------------------------------------------------------------------------------
import arcpy

def DelRepeat(inputFeatureClass, outputFeatureClass):
    #copy feature
    fc = outputFeatureClass
    arcpy.CopyFeatures_management(inputFeatureClass, fc)
    
    #unique id
    if len(arcpy.ListFields(fc, "TempId")) <= 0:
        arcpy.AddField_management(fc, "TempId", "LONG")
    if len(arcpy.ListFields(fc, "TempMark")) <= 0:
        arcpy.AddField_management(fc, "TempMark", "STRING")
    num = 1
    cursor = arcpy.UpdateCursor(fc)
    for row in cursor:
        row.TempId = num
        row.TempMark = "N"
        num +=1
        cursor.updateRow(row)
    del row
    del cursor
    
    #find repeat polygon
    repeat = []
    cursor1 = arcpy.SearchCursor(fc)
    for row1 in cursor1:
        if row1.TempMark == "N":
            geom1 = row1.shape
            cursor2 = arcpy.UpdateCursor(fc)
            for row2 in cursor2:
                geom2 = row2.shape
                if geom1.equals(geom2) and (row2.TempId != row1.TempId):
                    row2.TempMark = "Y"
                    repeat.append(row2.TempId)
                    cursor2.updateRow(row2)
            del row2
            del cursor2
    del row1
    del cursor1
    print repeat
    
    #delete repeat polygon
    arcpy.MakeFeatureLayer_management(fc, "layer")
    sql = ""
    for r in repeat:
        if sql == "":
            sql += "\"TempId\" = " + str(r)
        else:
            sql += " OR \"TempId\" = " + str(r)
    print sql
    arcpy.SelectLayerByAttribute_management("layer", "NEW_SELECTION", sql)
    arcpy.DeleteFeatures_management("layer")
    arcpy.DeleteField_management(fc, "TempId")
    arcpy.DeleteField_management(fc, "TempMark")

def main():
    inFC = arcpy.GetParameterAsText(0)
    outFC = arcpy.GetParameterAsText(1)
    DelRepeat(inFC, outFC)

if __name__ == "__main__":
    main()