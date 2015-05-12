# Script Name: TauDEM functions
# 
# Created By:  David Tarboton
# Date:        9/28/11
# Revised By:  Liangjun Zhu (zlj@lreis.ac.cn)
# Date:        3/5/15
# Modified  :  Integrate to one file. Run without arcpy. Same name with executable files.
# Revised By:  Liangjun Zhu
# Date:        4/14/15
# Modified  :  add path to TauDEM executable program


# Program: TauDEM and extensions based on TauDEM parallelized framework
# 
# Revised By:  Liangjun Zhu
# Date From :  3/20/15
# Email     :  zlj@lreis.ac.cn
#

# Import modules
import os
import sys
import time
import string
import subprocess

## Basic Grid Analysis
def pitremove(inZfile,inputProc,outFile, exeDir=None):
    print "PitRemove......"
    print "Input Elevation file: "+inZfile
    print "Input Number of Processes: "+str(inputProc)
    print "Output Pit Removed Elevation file: "+outFile
    # Construct the taudem command line.  Put quotes around file names in case there are spaces
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' pitremove -z ' + '"' + inZfile + '"' + ' -fel ' + '"' + outFile + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\pitremove -z ' + '"' + inZfile + '"' + ' -fel ' + '"' + outFile + '"'
    print "Command Line: "+cmd
    ##os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def D8FlowDir(fel,inputProc,p,sd8, exeDir=None):
    print "Calculating D8 flow direction......"
    print "Input Pit Filled Elevation file: "+fel
    print "Input Number of Processes: "+str(inputProc)
    print "Output D8 Flow Direction File: "+p
    print "Output D8 Slope File: "+sd8
    # Construct command
     
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' D8FlowDir -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -sd8 ' + '"' + sd8 + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\D8FlowDir -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -sd8 ' + '"' + sd8 + '"'
    print "Command Line: "+cmd
    ##os.system(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def DinfFlowDir(fel,inputProc,ang,slp, exeDir=None):
    print "Calculating D-infinity direction......"
    print "Input Pit Filled Elevation file: "+fel
    print "Input Number of Processes: "+str(inputProc)
    print "Output Dinf Flow Direction File: "+ang
    print "Output Dinf Slope File: "+slp
    # Construct command 
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfFlowDir -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -slp ' + '"' + slp + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfFlowDir -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -slp ' + '"' + slp + '"'
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
        
def AreaD8(p,Shapefile,weightgrid,edgecontamination,inputProc,ad8, exeDir=None):
    print "Calculating D8 contributing area......"
    print "Input D8 Flow Direction file: "+p
    if os.path.exists(Shapefile):
        print "Input Outlets Shapefile: "+Shapefile
    if os.path.exists(weightgrid):
        print "Input Weight Grid: "+weightgrid
    print "Edge Contamination: "+edgecontamination
    print "Input Number of Processes: "+str(inputProc)
    print "Output D8 Contributing Area Grid: "+ad8
    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' AreaD8 -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\AreaD8 -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"'
    if os.path.exists(Shapefile):
        cmd = cmd + ' -o ' + '"' + Shapefile + '"'
    if os.path.exists(weightgrid):
        cmd = cmd + ' -wg ' + '"' + weightgrid + '"'
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
        
def AreaDinf(ang,shapefile,weightgrid,edgecontamination,inputProc,sca, exeDir=None):
    print "Calculating D-infinity contributing area......"
    print "Input Dinf Flow Direction file: "+ang
    if os.path.exists(shapefile):
        print "Input Outlets Shapefile: "+shapefile
    if os.path.exists(weightgrid):
        print "Input Weight Grid: "+weightgrid
    print "Edge Contamination: "+edgecontamination
    print "Input Number of Processes: "+str(inputProc)
    print "Output Dinf Specific Catchment Area Grid: "+sca
    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' AreaDinf -ang ' + '"' + ang + '"' + ' -sca ' + '"' + sca + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\AreaDinf -ang ' + '"' + ang + '"' + ' -sca ' + '"' + sca + '"'
    if os.path.exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shapefile + '"'
    if os.path.exists(weightgrid):
        cmd = cmd + ' -wg ' + '"' + weightgrid + '"'
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def GridNet(p,inputProc,shapefile,maskgrid,maskthreshold,gord,plen,tlen, exeDir=None):
    print "Creating 1) the longest path, 2) the total path, and 3) the Strahler order number for each grid based on D8 model......."
    print "Input D8 Flow Direction file: "+p
    print "Input Number of Processes: "+str(inputProc)
    if os.path.exists(shapefile):
        print "Input Outlets Shapefile: "+shapefile
    if os.path.exists(maskgrid):
        print "Input Mask Grid: "+maskgrid
    if maskthreshold:
        print "Input Mask Threshold Value: "+maskthreshold
    print "Output Strahler Network Order Grid: "+gord
    print "Output Longest Upslope Length Grid: "+plen
    print "Output Total Upslope Length Grid: "+tlen
    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' GridNet -p ' + '"' + p + '"' + ' -plen ' + '"' + plen + '"' + ' -tlen ' + '"' + tlen + '"' + ' -gord ' + '"' + gord + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\GridNet -p ' + '"' + p + '"' + ' -plen ' + '"' + plen + '"' + ' -tlen ' + '"' + tlen + '"' + ' -gord ' + '"' + gord + '"'
    if os.path.exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shapefile + '"'
    if os.path.exists(maskgrid):
        cmd = cmd + ' -mask ' + '"' + maskgrid + '"' + ' -thresh ' + maskthreshold
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

