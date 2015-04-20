#! /usr/bin/env python
#coding=utf-8

## Test TauDEM functions...
import os
import TauDEM
folder = r'E:\MasterBNU\RillMorphology\20150305\1Preprocess'
DEMsrc = folder + os.sep + 'testdem.tif'
DEMfil = folder + os.sep + 'demfil.tif'
d8dir = folder + os.sep + 'D8Flowdir.tif'
sd8 = folder + os.sep + 'D8Slp.tif'
ad8 = folder + os.sep + 'D8ContArea.tif'
D8sar = folder + os.sep + 'D8SlpAreaRatio.tif'
dinfang = folder + os.sep + 'Dinfang.tif'
dinfslp = folder + os.sep + 'Dinfslp.tif'
adinf = folder + os.sep + 'DinfContArea.tif'
gord = folder + os.sep + 'D8StreamOrd.tif'
plen = folder + os.sep + 'D8MaxUpLen.tif'
tlen = folder + os.sep + 'D8TotalLen.tif'
Avalanche = folder + os.sep + 'Avalanche.tif'
RunoutZ = folder + os.sep + 'RunoutZone.tif'
dfs = folder + os.sep + 'PathDist.tif'
stream = folder + os.sep + 'stream.tif'
DinfDistDown = folder + os.sep + 'DinfDistDown.tif'
DinfDistUp = folder + os.sep + 'DinfDistUp.tif'
DinfUpDep = folder + os.sep + 'DinfUpDependence.tif'
D8DistToStream = folder + os.sep + 'D8DistToStream.tif'
SlpAveDown = folder + os.sep + 'D8SlpAveDown.tif'
D8ExtrVal = folder + os.sep + 'D8ExtrVal.tif'
inputProc = 8
#TauDEM.PitRemove(DEMsrc,inputProc,DEMfil)
#TauDEM.D8FlowDirection(DEMfil,inputProc,d8dir,sd8)
#TauDEM.D8ContributingArea(d8dir,"","","true",inputProc,ad8)
#TauDEM.DinfFlowDirection(DEMfil,inputProc,dinfang,dinfslp)
#TauDEM.DinfContributingArea(dinfang,"","","false",inputProc,adinf)
#TauDEM.GridNetwork(d8dir,inputProc,"","","",gord,plen,tlen)
#TauDEM.DinfAvalancheRunout(DEMfil,dinfang,Avalanche,0.2,8,1,inputProc,RunoutZ,dfs)
#TauDEM.DinfDecayingAccumulation(dinfang,decaymultiplier,weightgrid,shapefile,edgecontamination,inputProc,dsca) not tested yet
#TauDEM.DinfDistDown(dinfang,DEMfil,stream,"Average","Surface","false","",inputProc,DinfDistDown)
#TauDEM.DinfDistUp(dinfang,DEMfil,dinfslp,0.5,"Average","Surface","false",inputProc,DinfDistUp)
#TauDEM.DinfReverseAccumulation(dinfang,weightgrid,inputProc,racc,dmax) not tested yet
#TauDEM.DinfTransLimitAccum(dinfang,supply,transcap,concentration,outletsShp,edgecontamination,inputProc,translimitaccu,tdeposition,concentratept) not tested yet
#TauDEM.DinfUpslopeDependence(dinfang,stream,inputProc,DinfUpDep)
#TauDEM.D8DistanceToStreams(d8dir,stream,1,inputProc,D8DistToStream)
#TauDEM.SlopeAveDown(d8dir,DEMfil,20,inputProc,SlpAveDown)
#TauDEM.SlopeOverAreaRatio(d8dir,ad8,inputProc,D8sar)
#TauDEM.D8ExtremeUpslope(d8dir,,"true","false","",inputProc,D8ExtrVal) Still do not know how to use it
