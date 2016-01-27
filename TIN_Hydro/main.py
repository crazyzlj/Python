#! /usr/bin/env python
#coding=utf-8
# Package   :  TIN-based Hydro-Net Extraction
# 
# Created By:  Liangjun Zhu
# Date From :  5/13/15
# Version   :  
               
# Email     :  zlj@lreis.ac.cn
#

import os,sys
from ShapefileIO import *
from HydroTIN import *

if __name__ == '__main__':
    ####     INPUT        ####
    ptsShp = r'E:\github-zlj\Python\TIN-Hydro\data\test.shp'
    #elevField = "ELEV"
    elevField = "Z"
    workspace = r'E:\github-zlj\Python\TIN-Hydro\data\result'
    ####    OPTIONAL      ####
    HANDLE_FLAT_TRIANGLE = False
    HANDLE_PIT = False
    HANDLE_FLAT_EDGE = False
    HANDLE_FALSE_DAM = False
    idwShepardParams = [15,25]   ## refers to http://www.alglib.net/translator/man/manual.cpython.html#sub_idwbuildmodifiedshepard
    multiplier = 2.0             ## used for false dam detection, refers to detectFalseDam funtion in TINcreator.py
    angleThreshold = 10.0         ## used in FindChannelNodes
    ####      END         ####
    
    ####  DEFAULT OUTPUT  ####
    preprocessing_pts = workspace + os.sep + 'new_point.shp'
    tin_origin_Shp = workspace + os.sep + 'new_tin.shp'
    steepestpath_Shp = workspace + os.sep + 'steepestpath.shp'
    channelpath_Shp = workspace + os.sep + 'channelpath.shp'
    ####      END         ####
    
    #### GLOBAL VARIABLES ####
    VertexList = []          ## VertexList stores 3D coordinates (x,y,z) of all the input points
    TriangleVertexList = []  ## TriangleList stores all the triangles, each element stores index of vertexes
    TriangleNbrIdxList = []  ## TriangleNbrIdx stores index of triangle's neighbors, if there is not neighbor, set it None
    VertexTriangleList = []  ## VertexTriangleList stores every vertex's adjacent triangles in counterclockwise
    ####      END         ####
    
    ####  TEMP VARIABLES  ####
    pts2DList = []            ## temp list to store 2D coordinates of points
    SWITCH = [HANDLE_FLAT_TRIANGLE,HANDLE_PIT,HANDLE_FLAT_EDGE,HANDLE_FALSE_DAM]
    ####      END         ####
    
    ####  INTERMEDIATE    ####
    SteepestPathList = []     ## Each steepest path is consist with serveral vertexes from the centriod of triangle
    SteepestPathVertexIdx = []## Corresponding to SteepestPathList, it stores the index, if the vertex is not node, assigned -1
    ChannelNodesDict = {}     ## Dictionary of channel nodes, include downstream and upstreams
    ####      END         ####
    
    ####  MAIN FUNCTIONS  ####
    ## 1. Read input shapefile of points
    VertexList,pts2DList = ReadPoints(ptsShp,elevField)  
    ## 2. Construct hydrological TIN 
    TriangleVertexList,TriangleNbrIdxList,VertexTriangleList,VertexList = createTIN(VertexList,pts2DList,idwShepardParams,multiplier,SWITCH)
    ## 3. Calculate path of steepest decent
    SteepestPathList,SteepestPathVertexIdx = SteepestDescentPath(TriangleVertexList, VertexList, VertexTriangleList)
#    for i in range(len(SteepestPathList)):
#        print SteepestPathVertexIdx[i]
    ## 4. Channel nodes and channel flow lines
    ChannelNodesDict, channelList = FindChannelNodes(TriangleVertexList, VertexTriangleList, VertexList, angleThreshold)
#    for cha in channelList:
#        print cha
#    print ChannelNodesDict
    ##    Write outputs
    WritePointShp(VertexList,elevField,preprocessing_pts)
    WritePolyonShp(TriangleVertexList,VertexList,tin_origin_Shp)
    WriteLineShp(SteepestPathList,steepestpath_Shp)
    WriteLineShp(channelList,channelpath_Shp)
    #del pts2DList
   
    ####      END         ####