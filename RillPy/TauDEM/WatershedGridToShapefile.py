# Script Name: WatershedGridToShapefile
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def WatershedToShapefile(inlyr,shfl):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    w=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Elevation file: "+w)
    print "Input Elevation file: "+w

    # Output
    #shfl = arcpy.GetParameterAsText(1)
    #arcpy.AddMessage("\nOutput Stream Source file: "+shfl)
    print "Output Stream Source file: "+shfl

    # Convert tiff to shp
    cmd = arcpy.RasterToPolygon_conversion(w, shfl, "NO_SIMPLIFY", "Value")
