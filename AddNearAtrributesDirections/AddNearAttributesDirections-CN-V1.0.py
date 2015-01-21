import arcpy
from arcpy import env

# ---------------------------------------------------------------------------
# AddNearAttributesDirections.py
# Created on: 2013-04-08
# Author: Zhu Liangjun
# ---------------------------------------------------------------------------


#################### Inputs ########################
def setupNearAttributes():
    poly_shp = arcpy.GetParameterAsText(0)
    nameField = arcpy.GetParameterAsText(1)
    fieldName = arcpy.GetParameterAsText(2)
    fieldLength = arcpy.GetParameterAsText(3)
    isDirection = arcpy.GetParameterAsText(4)
    Direct = arcpy.GetParameterAsText(5)
    outFile = arcpy.GetParameterAsText(6)
    arcpy.gp.overwriteOutput = 1
    shpDesc = arcpy.Describe(poly_shp)
    env.workspace = shpDesc.Path
    if isDirection:
        AddNearAttributesDirec(poly_shp,nameField,Direct,outFile,fieldName,fieldLength)
    else:
        AddNearAttributes(poly_shp,nameField,outFile,fieldName,fieldLength)

################### Functions ######################
def sendmsg(msg):
    print msg
    arcpy.AddMessage(msg)

def CalFieldMappings(origial_shp,join_shp,nameField,fieldmappings,fieldName,Length):
    fieldmappings.addTable(origial_shp)
    AddNearPoly = arcpy.FieldMap()
    AddNearPoly.addInputField(join_shp,nameField)
    field = AddNearPoly.outputField
    field.name = fieldName
    field.aliasName = fieldName
    field.length = Length
    AddNearPoly.mergeRule = "Join"
    AddNearPoly.joinDelimiter = ","
    AddNearPoly.outputField = field
    fieldmappings.addFieldMap(AddNearPoly)
    ##sendmsg(fieldmappings.exportToString())
    