## Specialized grid analysis
def DinfAvalanche(fel,ang,ass,propthresh,alphthresh,pathdistancecode,inputProc,rz,dfs, exeDir=None):
    print "Input Pit Filled Elevation Grid: "+fel
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Avalanche Source Site Grid: "+ass
    print "Input Proportion Threshold: "+str(propthresh)
    print "Input Alpha Angle Threshold: "+str(alphthresh)
    if pathdistancecode == 1:
        pathdistance = 'Flow Path'
    else:
        pathdistance = 'Straight Line'
    print "Path Distance Method: "+pathdistance
    print "Input Number of Processes: "+str(inputProc)

    print "Output Runout Zone Grid: "+rz
    print "Output Path Distance Grid: "+dfs

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfAvalanche -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -ass ' + '"' + ass + '"' + ' -rz ' + '"' + rz + '"' + ' -dfs ' + '"' + dfs + '"' + ' -thresh ' + str(propthresh) + ' -alpha ' + str(alphthresh)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfAvalanche -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -ass ' + '"' + ass + '"' + ' -rz ' + '"' + rz + '"' + ' -dfs ' + '"' + dfs + '"' + ' -thresh ' + str(propthresh) + ' -alpha ' + str(alphthresh)
        
    if pathdistance == 'Straight Line':
        cmd = cmd + ' -direct '
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
        
def DinfConcLimAccum(ang,wg,dg,dm,shapefile,concthresh,edgecontamination,inputProc,q,ctpt, exeDir=None):
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Effective Runoff Weight Grid: "+wg
    print "Input Disturbance Indicator Grid: "+dg
    print "Input Decay Multiplier Grid: "+dm
    if os.path.exists(shapefile):
        print "Input Outlets Shapefile: "+shapefile
    print "Concentration Threshold: "+str(concthresh)
    print "Edge Contamination: "+edgecontamination
    print "Input Number of Processes: "+str(inputProc)

    print "Output Overland Flow Specific Discharge Grid: "+q
    print "Output Concentration Grid: "+ctpt

    # Construct command 1
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' AreaDinf -ang ' + '"' + ang + '"' + ' -sca ' + '"' + q + '"' + ' -wg ' + '"' + wg + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\AreaDinf -ang ' + '"' + ang + '"' + ' -sca ' + '"' + q + '"' + ' -wg ' + '"' + wg + '"'
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

    # Construct command 2
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfConcLimAccum -ang ' + '"' + ang + '"' + ' -dg ' + '"' + dg + '"' + ' -dm ' + '"' + dm + '"' + ' -ctpt ' + '"' + ctpt + '"' + ' -q ' + '"' + q + '"' + ' -csol ' + str(concthresh)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) +  ' ' + exeDir +'\\DinfConcLimAccum -ang ' + '"' + ang + '"' + ' -dg ' + '"' + dg + '"' + ' -dm ' + '"' + dm + '"' + ' -ctpt ' + '"' + ctpt + '"' + ' -q ' + '"' + q + '"' + ' -csol ' + str(concthresh)
        
    if os.path.exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shapefile + '"'
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
def DinfDecayAccum(ang,dm,wg,shapefile,edgecontamination,inputProc,dsca, exeDir=None):
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Decay Multiplier Grid: "+dm
    if os.path.exists(wg):
        print "Input Weight Grid: "+wg
    if os.path.exists(shapefile):
        print "Input Outlets Shapefile: "+shapefile
    print "Edge Contamination: "+edgecontamination
    print "Input Number of Processes: "+str(inputProc)

    print "Output Decayed Specific Catchment Area Grid: "+dsca

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfDecayAccum -ang ' + '"' + ang + '"' + ' -dsca ' + '"' + dsca + '"' + ' -dm ' + '"' + dm + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) +  ' ' + exeDir +'\\DinfDecayAccum -ang ' + '"' + ang + '"' + ' -dsca ' + '"' + dsca + '"' + ' -dm ' + '"' + dm + '"'
        
    if os.path.exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shapefile + '"'
    if os.path.exists(wg):
        cmd = cmd + ' -wg ' + '"' + wg + '"'
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def DinfDistDown(ang,fel,src,statisticalmethod,distancemethod,edgecontamination,wg,inputProc,dd, exeDir=None):
    print "Calculating distance down to stream based on D-infinity model......"
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Pit Filled Elevation Grid: "+fel
    print "Input Stream Raster Grid: "+src
    print "Statistical Method: "+statisticalmethod
    print "Distance Method: "+distancemethod
    print "Edge Contamination: "+edgecontamination
    if os.path.exists(wg):
        print "Input Weight Path Grid: "+wg
    print "Input Number of Processes: "+str(inputProc)
    print "Output D-Infinity Drop to Stream Grid: "+dd

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
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfDistDown -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -src ' + '"' + src + '"' + ' -dd ' + '"' + dd + '"' + ' -m ' + statmeth + ' ' + distmeth
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfDistDown -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -src ' + '"' + src + '"' + ' -dd ' + '"' + dd + '"' + ' -m ' + statmeth + ' ' + distmeth
        
    if os.path.exists(wg):
        cmd = cmd + ' -wg ' + '"' + wg + '"'
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
def DinfDistUp(ang,fel,slp,propthresh,statisticalmethod,distancemethod,edgecontamination,inputProc,du, exeDir=None):
    print "Calculating distance up to ridges based on D-infinity model......"
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Pit Filled Elevation Grid: "+fel
    print "Input Slope Grid: "+slp
    print "Input Proportion Threshold: "+str(propthresh)
    print "Statistical Method: "+statisticalmethod
    print "Distance Method: "+distancemethod
    print "Edge Contamination: "+edgecontamination
    print "Input Number of Processes: "+str(inputProc)

    print "Output D-Infinity Distance Up: "+du

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
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfDistUp -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -slp ' + '"' + slp + '"' + ' -du ' + '"' + du + '"' + ' -m ' + statmeth + ' ' + distmeth + ' -thresh ' + str(propthresh)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfDistUp -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -slp ' + '"' + slp + '"' + ' -du ' + '"' + du + '"' + ' -m ' + statmeth + ' ' + distmeth + ' -thresh ' + str(propthresh)
        
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
        
