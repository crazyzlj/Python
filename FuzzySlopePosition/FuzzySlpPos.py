#! /usr/bin/env python
#coding=utf-8
# Program: Fuzzy slope position extraction based on D-8 and D-infinity algorithms
# 
# Created By:  Liangjun Zhu
# Date From :  3/20/15
# Email     :  zlj@lreis.ac.cn
#
import os,sys
import TauDEM
from Util import *
from PreProcessing import PreProcessing
from SelectTypLoc import SelectTypLoc
from FuzzySlpPosInference import FuzzySlpPosInference
from Nomenclature import *
from Config import *

if __name__ == '__main__':
    ## Stage 1: Preprocessing from DEMsrc
    #PreProcessing(FlowModel)
    ## Stage 2: Selection of Typical Locations
    SelectTypLoc()
    ## Stage 3: Fuzzy slope position inference
    #FuzzySlpPosInference()