def AddNearAttributes(poly_shp,nameField,outFile,fieldName,fieldLength):
    arcpy.Copy_management(poly_shp,"temp_poly.shp")
    fieldmappings = arcpy.FieldMappings()
    CalFieldMappings(poly_shp,"temp_poly.shp",nameField,fieldmappings,fieldName,fieldLength)
    arcpy.SpatialJoin_analysis(poly_shp,"temp_poly.shp",outFile,"JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings,"INTERSECT", "", "")
    arcpy.DeleteField_management(outFile,["Join_Count","TARGET_FID"])
    arcpy.CalculateField_management(outFile,fieldName,"Replace(["+fieldName+"],["+nameField+"]+\",\",\"\")","VB")
    arcpy.CalculateField_management(outFile,fieldName,"Replace(["+fieldName+"],\",\"+["+nameField+"],\"\")","VB")
    arcpy.CalculateField_management(outFile,fieldName,"Replace(["+fieldName+"],["+nameField+"],\"\")","VB")
##    arcpy.CalculateField_management(outFile,"NearPoly","string.replace(!"+fieldName+"!,!"+nameField+"!+',','')","PYTHON")
##    arcpy.CalculateField_management(outFile,"NearPoly","string.replace(!"+fieldName+"!,','+!"+nameField+"!,'')","PYTHON")
##    arcpy.CalculateField_management(outFile,"NearPoly","string.replace(!"+fieldName+"!,!"+nameField+"!,'')","PYTHON")
    arcpy.Delete_management("temp_poly.shp")

def AddNearAttributesDirec(poly_shp,nameField,Direct,outFile,fieldName,fieldLength):
    ##Define temporary files
    polytopoint_shp = "polytopoint.shp"
    pointneartab = "pointneartab"
    polyneartab = "polyneartab.dbf"
    
    try:
        arcpy.FeatureToPoint_management(poly_shp, polytopoint_shp, "INSIDE")
        arcpy.AddXY_management(polytopoint_shp)
    except:
        sendmsg(arcpy.GetMessages())
    try:
        arcpy.GenerateNearTable_analysis(polytopoint_shp, polytopoint_shp, pointneartab, "", "NO_LOCATION", "ANGLE", "ALL", "0")
        arcpy.GenerateNearTable_analysis(poly_shp, poly_shp, "polyneartabTemp","0", "NO_LOCATION", "NO_ANGLE", "ALL", "0")
        shpDesc = arcpy.Describe(poly_shp)
        arcpy.TableToTable_conversion("polyneartabTemp",shpDesc.Path,polyneartab)
    except:
        sendmsg(arcpy.GetMessages())
    try:
        arcpy.AddField_management(polyneartab,"near_link","TEXT")
        arcpy.AddField_management(polyneartab,"NameDirec","TEXT","","",80,"","","","")
        arcpy.AddField_management(polyneartab,"x","DOUBLE")
        arcpy.AddField_management(polyneartab,"y","DOUBLE")
        arcpy.AddField_management(polyneartab,"angle","DOUBLE")
        arcpy.CalculateField_management(polyneartab,"near_link","'{0:0>5}'.format(str(!IN_FID!))+'{0:0>5}'.format(str(!NEAR_FID!))","PYTHON")
        arcpy.AddField_management(pointneartab,"near_link","TEXT")
        arcpy.CalculateField_management(pointneartab,"near_link","'{0:0>5}'.format(str(!IN_FID!))+'{0:0>5}'.format(str(!NEAR_FID!))","PYTHON")
    except:
        sendmsg(arcpy.GetMessages())
    try:
        arcpy.MakeTableView_management(polyneartab, "polyneartab_View")
        arcpy.AddJoin_management("polyneartab_View", "IN_FID", polytopoint_shp, "ORIG_FID", "KEEP_ALL")
        arcpy.CalculateField_management("polyneartab_View","X","!polytopoint.POINT_X!","PYTHON")
        arcpy.CalculateField_management("polyneartab_View","Y","!polytopoint.POINT_Y!","PYTHON")
        arcpy.RemoveJoin_management("polyneartab_View","polytopoint")

        arcpy.AddJoin_management("polyneartab_View","NEAR_FID",polytopoint_shp,"ORIG_FID","KEEP_ALL")
        ##arcpy.CalculateField_management("polyneartab_View","polyneartab:NameDirec","!polytopoint."+nameField+"!","PYTHON")
        arcpy.CalculateField_management("polyneartab_View","NameDirec","[polytopoint."+nameField+"]","VB")
        arcpy.RemoveJoin_management("polyneartab_View","polytopoint")

        arcpy.MakeTableView_management(pointneartab, "pointneartab_View")
        arcpy.AddJoin_management("polyneartab_View","NEAR_LINK","pointneartab_View","NEAR_LINK","KEEP_ALL")
        arcpy.CalculateField_management("polyneartab_View","ANGLE","!pointneartab:NEAR_ANGLE!","PYTHON")

        expression = "DefAngle(float(!angle!),str(!NameDirec!))"
        if Direct == "Four":
            codeblock = """ if Abs ( [angle] ) <= 45 then
                                temp = [NameDirec]+\"（东）\"
                            elseif [angle] > 45 and [angle] <= 135 then
                                temp = [NameDirec]+\"（北）\"
                            elseif Abs ( [angle] ) > 135 then
                                temp = [NameDirec]+\"（西）\"
                            else
                                temp = [NameDirec]+\"（南）\"
                            end if """
        else:
            codeblock = """if Abs([angle])<=22.5 then
                                temp = [NameDirec]+\"（东）\"
                           elseif [angle]>22.5 and [angle]<=67.5 then
                                temp = [NameDirec]+\"（东北）\"
                           elseif [angle]>67.5 and [angle]<=112.5 then
                                temp = [NameDirec]+\"（北）\"
                           elseif [angle]>112.5 and [angle]<=157.5 then
                                temp = [NameDirec]+\"（西北）\"
                           elseif Abs([angle])>157.5 then
                                temp = [NameDirec]+\"（西）\"
                           elseif [angle]>-157.5 and [angle]<=-112.5 then
                                temp = [NameDirec]+\"（西南）\"
                           elseif [angle]>-112.5 and [angle]<=-67.5 then
                                temp = [NameDirec]+\"（南）\"
                           else
                                temp = [NameDirec]+\"（东南）\"
                           end if"""
        arcpy.CalculateField_management(polyneartab,"NameDirec","temp","VB",codeblock)
    except:
        sendmsg(arcpy.GetMessages())
        ## Add XY data
    try:
        spatialRef = arcpy.Describe(poly_shp).spatialReference
        arcpy.MakeXYEventLayer_management(polyneartab,"x","y","tempLayer",spatialRef)
        arcpy.CopyFeatures_management("tempLayer","point.shp")
    except:
        sendmsg(arcpy.GetMessages())
    try:
        ## Spatial Join
        fieldmappings = arcpy.FieldMappings()
        CalFieldMappings(poly_shp,"point.shp","NameDirec",fieldmappings,fieldName,fieldLength)
        arcpy.SpatialJoin_analysis(poly_shp, "point.shp", outFile, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings,"CONTAINS", "", "")
        arcpy.DeleteField_management(outFile,["Join_Count","TARGET_FID"])
    except:
        sendmsg(arcpy.GetMessages())
        
    ## Delete process data
    try:
        arcpy.Delete_management("polyneartabTemp")
        arcpy.Delete_management(pointneartab)
        arcpy.Delete_management(polyneartab)
        arcpy.Delete_management(polytopoint_shp)
        arcpy.Delete_management("point.shp")
    except:
        sendmsg(arcpy.GetMessages())

if __name__ == '__main__':
    setupNearAttributes()
