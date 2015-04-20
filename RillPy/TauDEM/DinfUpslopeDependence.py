# Script Name: DinfUpslopeDependence
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/6/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def DinfUpslopeDependence(inlyr,inlyr1,inputProc,dep):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    ang=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput D-Infinity Flow Direction Grid: "+ang)
    print "Input D-Infinity Flow Direction Grid: "+ang

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    dg=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Destination Grid: "+dg)
    print "Input Destination Grid: "+dg

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(2)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Output
    #dep = arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nOutput Upslope Dependence Grid: "+dep)
    print "Output Upslope Dependence Grid: "+dep

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' DinfUpDependence -ang ' + '"' + ang + '"' + ' -dg ' + '"' + dg + '"' + ' -dep ' + '"' + dep + '"'

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
    arcpy.CalculateStatistics_management(dep)