def DinfRevAccum(ang,dm,inputProc,racc,dmax, exeDir=None):
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Weight Grid: "+dm
    print "Input Number of Processes: "+str(inputProc)

    print "Output Reverse Accumulation Grid: "+racc
    print "Output Maximum Downslope Grid: "+dmax

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfRevAccum -ang ' + '"' + ang + '"' + ' -wg ' + '"' + dm + '"' + ' -racc ' + '"' + racc + '"' + ' -dmax ' + '"' + dmax + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfRevAccum -ang ' + '"' + ang + '"' + ' -wg ' + '"' + dm + '"' + ' -racc ' + '"' + racc + '"' + ' -dmax ' + '"' + dmax + '"'
    
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def DinfTransLimAccum(ang,tsup,tc,cs,shapefile,edgecontamination,inputProc,tla,tdep,ctpt, exeDir=None):
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Supply Grid: "+tsup
    print "Input Transport Capacity Grid: "+tc
    if os.path.exists(cs):
        print "Input Concentration Grid: "+cs
    if os.path.exists(shapefile):
        print "Input Outlets Shapefile: "+shapefile
    print "Edge Contamination: "+edgecontamination
    print "Input Number of Processes: "+str(inputProc)

    print "Output Transport Limited Accumulation Grid: "+tla
    print "Output Deposition Grid: "+tdep
    if os.path.exists(tc):
        print "Output Concentration Grid: "+ctpt

    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfTransLimAccum -ang ' + '"' + ang + '"' + ' -tsup ' + '"' + tsup + '"' + ' -tc ' + '"' + tc + '"' + ' -tla ' + '"' + tla + '"' + ' -tdep ' + '"' + tdep + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfTransLimAccum -ang ' + '"' + ang + '"' + ' -tsup ' + '"' + tsup + '"' + ' -tc ' + '"' + tc + '"' + ' -tla ' + '"' + tla + '"' + ' -tdep ' + '"' + tdep + '"'
        
    if os.path.exists(tc):
        cmd = cmd + ' -cs ' + '"' + cs + '"' + ' -ctpt ' + '"' + ctpt + '"'
    if os.path.exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shapefile + '"'
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def DinfUpDependence(ang,dg,inputProc,dep, exeDir=None):
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Destination Grid: "+dg
    print "Input Number of Processes: "+str(inputProc)

    print "Output Upslope Dependence Grid: "+dep

    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfUpDependence -ang ' + '"' + ang + '"' + ' -dg ' + '"' + dg + '"' + ' -dep ' + '"' + dep + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfUpDependence -ang ' + '"' + ang + '"' + ' -dg ' + '"' + dg + '"' + ' -dep ' + '"' + dep + '"'
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def D8HDistToStrm(p,src,thresh,inputProc,dist, exeDir=None):
    
    print "Calculating distance down to stream based on D8 model......"
    print "Input D8 Flow Direction Grid: "+p
    print "Input Stream Raster Grid: "+src
    print "Threshold: "+str(thresh)
    print "Input Number of Processes: "+str(inputProc)

    print "Output Distance To Streams: "+dist
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' D8HDistToStrm -p ' + '"' + p + '"' + ' -src ' + '"' + src + '"' + ' -dist ' + '"' + dist + '"' + ' -thresh ' + str(thresh)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\D8HDistToStrm -p ' + '"' + p + '"' + ' -src ' + '"' + src + '"' + ' -dist ' + '"' + dist + '"' + ' -thresh ' + str(thresh)
    
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def SlopeAveDown(p,fel,distance,inputProc,slpd, exeDir=None):
    print "Input D8 Flow Direction Grid: "+p
    print "Input Pit Filled Elevation Grid: "+fel
    print "Distance: "+str(distance)
    print "Input Number of Processes: "+str(inputProc)

    print "Output Slope Average Down Grid: "+slpd

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' SlopeAveDown -p ' + '"' + p + '"' + ' -fel ' + '"' + fel + '"' + ' -slpd ' + '"' + slpd + '"' + ' -dn ' + str(distance)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\SlopeAveDown -p ' + '"' + p + '"' + ' -fel ' + '"' + fel + '"' + ' -slpd ' + '"' + slpd + '"' + ' -dn ' + str(distance)
    
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def SlopeAreaRatio(slp,sca,inputProc,sar, exeDir=None):
    print "Input Slope Grid: "+slp
    print "Input Secific Catchment Area Grid: "+sca
    print "Input Number of Processes: "+str(inputProc)

    print "Output Slope Divided By Area Ratio Grid: "+sar
    # Construct command 
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' SlopeAreaRatio -slp ' + '"' + slp + '"' + ' -sca ' + '"' + sca + '"' + ' -sar ' + '"' + sar + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\SlopeAreaRatio -slp ' + '"' + slp + '"' + ' -sca ' + '"' + sca + '"' + ' -sar ' + '"' + sar + '"'
    
    print "Command Line: "+cmd
    #os.system(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

