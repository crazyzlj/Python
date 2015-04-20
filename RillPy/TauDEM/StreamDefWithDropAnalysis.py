# Script Name: StreamDefWithDropAnalysis
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def StreamDefWithDropAnalysis(inlyr,inlyr1,inlyr2,inlyr3,shapefile,maskgrid,minthresh,maxthresh,numthresh,logspace,inputProc,drp,src):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    fel=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Pit Filled Elevation Grid: "+fel)
    print "Input Pit Filled Elevation Grid: "+fel

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    p=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput D8 Flow Direction Grid: "+p)
    print "Input D8 Flow Direction Grid: "+p

    #inlyr2 = arcpy.GetParameterAsText(2)
    desc = arcpy.Describe(inlyr2)
    ad8=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput D8 Contributing Area Grid: "+ad8)
    print "Input D8 Contributing Area Grid: "+ad8

    #inlyr3 = arcpy.GetParameterAsText(3)
    desc = arcpy.Describe(inlyr3)
    ssa=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Accumulated Stream Source Grid: "+ssa)
    print "Input Accumulated Stream Source Grid: "+ssa

    #shapefile=arcpy.GetParameterAsText(4)
    desc = arcpy.Describe(shapefile)
    shfl=str(desc.catalogPath)
    #arcpy.AddMessage("\nInput Outlets Shapefile: "+shfl)
    print "Input Outlets Shapefile: "+shfl

    #maskgrid=arcpy.GetParameterAsText(5)
    if arcpy.Exists(maskgrid):
        desc = arcpy.Describe(maskgrid)
        mask=str(desc.catalogPath)
        #arcpy.AddMessage("\nInput Mask Grid: "+mask)
        print "Input Mask Grid: "+mask

    #minthresh=arcpy.GetParameterAsText(6)
    #arcpy.AddMessage("\nMinimum Threshold Value: "+minthresh)
    print "Minimum Threshold Value: "+str(minthresh)

    #maxthresh=arcpy.GetParameterAsText(7)
    #arcpy.AddMessage("\nMaximum Threshold Value: "+maxthresh)
    print "Maximum Threshold Value: "+str(maxthresh)

    #numthresh=arcpy.GetParameterAsText(8)
    #arcpy.AddMessage("\nNumber of Threshold Values: "+numthresh)
    print "Number of Threshold Values: "+str(numthresh)

    #logspace=arcpy.GetParameterAsText(9)
    #arcpy.AddMessage("\nLogarithmic Spacing: "+logspace)
    print "Logarithmic Spacing: "+logspace

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(10)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)
    print "Input Number of Processes: "+str(inputProc)

    # Outputs
    #drp = arcpy.GetParameterAsText(11)
    #arcpy.AddMessage("\nOutput Drop Analysis Text File: "+drp)
    print "Output Drop Analysis Text File: "+drp

    #src = arcpy.GetParameterAsText(12)
    #arcpy.AddMessage("\nOutput Stream Raster Grid: "+src)
    print "Output Stream Raster Grid: "+src

    # Construct command 1
    cmd = 'mpiexec -n ' + str(inputProc) + ' DropAnalysis -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -ssa ' + '"' + ssa + '"' + ' -o ' + '"' + shfl + '"' + ' -drp ' + '"' + drp + '"' + ' -par ' + str(minthresh) + ' ' + str(maxthresh) + ' ' + str(numthresh) + ' '
    if logspace == 'false':    
        cmd = cmd + '1'
    else:
        cmd = cmd + '0'

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

    drpfile = open(drp,"r")
    theContents=drpfile.read()
    (beg,threshold)=theContents.rsplit(' ',1)
    drpfile.close()

    # Construct command 2
    cmd = 'mpiexec -n ' + str(inputProc) + ' Threshold -ssa ' + '"' + ssa + '"' + ' -src ' + '"' + src + '"' + ' -thresh ' + str(threshold)
    if arcpy.Exists(maskgrid):
        cmd = cmd + ' -mask ' + '"' + mask + '"'

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
    arcpy.CalculateStatistics_management(src)

