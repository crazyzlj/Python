# Script Name: DinfDistUp
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/6/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def DinfDistUp(inlyr,inlyr1,inlyr2,propthresh,statisticalmethod,distancemethod,edgecontamination,inputProc,du):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    ang=str(desc.catalogPath)
    print "Input D-Infinity Flow Direction Grid: "+ang
    #arcpy.AddMessage("\nInput D-Infinity Flow Direction Grid: "+ang)

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    fel=str(desc.catalogPath)
    print "Input Pit Filled Elevation Grid: "+fel
    #arcpy.AddMessage("\nInput Pit Filled Elevation Grid: "+fel)

    #inlyr2 = arcpy.GetParameterAsText(2)
    desc = arcpy.Describe(inlyr2)
    slp=str(desc.catalogPath)
    print "Input Slope Grid: "+slp
    #arcpy.AddMessage("\nInput Slope Grid: "+slp)

    #propthresh=arcpy.GetParameterAsText(3)
    print "Input Proportion Threshold: "+str(propthresh)
    #arcpy.AddMessage("\nInput Proportion Threshold: "+propthresh)

    #statisticalmethod=arcpy.GetParameterAsText(4)
    print "Statistical Method: "+statisticalmethod
    #arcpy.AddMessage("\nStatistical Method: "+statisticalmethod)

    #distancemethod=arcpy.GetParameterAsText(5)
    print "Distance Method: "+distancemethod
    #arcpy.AddMessage("\nDistance Method: "+distancemethod)

    #edgecontamination=arcpy.GetParameterAsText(6)
    print "Edge Contamination: "+edgecontamination
    #arcpy.AddMessage("\nEdge Contamination: "+edgecontamination)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(7)
    print "Input Number of Processes: "+str(inputProc)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

    # Output
    #du = arcpy.GetParameterAsText(8)
    print "Output D-Infinity Distance Up: "+du
    #arcpy.AddMessage("\nOutput D-Infinity Distance Up: "+du)

    # Construct command
    if statisticalmethod == 'Average':
        statmeth = 'ave'
    if statisticalmethod == 'Maximum':
        statmeth = 'max'
    if statisticalmethod == 'Minimum':
        statmeth = 'min'
    if distancemethod == 'Horizontal':
        distmeth = 'h'
    if distancemethod == 'Vertical':
        distmeth = 'v'
    if distancemethod == 'Pythagoras':
        distmeth = 'p'
    if distancemethod == 'Surface':
        distmeth = 's'
    cmd = 'mpiexec -n ' + str(inputProc) + ' DinfDistUp -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -slp ' + '"' + slp + '"' + ' -du ' + '"' + du + '"' + ' -m ' + statmeth + ' ' + distmeth + ' -thresh ' + str(propthresh)
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
    arcpy.CalculateStatistics_management(du)