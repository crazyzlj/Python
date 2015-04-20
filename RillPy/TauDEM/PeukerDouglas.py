# Script Name: PeukerDouglas
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/22/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def PeukerDouglas(inlyr,centerweight,sideweight,diagonalweight,inputProc,ss):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    fel=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Elevation file: "+fel)
    print "Input Elevation file: "+fel

    #centerweight=arcpy.GetParameterAsText(1)
    #arcpy.AddMessage("\nCenter Smoothing Weight: "+centerweight)
    print "Center Smoothing Weight: "+str(centerweight)

    #sideweight=arcpy.GetParameterAsText(2)
    #arcpy.AddMessage("\nSide Smoothing Weight: "+sideweight)
    print "Side Smoothing Weight: "+str(sideweight)

    #diagonalweight=arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nDiagonal Smoothing Weight: "+diagonalweight)
    print "Diagonal Smoothing Weight: "+str(diagonalweight)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(4)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Output
    #ss = arcpy.GetParameterAsText(5)
    #arcpy.AddMessage("\nOutput Stream Source file: "+ss)
    print "Output Stream Source file: "+ss

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' PeukerDouglas -fel ' + '"' + fel + '"' + ' -ss ' + '"' + ss + '"' + ' -par ' + str(centerweight) + ' ' + str(sideweight) + ' ' + str(diagonalweight)

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
    arcpy.CalculateStatistics_management(ss)