## Stream network analysis toolset
def D8FlowPathExtremeUp(p,sa,maximumupslope,edgecontamination,shapefile,inputProc,ssa, exeDir=None):
    print "Input D8 Flow Direction Grid: "+p
    print "Input Value Grid: "+sa
    print "Maximum Upslope: "+maximumupslope
    print "Edge Contamination: "+edgecontamination
    if os.path.exists(shapefile):
        print "Input Outlets Shapefile: "+shapefile
    print "Input Number of Processes: "+str(inputProc)

    print "Output Extreme Value Grid: "+ssa
    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' D8FlowPathExtremeUp -p ' + '"' + p + '"' + ' -sa ' + '"' + sa + '"' + ' -ssa ' + '"' + ssa + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\D8FlowPathExtremeUp -p ' + '"' + p + '"' + ' -sa ' + '"' + sa + '"' + ' -ssa ' + '"' + ssa + '"'
        
    if os.path.exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shapefile + '"'
    if maximumupslope == 'false':
        cmd = cmd + ' -min '
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def GageWatershed(p,shapefile,inputProc,gw,idf, exeDir=None):
    print "Input D8 Flow Direction Grid: "+p    
    print "Input Outlets Shapefile: "+shapefile
    print "Input Number of Processes: "+str(inputProc)

    print "Output GageWatershed Grid: "+gw
    print "Output Downstream ID Text File: "+idf

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' GageWatershed'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\GageWatershed'
    cmd = cmd+ ' -p ' + '"' + p + '"'
    cmd = cmd + ' -o ' + '"' + shapefile + '"'
    cmd = cmd + ' -gw ' + '"' + gw + '"'
    if idf != '':
        cmd=cmd + ' -id ' + '"' + idf + '"' 
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def LengthArea(plen,ad8,threshold,exponent,inputProc,ss, exeDir=None):
    print "Input Length Grid: "+plen
    print "Input Contributing Area Grid: "+ad8
    print "Threshold(M): "+str(threshold)
    print "Exponent(y): "+str(exponent)
    print "Input Number of Processes: "+str(inputProc)
    print "Output Stream Source Grid: "+ss

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' LengthArea -plen ' + '"' + plen + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -ss ' + '"' + ss + '"' + ' -par ' + str(threshold) + ' ' + str(exponent)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\LengthArea -plen ' + '"' + plen + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -ss ' + '"' + ss + '"' + ' -par ' + str(threshold) + ' ' + str(exponent)
        
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
        
