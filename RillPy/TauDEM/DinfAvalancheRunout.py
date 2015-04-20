# Script Name: DinfAvalancheRunout
# 
# Created By:  David Tarboton
# Date:        9/29/11
# Revised By:  Liangjun Zhu
# Date:        3/5/15

# Import ArcPy site-package and os modules
import arcpy 
import os
import subprocess
def DinfAvalancheRunout(inlyr,inlyr1,inlyr2,propthresh,alphthresh,pathdistancecode,inputProc,rz,dfs):
    # Inputs
    #inlyr = arcpy.GetParameterAsText(0)
    desc = arcpy.Describe(inlyr)
    fel=str(desc.catalogPath)
    print "Input Pit Filled Elevation Grid: "+fel
    #arcpy.AddMessage("\nInput Pit Filled Elevation Grid: "+fel)

    #inlyr1 = arcpy.GetParameterAsText(1)
    desc = arcpy.Describe(inlyr1)
    ang=str(desc.catalogPath)
    print "Input D-Infinity Flow Direction Grid: "+ang
    #arcpy.AddMessage("\nInput D-Infinity Flow Direction Grid: "+ang)

    #inlyr2 = arcpy.GetParameterAsText(2)
    desc = arcpy.Describe(inlyr2)
    ass=str(desc.catalogPath)
    print "Input Avalanche Source Site Grid: "+ass
    #arcpy.AddMessage("\nInput Avalanche Source Site Grid: "+ass)

    #propthresh=arcpy.GetParameterAsText(3)
    print "Input Proportion Threshold: "+str(propthresh)
    #arcpy.AddMessage("\nInput Proportion Threshold: "+propthresh)

    #alphthresh=arcpy.GetParameterAsText(4)
    print "Input Alpha Angle Threshold: "+str(alphthresh)
    #arcpy.AddMessage("\nInput Alpha Angle Threshold: "+alphthresh)

    #pathdistance=arcpy.GetParameterAsText(5)
    if pathdistancecode == 1:
        pathdistance = 'Flow Path'
    else:
        pathdistance = 'Straight Line'
    print "Path Distance Method: "+pathdistance
    #arcpy.AddMessage("\nPath Distance Method: "+pathdistance)

    # Input Number of Processes
    #inputProc=arcpy.GetParameterAsText(6)
    print "Input Number of Processes: "+str(inputProc)
    #arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

    # Output
    #rz = arcpy.GetParameterAsText(7)
    print "Output Runout Zone Grid: "+rz
    #arcpy.AddMessage("\nOutput Runout Zone Grid: "+rz)

    #dfs = arcpy.GetParameterAsText(8)
    print "Output Path Distance Grid: "+dfs
    #arcpy.AddMessage("\nOutput Path Distance Grid: "+dfs)

    # Construct command
    cmd = 'mpiexec -n ' + str(inputProc) + ' DinfAvalanche -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -ass ' + '"' + ass + '"' + ' -rz ' + '"' + rz + '"' + ' -dfs ' + '"' + dfs + '"' + ' -thresh ' + str(propthresh) + ' -alpha ' + str(alphthresh)
    if pathdistance == 'Straight Line':
        cmd = cmd + ' -direct '

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
    arcpy.CalculateStatistics_management(rz)
    arcpy.CalculateStatistics_management(dfs)
