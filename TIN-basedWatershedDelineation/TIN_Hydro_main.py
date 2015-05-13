#! /usr/bin/env python
#coding=utf-8
# Package   :  TIN-base Watershed Delineation
# 
# Created By:  Liangjun Zhu
# Date From :  5/13/15
# Version   :  
               
# Email     :  zlj@lreis.ac.cn
#

import os,sys
from ShapefileIO import *
from TINcreator import *

if __name__ == '__main__':
    ####     INPUT        ####
    ptsShp = r'E:\research\TIN-based\Points_Elev.shp'
    elevField = "ELEV"
    workspace = r'E:\research\TIN-based'
    ####      END         ####
    
    ####  DEFAULT OUTPUT  ####
    tin_origin_Shp = workspace + os.sep + 'tin_origin.shp'
    ####      END         ####
    
    #### GLOBAL VARIABLES ####
    VertexList = []  ## VertexList stores all the input points' 3D coordinates
    TriangleVertexList = []  ## TriangleList stores all the triangles, each element stores index of vertexes
    TriangleNbrIdxList = [] ## TriangleNbrIdx stores index of triangle's neighbors, if there is not neighbor, set it None
    VertexTriangleList = []  ## VertexTriangleList stores every vertex's adjacent triangles in counterclockwise
    ####      END         ####
    
    ####  TEMP VARIABLES  ####
    pts2DList = []   ## temp list to store 2D coordinates of points
    
    ####      END         ####
    VertexList,pts2DList = ReadPoints(ptsShp,elevField)  ## Read input shapefile of points
    TriangleVertexList,TriangleNbrIdxList,VertexTriangleList = createTIN(VertexList,pts2DList)
    del pts2DList
    WritePolyonShp(TriangleVertexList,VertexList,tin_origin_Shp)
    
    
#    print TriangleVertexList[100]
#    print VertexList[TriangleVertexList[100][0]]
#    print VertexList[TriangleVertexList[100][1]]
#    print VertexList[TriangleVertexList[100][2]]
#    print TriangleNbrIdxList[100]
    