def MoveOutletsToStreams(p,src,shapefile,maxdistance,inputProc,om, exeDir=None):
    print "Moving outlet point(s) to streams......"
    print "Input D8 Flow Direction Grid: "+p
    print "Input Stream Raster Grid: "+src
    print "Input Outlets Shapefile: "+shapefile
    print "Minimum Threshold Value: "+str(maxdistance)
    print "Input Number of Processes: "+str(inputProc)

    print "Output Outlet Shapefile: "+om

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' MoveOutletsToStreams -p ' + '"' + p + '"' + ' -src ' + '"' + src + '"' + ' -o ' + '"' + shapefile + '"' + ' -om ' + '"' + om + '"' + ' -md ' + str(maxdistance)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\MoveOutletsToStreams -p ' + '"' + p + '"' + ' -src ' + '"' + src + '"' + ' -o ' + '"' + shapefile + '"' + ' -om ' + '"' + om + '"' + ' -md ' + str(maxdistance)
        
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def PeukerDouglas(fel,centerweight,sideweight,diagonalweight,inputProc,ss, exeDir=None):
    print "PeukerDouglas algrithm to dectect stream sources......"
    print "Input Elevation file: "+fel
    print "Center Smoothing Weight: "+str(centerweight)
    print "Side Smoothing Weight: "+str(sideweight)
    print "Diagonal Smoothing Weight: "+str(diagonalweight)
    print "Input Number of Processes: "+str(inputProc)

    print "Output Stream Source file: "+ss

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' PeukerDouglas -fel ' + '"' + fel + '"' + ' -ss ' + '"' + ss + '"' + ' -par ' + str(centerweight) + ' ' + str(sideweight) + ' ' + str(diagonalweight)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) +  ' ' + exeDir +'\\PeukerDouglas -fel ' + '"' + fel + '"' + ' -ss ' + '"' + ss + '"' + ' -par ' + str(centerweight) + ' ' + str(sideweight) + ' ' + str(diagonalweight)
    
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def SlopeArea(slp,sca,slopeexponent,areaexponent,inputProc,sa, exeDir=None):
    print "Calculating Slope-Area ratio for TWI......"
    print "Input Slope Grid: "+slp
    print "Input Area Grid: "+sca
    print "Slope Exponent(m): "+str(slopeexponent)
    print "Area Exponent(n): "+str(areaexponent)
    print "Input Number of Processes: "+str(inputProc)

    print "Output Slope Area Grid: "+sa

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' SlopeArea -slp ' + '"' + slp + '"' + ' -sca ' + '"' + sca + '"' + ' -sa ' + '"' + sa + '"' + ' -par ' + str(slopeexponent) + ' ' + str(areaexponent)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\SlopeArea -slp ' + '"' + slp + '"' + ' -sca ' + '"' + sca + '"' + ' -sa ' + '"' + sa + '"' + ' -par ' + str(slopeexponent) + ' ' + str(areaexponent)
    
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def Threshold(ssa,mask,threshold,inputProc,src, exeDir=None):
    print "Stream definition according to threshold......"
    print "Input Accumulated Stream Source Grid: "+ssa
    if os.path.exists(mask):        
        print "Input Mask Grid: "+mask
    print "Threshold: "+str(threshold)
    print "Input Number of Processes: "+str(inputProc)

    print "Output Stream Raster Grid: "+src

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' Threshold -ssa ' + '"' + ssa + '"' + ' -src ' + '"' + src + '"' + ' -thresh ' + str(threshold)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\Threshold -ssa ' + '"' + ssa + '"' + ' -src ' + '"' + src + '"' + ' -thresh ' + str(threshold)
        
    if os.path.exists(mask):
        cmd = cmd + ' -mask ' + mask

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def DropAnalysis(fel,p,ad8,ssa,shapefile,minthresh,maxthresh,numthresh,logspace,inputProc,drp, exeDir=None):
    print "Stream drop analysis for the optimal threshold......"
    print "Input Pit Filled Elevation Grid: "+fel
    print "Input D8 Flow Direction Grid: "+p
    print "Input D8 Contributing Area Grid: "+ad8
    print "Input Accumulated Stream Source Grid: "+ssa
    print "Input Outlets Shapefile: "+shapefile
    print "Minimum Threshold Value: "+str(minthresh)
    print "Maximum Threshold Value: "+str(maxthresh)
    print "Number of Threshold Values: "+str(numthresh)
    print "Logarithmic Spacing: "+logspace
    print "Input Number of Processes: "+str(inputProc)

    print "Output Drop Analysis Text File: "+drp

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DropAnalysis -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -ssa ' + '"' + ssa + '"' + ' -o ' + '"' + shapefile + '"' + ' -drp ' + '"' + drp + '"' + ' -par ' + str(minthresh) + ' ' + str(maxthresh) + ' ' + str(numthresh) + ' '
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DropAnalysis -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -ssa ' + '"' + ssa + '"' + ' -o ' + '"' + shapefile + '"' + ' -drp ' + '"' + drp + '"' + ' -par ' + str(minthresh) + ' ' + str(maxthresh) + ' ' + str(numthresh) + ' '
    if logspace == 'false':    
        cmd = cmd + '1'
    else:
        cmd = cmd + '0'

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def StreamNet(fel,p,ad8,src,shapefile,delineate,inputProc,ord,tree,coord,net,w, exeDir=None):
    print "Generating stream network ......"
    print "Input Pit Filled Elevation Grid: "+fel
    print "Input D8 Flow Direction Grid: "+p
    print "Input D8 Drainage Area: "+ad8
    print "Input Stream Raster Grid: "+src
    if os.path.exists(shapefile):
        print "Input Outlets Shapefile as Network Nodes: "+shapefile
    print "Delineate Single Watershed: "+delineate
    print "Input Number of Processes: "+str(inputProc)

    print "Output Stream Order Grid: "+ord
    print "Output Network Connectivity Tree: "+tree
    print "Output Network Coordinates: "+coord
    print "Output Stream Reach Shapefile: "+net
    print "Output Watershed Grid: "+w

    # Construct command
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' StreamNet -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -src ' + '"' + src + '"' + ' -ord ' + '"' + ord + '"' + ' -tree ' + '"' + tree + '"' + ' -coord ' + '"' + coord + '"' + ' -net ' + '"' + net + '"' + ' -w ' + '"' + w + '"'
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\StreamNet -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -src ' + '"' + src + '"' + ' -ord ' + '"' + ord + '"' + ' -tree ' + '"' + tree + '"' + ' -coord ' + '"' + coord + '"' + ' -net ' + '"' + net + '"' + ' -w ' + '"' + w + '"'
        
    if os.path.exists(shapefile):
        cmd = cmd + ' -o ' + '"' + shapefile + '"'
    if delineate == 'true':
        cmd = cmd + ' -sw '
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
    
