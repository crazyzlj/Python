# Script Name: DinfContributingArea
# 
# Created By:  David Tarboton
# Date:        9/28/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def DinfContributingArea(inlyr,shapefile,weightgrid,edgecontamination,inputProc,sca):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    ang=str(desc.catalogPath)
    print "Input Dinf Flow Direction file: "+ang
    #arcpy.AddMessage("\nInput Dinf Flow Direction file: "+ang)

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
    #sca = arcpy.GetParameterAsText(5)
    print "Output Dinf Specific Catchment Area Grid: "+sca
    #arcpy.AddMessage("\nOutput Dinf Specific Catchment Area Grid: "+sca)

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' AreaDinf -ang ' + '"' + ang + '"' + ' -sca ' + '"' + sca + '"'
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
    arcpy.CalculateStatistics_management(sca)
