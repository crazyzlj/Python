#! /usr/bin/env python
#coding=utf-8
# Program: Fuzzy slope position extraction based on D-8 and D-infinity algorithms
# 
# Created By:  Liangjun Zhu
# Date From :  3/20/15
# Version   :  5/7/15  v0.1-beta first released version for test.
               
# Email     :  zlj@lreis.ac.cn
#
import os,sys
import TauDEM
from Nomenclature import *
from Config import *
from Util import *
from PreProcessing import PreProcessing
from SelectTypLoc import SelectTypLoc
from FuzzySlpPosInference import FuzzySlpPosInference

if __name__ == '__main__':
    ## Stage 1: Preprocessing if needed
    if preprocess:
        PreProcessing(FlowModel)
    ## Stage 2: Selection of Typical Locations and Calculation of Inference Parameters
    SelectTypLoc()
    ## Stage 3: Fuzzy slope position inference
    FuzzySlpPosInference()