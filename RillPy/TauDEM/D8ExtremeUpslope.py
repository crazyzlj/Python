# Script Name: D8ExtremeUpslope
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/22/15


# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def D8ExtremeUpslope(inlyr,inlyr2,maximumupslope,edgecontamination,shapefile,inputProc,ssa):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    p=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput D8 Flow Direction Grid: "+p)
    print "Input D8 Flow Direction Grid: "+p

    #inlyr2 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr2)
    sa=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Value Grid: "+sa)
    print "Input Value Grid: "+sa

    #maximumupslope=arcpy.GetParameterAsText(2)
    #arcpy.AddMessage("\nMaximum Upslope: "+maximumupslope)
    print "Maximum Upslope: "+maximumupslope

    #edgecontamination=arcpy.GetParameterAsText(3)
    #arcpy.AddMessage("\nEdge Contamination: "+edgecontamination)
    print "Edge Contamination: "+edgecontamination

    #shapefile=arcpy.GetParameterAsText(4)
    if arcpy.Exists(shapefile):
        desc = arcpy.Describe(shapefile)
        shfl=str(desc.catalogPath)
        #arcpy.AddMessage("\nInput Outlets Shapefile: "+shfl)
        print "Input Outlets Shapefile: "+shfl

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(5)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Output
    #ssa = arcpy.GetParameterAsText(6)
    #arcpy.AddMessage("\nOutput Extreme Value Grid: "+ssa)
    print "Output Extreme Value Grid: "+ssa

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' D8FlowPathExtremeUp -p ' + '"' + p + '"' + ' -sa ' + '"' + sa + '"' + ' -ssa ' + '"' + ssa + '"'
    if arcpy.Exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shfl + '"'
    if maximumupslope == 'false':
        cmd = cmd + ' -min '
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '

    #arcpy.AddMessage("\nCommand Line: "+cmd)
    print "Command Line: "+cmd

    # Submit command to operating system
    os.system(cmd)

    # Capture the contents of shell command and print it to the arcgis dialog box
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #arcpy.AddMessage('\nProcess started:\n')
    print "Process started:"
    for line in process.stdout.readlines():
        #arcpy.AddMessage(line)
        print line

    # Calculate statistics on the output so that it displays properly
    #arcpy.AddMessage('Executing: Calculate Statistics\n')
    arcpy.CalculateStatistics_management(ssa)