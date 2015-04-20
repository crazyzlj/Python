# Script Name: DinfDistDown
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/6/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def DinfDistDown(inlyr,inlyr1,inlyr2,statisticalmethod,distancemethod,edgecontamination,weightgrid,inputProc,dd):
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
    src=str(desc.catalogPath)
    print "Input Stream Raster Grid: "+src
    #arcpy.AddMessage("\nInput Stream Raster Grid: "+src)

    #statisticalmethod=arcpy.GetParameterAsText(3)
    print "Statistical Method: "+statisticalmethod
    #arcpy.AddMessage("\nStatistical Method: "+statisticalmethod)

    #distancemethod=arcpy.GetParameterAsText(4)
    print "Distance Method: "+distancemethod
    #arcpy.AddMessage("\nDistance Method: "+distancemethod)

    #edgecontamination=arcpy.GetParameterAsText(5)
    print "Edge Contamination: "+edgecontamination
    #arcpy.AddMessage("\nEdge Contamination: "+edgecontamination)

    #weightgrid = arcpy.GetParameterAsText(6)
    if arcpy.Exists(weightgrid):
        desc = arcpy.Describe(weightgrid)
        wg=str(desc.catalogPath)
        print "Input Weight Path Grid: "+wg
        #arcpy.AddMessage("\nInput Weight Path Grid: "+wg)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(7)
    print "Input Number of Processes: "+str(inputProc)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

    # Output
    #dd = arcpy.GetParameterAsText(8)
    print "Output D-Infinity Drop to Stream Grid: "+dd
    #arcpy.AddMessage("\nOutput D-Infinity Drop to Stream Grid: "+dd)

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
    cmd = 'mpiexec -n ' + str(inputProc) + ' DinfDistDown -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -src ' + '"' + src + '"' + ' -dd ' + '"' + dd + '"' + ' -m ' + statmeth + ' ' + distmeth
    if arcpy.Exists(weightgrid):
        cmd = cmd + ' -wg ' + '"' + wg + '"'
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
    arcpy.CalculateStatistics_management(dd)
