# Script Name: D8FlowDirection
# 
# Created By:  David Tarboton
# Date:        9/22/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15
# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def D8FlowDirection(inlyr,inputProc,p,sd8):
    # Input
    #inlyr = arcpy.GetParameterAsText(0)  for ArcToolbox
    desc = arcpy.Describe(inlyr)
    fel=str(desc.catalogPath)
    print "Input Pit Filled Elevation file: "+fel
    #arcpy.AddMessage("\nInput Pit Filled Elevation file: "+fel)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(1)  for ArcToolbox
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Outputs
    #p = arcpy.GetParameterAsText(2)    for ArcToolbox
    #arcpy.AddMessage("\nOutput D8 Flow Direction File: "+p)
    #sd8 = arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nOutput D8 Slope File: "+sd8)
    print "Output D8 Flow Direction File: "+p
    print "Output D8 Slope File: "+sd8

    # Construct command 
    cmd = 'mpiexec -n ' + str(inputProc) + ' D8FlowDir -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -sd8 ' + '"' + sd8 + '"'
    #arcpy.AddMessage("\nCommand Line: "+cmd)
    print "Command Line: "+cmd

    # Submit command to operating system
    os.system(cmd)

    # Capture the contents of shell command and print it to the arcgis dialog box
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #arcpy.AddMessage('\nProcess started:\n')
    print "Process started:"
    for line in process.stdout.readlines():
        #arcpy.AddMessage(line)
        print line

    # Calculate statistics on the output so that it displays properly
    #arcpy.AddMessage('Executing: Calculate Statistics\n')
    #print "Executing: Calculate Statistics\n"
    arcpy.CalculateStatistics_management(p)
    arcpy.CalculateStatistics_management(sd8)
