# Script Name: GridNetwork
# 
# Created By:  David Tarboton
# Date:        9/28/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def GridNetwork(inlyr,inputProc,shapefile,maskgrid,maskthreshold,gord,plen,tlen):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    p=str(desc.catalogPath)
    print "Input D8 Flow Direction file: "+p
    #arcpy.AddMessage("\nInput D8 Flow Direction file: "+p)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(1)
    print "Input Number of Processes: "+str(inputProc)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

    #shapefile=arcpy.GetParameterAsText(2)
    if arcpy.Exists(shapefile):
        desc = arcpy.Describe(shapefile)
        shfl=str(desc.catalogPath)
        print "Input Outlets Shapefile: "+shfl
        #arcpy.AddMessage("\nInput Outlets Shapefile: "+shfl)

    #maskgrid=arcpy.GetParameterAsText(3)
    if arcpy.Exists(maskgrid):
        desc = arcpy.Describe(maskgrid)
        mkgr=str(desc.catalogPath)
        print "Input Mask Grid: "+mkgr
        #arcpy.AddMessage("\nInput Mask Grid: "+mkgr)

    #maskthreshold=arcpy.GetParameterAsText(4)
    if maskthreshold:
        print "Input Mask Threshold Value: "+maskthreshold
        #arcpy.AddMessage("\nInput Mask Threshold Value: "+maskthreshold)

    # Outputs
    #gord=arcpy.GetParameterAsText(5)
    print "Output Strahler Network Order Grid: "+gord
    #arcpy.AddMessage("\nOutput Strahler Network Order Grid: "+gord)

    #plen=arcpy.GetParameterAsText(6)
    print "Output Longest Upslope Length Grid: "+plen
    #arcpy.AddMessage("\nOutput Longest Upslope Length Grid: "+plen)

    #tlen = arcpy.GetParameterAsText(7)
    print "Output Total Upslope Length Grid: "+tlen
    #arcpy.AddMessage("\nOutput Total Upslope Length Grid: "+tlen)

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' GridNet -p ' + '"' + p + '"' + ' -plen ' + '"' + plen + '"' + ' -tlen ' + '"' + tlen + '"' + ' -gord ' + '"' + gord + '"'
    if arcpy.Exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shfl + '"'
    if arcpy.Exists(maskgrid):
        cmd = cmd + ' -mask ' + '"' + mkgr + '"' + ' -thresh ' + maskthreshold

    #arcpy.AddMessage("\nCommand Line: "+cmd)
    print "Command Line: "+cmd

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
    arcpy.CalculateStatistics_management(gord)
    arcpy.CalculateStatistics_management(plen)
    arcpy.CalculateStatistics_management(tlen)