def StreamDefWithDropAnalysis(fel,p,ad8,ssa,shapefile,mask,minthresh,maxthresh,numthresh,logspace,inputProc,drp,src, exeDir=None):
    print "Input Pit Filled Elevation Grid: "+fel
    print "Input D8 Flow Direction Grid: "+p
    print "Input D8 Contributing Area Grid: "+ad8
    print "Input Accumulated Stream Source Grid: "+ssa
    print "Input Outlets Shapefile: "+shapefile
    if os.path.exists(mask):
        print "Input Mask Grid: "+mask
    print "Minimum Threshold Value: "+str(minthresh)
    print "Maximum Threshold Value: "+str(maxthresh)
    print "Number of Threshold Values: "+str(numthresh)
    print "Logarithmic Spacing: "+logspace
    print "Input Number of Processes: "+str(inputProc)
    print "Output Drop Analysis Text File: "+drp
    print "Output Stream Raster Grid: "+src

    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DropAnalysis -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -ssa ' + '"' + ssa + '"' + ' -o ' + '"' + shapefile + '"' + ' -drp ' + '"' + drp + '"' + ' -par ' + str(minthresh) + ' ' + str(maxthresh) + ' ' + str(numthresh) + ' '
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DropAnalysis -fel ' + '"' + fel + '"' + ' -p ' + '"' + p + '"' + ' -ad8 ' + '"' + ad8 + '"' + ' -ssa ' + '"' + ssa + '"' + ' -o ' + '"' + shapefile + '"' + ' -drp ' + '"' + drp + '"' + ' -par ' + str(minthresh) + ' ' + str(maxthresh) + ' ' + str(numthresh) + ' '
        
    if logspace == 'false':    
        cmd = cmd + '1'
    else:
        cmd = cmd + '0'
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

    drpfile = open(drp,"r")
    theContents=drpfile.read()
    (beg,threshold)=theContents.rsplit(' ',1)
    drpfile.close()

    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' Threshold -ssa ' + '"' + ssa + '"' + ' -src ' + '"' + src + '"' + ' -thresh ' + str(threshold)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\Threshold -ssa ' + '"' + ssa + '"' + ' -src ' + '"' + src + '"' + ' -thresh ' + str(threshold)
    if os.path.exists( mask):
        cmd = cmd + ' -mask ' + '"' + mask + '"'
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line



####   Functions added by Liangjun Zhu    ####

