# Script Name: D8ContributingArea
# 
# Created By:  David Tarboton
# Date:        9/28/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def D8ContributingArea(inlyr,shapefile,weightgrid,edgecontamination,inputProc,ad8):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    p=str(desc.catalogPath)
    print "Input D8 Flow Direction file: "+p
    #arcpy.AddMessage("\nInput D8 Flow Direction file: "+p)

    #shapefile=arcpy.GetParameterAsText(1)
    if arcpy.Exists(shapefile):
        desc = arcpy.Describe(shapefile)
        shfl=str(desc.catalogPath)
        print "Input Outlets Shapefile: "+shfl
        #arcpy.AddMessage("\nInput Outlets Shapefile: "+shfl)

    #weightgrid=arcpy.GetParameterAsText(2)
    if arcpy.Exists(weightgrid):
        desc = arcpy.Describe(weightgrid)
        wtgr=str(desc.catalogPath)
        print "Input Weight Grid: "+wtgr
        #arcpy.AddMessage("\nInput Weight Grid: "+wtgr)

    #edgecontamination=arcpy.GetParameterAsText(3)
    print "Edge Contamination: "+edgecontamination
    #arcpy.AddMessage("\nEdge Contamination: "+edgecontamination)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(4)
    print "Input Number of Processes: "+str(inputProc)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

    # Output
    #ad8 = arcpy.GetParameterAsText(5)
    print "Output D8 Contributing Area Grid: "+ad8
    #arcpy.AddMessage("\nOutput D8 Contributing Area Grid: "+ad8)

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' AreaD8 -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"'
    if arcpy.Exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shfl + '"'
    if arcpy.Exists(weightgrid):
        cmd = cmd + ' -wg ' + '"' + wtgr + '"'
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '
    print "Command Line: "+cmd
    #arcpy.AddMessage("\nCommand Line: "+cmd)

    # Submit command to operating system
    os.system(cmd)

    # Capture the contents of shell command and print it to the arcgis dialog box
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    print "Process started:"
    #arcpy.AddMessage('\nProcess started:\n')
    for line in process.stdout.readlines():
        print line
        #arcpy.AddMessage(line)

    # Calculate statistics on the output so that it displays properly
    #arcpy.AddMessage('Executing: Calculate Statistics\n')
    arcpy.CalculateStatistics_management(ad8)