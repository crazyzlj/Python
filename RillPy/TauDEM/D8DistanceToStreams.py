# Script Name: D8DistanceToStreams
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/6/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def D8DistanceToStreams(inlyr,inlyr1,thresh,inputProc,dist):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    p=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput D8 Flow Direction Grid: "+p)
    print "Input D8 Flow Direction Grid: "+p

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    src=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Stream Raster Grid: "+src)
    print "Input Stream Raster Grid: "+src

    #thresh = arcpy.GetParameterAsText(2)
    #arcpy.AddMessage("\nThreshold: "+thresh)
    print "Threshold: "+str(thresh)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Output
    #dist = arcpy.GetParameterAsText(4)
    #arcpy.AddMessage("\nOutput Distance To Streams: "+dist)
    print "Output Distance To Streams: "+dist

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' D8HDistToStrm -p ' + '"' + p + '"' + ' -src ' + '"' + src + '"' + ' -dist ' + '"' + dist + '"' + ' -thresh ' + str(thresh)

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

    # Calculate statistics on the output so that it displays properly
    #arcpy.AddMessage('Executing: Calculate Statistics\n')
    arcpy.CalculateStatistics_management(dist)