def D8DistDownToStream(p,fel,src,dist,distancemethod,thresh,inputProc,exeDir=None):
    
    print "Calculating distance down to stream based on D8 model......"
    print "Input D8 Flow Direction Grid: "+p
    print "Input filled DEM: "+fel
    print "Input Stream Raster Grid: "+src
    print "Distance calculating method: "+distancemethod
    print "Threshold: "+str(thresh)
    print "Input Number of Processes: "+str(inputProc)

    print "Output Distance To Streams: "+dist
    if distancemethod == 'Horizontal':
        distmeth = 'h'
    if distancemethod == 'Vertical':
        distmeth = 'v'
    if distancemethod == 'Pythagoras':
        distmeth = 'p'
    if distancemethod == 'Surface':
        distmeth = 's'
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' D8DistDownToStream -p ' + '"' + p + '"' + ' -fel ' + '"' +fel+ '"' +' -src ' + '"' + src + '"' + ' -dist ' + '"' + dist + '"' +' -m '+distmeth+ ' -thresh ' + str(thresh)
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\D8DistDownToStream -p ' + '"' + p + '"' + ' -fel ' + '"' +fel+ '"' +' -src ' + '"' + src + '"' + ' -dist ' + '"' + dist + '"' +' -m '+distmeth+ ' -thresh ' + str(thresh)
    
    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def D8DistUpToRidge(p,fel,du,distancemethod,statisticalmethod,inputProc,rdg=None,exeDir=None):
    print "Calculating distance up to ridges based on D8 model......"
    print "Input D8 Flow Direction Grid: "+p
    print "Input Pit Filled Elevation Grid: "+fel
    if not rdg is None:
        print "Input Ridge Source Grid: "+rdg
    print "Statistical Method: "+statisticalmethod
    print "Distance Method: "+distancemethod
    print "Input Number of Processes: "+str(inputProc)
    print "Output D-Infinity Distance Up: "+du

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
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' D8DistUpToRidge -p '
    else:
        cmd = 'mpiexec -n ' + str(inputProc) +  ' ' + exeDir +'\\D8DistUpToRidge -p '
    if not rdg is None:
        cmd = cmd + '"' + p + '"' +' -fel ' + '"' + fel + '"' + ' -rdg ' + '"' + rdg + '"' + ' -du ' + '"' + du + '"' + ' -m ' + statmeth + ' ' + distmeth
    else:
        cmd = cmd + '"' + p + '"' +' -fel ' + '"' + fel + '"' + ' -du ' + '"' + du + '"' + ' -m ' + statmeth + ' ' + distmeth

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def DinfDistUpToRidge(ang,fel,slp,propthresh,statisticalmethod,distancemethod,edgecontamination,inputProc,du,rdg=None, exeDir=None):
    print "Calculating distance up to ridges based on D-infinity model......"
    print "Input D-Infinity Flow Direction Grid: "+ang
    print "Input Pit Filled Elevation Grid: "+fel
    print "Input Slope Grid: "+slp
    if not rdg is None:
        print "Input Ridge Source Grid: "+rdg
    print "Input Proportion Threshold: "+str(propthresh)
    print "Statistical Method: "+statisticalmethod
    print "Distance Method: "+distancemethod
    print "Edge Contamination: "+edgecontamination
    print "Input Number of Processes: "+str(inputProc)

    print "Output D-Infinity Distance Up: "+du

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
    if exeDir is None:
        cmd = 'mpiexec -n ' + str(inputProc) + ' DinfDistUpToRidge '
    else:
        cmd = 'mpiexec -n ' + str(inputProc) + ' ' + exeDir +'\\DinfDistUpToRidge '
    if not rdg is None:
        cmd = cmd +' -ang ' + '"' + ang + '"'+' -fel '+ '"' + fel + '"' + ' -slp ' + '"' + slp + '"' +' -rdg ' + '"' + rdg + '"' +  ' -du ' + '"' + du + '"' + ' -m ' + statmeth + ' ' + distmeth + ' -thresh ' + str(propthresh)
    else:
        cmd = cmd +' -ang ' + '"' + ang + '"'+' -fel '+ '"' + fel + '"' + ' -slp ' + '"' + slp + '"' + ' -du ' + '"' + du + '"' + ' -m ' + statmeth + ' ' + distmeth + ' -thresh ' + str(propthresh)
    if edgecontamination == 'false':
        cmd = cmd + ' -nc '

    print "Command Line: "+cmd
    #os.system(cmd)
    process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line

def Curvature(inputProc,fel,prof=None,plan=None,horiz=None,unspher=None,ave=None,max=None,min=None,exeDir=None):
    if exeDir is None:
        cmd = 'mpiexec -n '+str(inputProc)+' Curvature'
    else:
        cmd = 'mpiexec -n '+str(inputProc)+ ' ' + exeDir +'\\Curvature'
    if prof is None and plan is None and horiz is None and unspher is None and ave is None and max is None and min is None:
        cmd = cmd +' -fel ' + '"' + fel + '"'
    else:
        cmd = cmd +' -fel ' + '"' + fel + '"'+ ' -out '
    print "Input Pit Filled Elevation Grid: "+fel
    if not prof is None:
        print "Output Profile Curvature Grid: "+prof
        cmd = cmd +' -prof '+'"' + prof + '" '
    if not plan is None:
        print "Output Plan Curvature Grid: "+plan
        cmd = cmd +' -plan '+'"' + plan + '" '
    if not horiz is None:
        print "Output Horizontal Curvature Grid: "+horiz
        cmd = cmd +' -horiz '+'"' + horiz + '" '
    if not unspher is None:
        print "Output Nnsphericity Grid: "+unspher
        cmd = cmd +' -unspher '+'"' + unspher + '" '
    if not ave is None:
        print "Output Average Curvature Grid: "+ave
        cmd = cmd +' -ave '+'"' + ave + '" '
    if not max is None:
        print "Output Maximum Curvature Grid: "+max
        cmd = cmd +' -max '+'"' + max + '" '
    if not min is None:
        print "Output Minimum Curvature Grid: "+min
        cmd = cmd +' -min '+'"' + min + '" '
    print "Command Line: "+cmd
    print "Input Number of Processes: "+str(inputProc)
    #os.system(cmd)
    process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
