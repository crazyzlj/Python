# Script Name: SlopeOverAreaRatio
# 
# Created By:  David Tarboton
# Date:        9/22/11
# Revised By:  Liangjun Zhu
# Date:        3/6/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def SlopeOverAreaRatio(inlyr,inlyr2,inputProc,sar):
    # Input
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    slp=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Slope Grid: "+slp)
    print "Input Slope Grid: "+slp

    #inlyr2 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr2)
    sca=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Secific Catchment Area Grid: "+sca)
    print "Input Secific Catchment Area Grid: "+sca

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(2)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Outputs
    #sar = arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nOutput Slope Divided By Area Ratio Grid: "+sar)
    print "Output Slope Divided By Area Ratio Grid: "+sar

    # Construct command 
    cmd = 'mpiexec -n ' + str(inputProc) + ' SlopeAreaRatio -slp ' + '"' + slp + '"' + ' -sca ' + '"' + sca + '"' + ' -sar ' + '"' + sar + '"'
    #arcpy.AddMessage("\nCommand Line: "+cmd)
    print "Command Line: "+cmd

    # Submit command to operating system
    os.system(cmd)

    # Capture the contents of shell command and print it to the arcgis dialog box
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #arcpy.AddMessage('\nProcess started:\n')
    print "Process started:"
    for line in process.stdout.readlines():
        print line
        #arcpy.AddMessage(line)

    # Calculate statistics on the output so that it displays properly
    #arcpy.AddMessage('Executing: Calculate Statistics\n')
    arcpy.CalculateStatistics_management(sar)