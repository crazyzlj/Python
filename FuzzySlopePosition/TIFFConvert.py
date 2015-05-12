#! /usr/bin/env python
#coding=utf-8

from Util import *
import TauDEM
rawdem = r'E:\data\DEMs\PleasantValley.tif'
#dem  = r'E:\Anhui\FuzzySlpPosNew\preparedParams\dem_10.tif'
#demfil = r'E:\Anhui\FuzzySlpPosNew\preparedParams\dem_10_fil.tif'
#exeDir = r'E:\coding\Taudem5PCVS2010Soln_512\Taudem5PCVS2010\Release'
#ProfC = r'E:\Anhui\FuzzySlpPosNew\preparedParams\profc_ori.tif'
#HorizC = r'E:\Anhui\FuzzySlpPosNew\preparedParams\horizc_ori.tif'
#SubBasin = r'E:\Anhui\FuzzySlpPosNew\preparedParams\slope.tif'
HorizC_mask = r'E:\Anhui\FuzzySlpPosNew\preparedParams\horizc.tif'
ProfC_mask = r'E:\data\DEMs\pleasantvalley_pre\pvdem.tif'
TIFF2GeoTIFF(rawdem, ProfC_mask)
#inputProc = 8
#TauDEM.pitremove(dem,inputProc,demfil,exeDir)
#TauDEM.Curvature(inputProc,demfil,prof=ProfC,horiz=HorizC,exeDir=exeDir)
#TauDEM.SimpleCalculator(ProfC,SubBasin,ProfC_mask,5,inputProc,exeDir)
#TauDEM.SimpleCalculator(HorizC,SubBasin,HorizC_mask,5,inputProc,exeDir)