def SelectTypLocSlpPos(inputConf,outputConf,inputProc,outlog=None,exeDir=None):
    print "Selecting Typical Slope Position Location and Calculating Fuzzy Inference Parameters"
    print "    Input configuration file: "+inputConf
    print "    Output configuration file: "+outputConf
    if outlog is not None:
        print "    Output Log file: "+outlog
    
    if exeDir is None:
        cmd = 'mpiexec -n '+str(inputProc)+' SelectTypLocSlpPos ' + '"' + inputConf + '"' + ' "' + outputConf + '" '
    else:
        cmd = 'mpiexec -n '+str(inputProc)+ ' ' + exeDir +'\\SelectTypLocSlpPos ' + '"' + inputConf + '"' + ' "' + outputConf + '" '
    if outlog is not None:
        cmd = cmd + ' "' + outlog + '" '
    print "Command Line: "+cmd
    print "Input Number of Processes: "+str(inputProc)
    ##os.system(cmd)
    process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
    
def FuzzySlpPosInference(config,inputProc,exeDir=None):
    print "Fuzzy Slope Position Inference"
    print "    Configuration file: "+config
    if exeDir is None:
        cmd = 'mpiexec -n '+str(inputProc)+' FuzzySlpPosInference ' + '"' + config + '"'
    else:
        cmd = 'mpiexec -n '+str(inputProc)+ ' ' + exeDir +'\\FuzzySlpPosInference ' + '"' + config + '"'
    print "Command Line: "+cmd
    print "Input Number of Processes: "+str(inputProc)
    ##os.system(cmd)
    process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
    
def HardenSlpPos(rdg,shd,bks,fts,vly,inputProc,hard,maxsimi,sechard=None,secsimi=None,spsim=None,spsi=None,exeDir=None):
    print "Harden Slope Position Inference"
    print "Ridge Similarity file: "+rdg
    print "Shoulder slope similarity file: "+shd
    print "Back slope similarity file: "+bks
    print "Foot slope similarity file: "+fts
    print "Valley similarity file: "+vly
    print "Hard slope position file: "+hard
    print "Maximum similarity: "+maxsimi
    
    if exeDir is None:
        cmd = 'mpiexec -n '+str(inputProc)+' HardenSlpPos -rdg ' + '"' + rdg + '"' + ' -shd ' + '"' + shd + '"' + ' -bks ' + '"' + bks + '"' + ' -fts ' + '"' + fts + '"' + ' -vly ' + '"' + vly + '"' + ' -maxS ' + '"' + hard + '" ' + '"' + maxsimi + '"'
    else:
        cmd = 'mpiexec -n '+str(inputProc)+ ' ' + exeDir +'\\HardenSlpPos -rdg ' + '"' + rdg + '"' + ' -shd ' + '"' + shd + '"' + ' -bks ' + '"' + bks + '"' + ' -fts ' + '"' + fts + '"' + ' -vly ' + '"' + vly + '"' + ' -maxS ' + '"' + hard + '" ' + '"' + maxsimi + '"'
    if (not sechard is None) and (not secsimi is None):
        print "Second Hard slope position file: "+sechard
        print "Second Maximum similarity: "+secsimi
        cmd = cmd + ' -secS ' + '"' + sechard + '" ' + '"' + secsimi + '"'
        if (not spsim is None) and (not spsi is None):
            print "Slope Position Sequence Index: "+spsi
            cmd = cmd + ' -m '+str(spsim)+' "'+spsi+'"'
        
    print "Command Line: "+cmd
    print "Input Number of Processes: "+str(inputProc)
    ##os.system(cmd)
    process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
    
    
def SimpleCalculator(inputa,inputb,output,operator,inputProc,exeDir=None):
    if exeDir is None:
        cmd = 'mpiexec -n '+str(inputProc)+' SimpleCalculator -in '+ '"' + inputa + '"' + ' "' + inputb + '"' +' -out '+ '"' + output + '"' + ' -op '+ str(operator)
    else:
        cmd = 'mpiexec -n '+str(inputProc)+ ' ' + exeDir +'\\SimpleCalculator -in '+ '"' + inputa + '"' + ' "' + inputb + '"' +' -out '+ '"' + output + '"' + ' -op '+ str(operator)
    print "Command Line: "+cmd
    print "Input Number of Processes: "+str(inputProc)
    ##os.system(cmd)
    process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    for line in process.stdout.readlines():
        print line
        
####           END DEFINITION             ####