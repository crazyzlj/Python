# Script Name: Remove Pits
# 
# Created By:  David Tarboton
# Date:        9/21/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15

# Import ArcPy site-package and os modules
#
import arcpy
import os
import sys
import time
import string
import subprocess

def PitRemove(inLyr,inputProc,outFile):
    # Get and describe the first argument
    #
    #inLyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inLyr)
    inZfile=str(desc.catalogPath)
    print "Input Elevation file: "+inZfile
    #arcpy.AddMessage("\nInput Elevation file: "+inZfile)

    # Get the Input No. of Processes
    #
    #inputProc=arcpy.GetParameterAsText(1)
    print "Input Number of Processes: "+str(inputProc)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

    # Get the output file
    #
    #outFile = arcpy.GetParameterAsText(2)
    print "Output Pit Removed Elevation file: "+outFile
    #arcpy.AddMessage("\nOutput Pit Removed Elevation file: "+outFile)

    # Construct the taudem command line.  Put quotes around file names in case there are spaces
    cmd = 'mpiexec -n ' + str(inputProc) + ' pitremove -z ' + '"' + inZfile + '"' + ' -fel ' + '"' + outFile + '"'
    print "Command Line: "+cmd
    #arcpy.AddMessage("\nCommand Line: "+cmd)
    os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    print "Process started:"
    #arcpy.AddMessage('\nProcess started:\n')
    for line in process.stdout.readlines():
        print line
        #arcpy.AddMessage(line)

    #  Calculate statistics so that grids display with correct bounds
    #arcpy.AddMessage('Executing: Calculate Statistics\n')
    arcpy.CalculateStatistics_management(outFile)
