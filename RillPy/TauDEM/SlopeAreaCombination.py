# Script Name: SlopeAreaCombination
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/22/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def SlopeAreaCombination(inlyr,inlyr1,slopeexponent,areaexponent,inputProc,sa):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    slp=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Slope Grid: "+slp)
    print "Input Slope Grid: "+slp

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    sca=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Area Grid: "+sca)
    print "Input Area Grid: "+sca

    #slopeexponent=arcpy.GetParameterAsText(2)
    #arcpy.AddMessage("\nSlope Exponent(m): "+slopeexponent)
    print "Slope Exponent(m): "+str(slopeexponent)

    #areaexponent=arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nArea Exponent(n): "+areaexponent)
    print "Area Exponent(n): "+str(areaexponent)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(4)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Output
    #sa = arcpy.GetParameterAsText(5)
    #arcpy.AddMessage("\nOutput Slope Area Grid: "+sa)
    print "Output Slope Area Grid: "+sa

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' SlopeArea -slp ' + '"' + slp + '"' + ' -sca ' + '"' + sca + '"' + ' -sa ' + '"' + sa + '"' + ' -par ' + str(slopeexponent) + ' ' + str(areaexponent)

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
    arcpy.CalculateStatistics_management(sa)
