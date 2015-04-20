# Script Name: DinfConcenLimitAccum
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/6/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess

def DinfConcenLimitAccum(inlyr,inlyr1,inlyr2,inlyr3,shapefile,concthresh,edgecontamination,inputProc,q,ctpt,):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    ang=str(desc.catalogPath)
    print "Input D-Infinity Flow Direction Grid: "+ang
    #arcpy.AddMessage("\nInput D-Infinity Flow Direction Grid: "+ang)

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    wg=str(desc.catalogPath)
    print "Input Effective Runoff Weight Grid: "+wg
    #arcpy.AddMessage("\nInput Effective Runoff Weight Grid: "+wg)

    #inlyr2 = arcpy.GetParameterAsText(2)
    desc = arcpy.Describe(inlyr2)
    dg=str(desc.catalogPath)
    print "Input Disturbance Indicator Grid: "+dg
    #arcpy.AddMessage("\nInput Disturbance Indicator Grid: "+dg)

    #inlyr3 = arcpy.GetParameterAsText(3)
    desc = arcpy.Describe(inlyr3)
    dm=str(desc.catalogPath)
    print "Input Decay Multiplier Grid: "+dm
    #arcpy.AddMessage("\nInput Decay Multiplier Grid: "+dm)

    #shapefile=arcpy.GetParameterAsText(4)
    if arcpy.Exists(shapefile):
        desc = arcpy.Describe(shapefile)
        shfl=str(desc.catalogPath)
        print "Input Outlets Shapefile: "+shfl
        #arcpy.AddMessage("\nInput Outlets Shapefile: "+shfl)

    #concthresh=arcpy.GetParameterAsText(5)
    print "Concentration Threshold: "+str(concthresh)
    #arcpy.AddMessage("\nConcentration Threshold: "+concthresh)

    #edgecontamination=arcpy.GetParameterAsText(6)
    print "Edge Contamination: "+edgecontamination
    #arcpy.AddMessage("\nEdge Contamination: "+edgecontamination)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(7)
    print "Input Number of Processes: "+str(inputProc)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

    # Output
    #q = arcpy.GetParameterAsText(8)
    print "Output Overland Flow Specific Discharge Grid: "+q
    #arcpy.AddMessage("\nOutput Overland Flow Specific Discharge Grid: "+q)

    #ctpt = arcpy.GetParameterAsText(9)
    print "Output Concentration Grid: "+ctpt
    #arcpy.AddMessage("\nOutput Concentration Grid: "+ctpt)

    # Construct command 1
    cmd = 'mpiexec -n ' + str(inputProc) + ' AreaDinf -ang ' + '"' + ang + '"' + ' -sca ' + '"' + q + '"' + ' -wg ' + '"' + wg + '"'
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
    arcpy.CalculateStatistics_management(q)

    # Construct command 2
    cmd = 'mpiexec -n ' + str(inputProc) + ' DinfConcLimAccum -ang ' + '"' + ang + '"' + ' -dg ' + '"' + dg + '"' + ' -dm ' + '"' + dm + '"' + ' -ctpt ' + '"' + ctpt + '"' + ' -q ' + '"' + q + '"' + ' -csol ' + str(concthresh)
    if arcpy.Exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shfl + '"'
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
    arcpy.CalculateStatistics_management(ctpt)
