# Script Name: MoveOuletsToStreams
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/22/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def MoveOutletsToStreams(inlyr,inlyr1,inlyr2,maxdistance,inputProc,om):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    p=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput D8 Flow Direction Grid: "+p)
    print "Input D8 Flow Direction Grid: "+p
    coord_sys = desc.spatialReference
    #arcpy.AddMessage("Spatial Reference: "+str(coord_sys.name))
    print "Spatial Reference: "+str(coord_sys.name)

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    src=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Stream Raster Grid: "+src)
    print "Input Stream Raster Grid: "+src

    #inlyr2 = arcpy.GetParameterAsText(2)
    desc = arcpy.Describe(inlyr2)
    shfl=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Outlets Shapefile: "+shfl)
    print "Input Outlets Shapefile: "+shfl

    #maxdistance=arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nMinimum Threshold Value: "+maxdistance)
    print "Minimum Threshold Value: "+str(maxdistance)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(4)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Output
    #om = arcpy.GetParameterAsText(5)
    #arcpy.AddMessage("\nOutput Outlet Shapefile: "+om)
    print "Output Outlet Shapefile: "+om

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' MoveOutletsToStreams -p ' + '"' + p + '"' + ' -src ' + '"' + src + '"' + ' -o ' + '"' + shfl + '"' + ' -om ' + '"' + om + '"' + ' -md ' + str(maxdistance)

    #arcpy.AddMessage("\nCommand Line: "+cmd)
    print "Command Line: "+cmd

    # Submit command to operating system
    os.system(cmd)

    # Capture the contents of shell command and print it to the arcgis dialog box
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #arcpy.AddMessage('\nProcess started:\n')
    print "Process started:"
    for line in process.stdout.readlines():
        print line
        #arcpy.AddMessage(line)

    arcpy.DefineProjection_management(om, coord_sys)
