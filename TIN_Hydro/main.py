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
    ptsShp = r'E:\test\lyg\preprocess\lyg_elevs.shp'
    #ptsShp = r'E:\test\TINresult\test.shp'
    elevField = "elev"
    inBorder = "isBorder"   ## if do not want to create concave TIN, set inBorder to be None.
    isOutlet = "isOutlet"   ## This is aimed to invoid the outlet be filled as a sink.
    workspace = r'E:\test\lyg\20160217'
    ####    OPTIONAL      ####
    HANDLE_FLAT_TRIANGLE = True
    HANDLE_PIT = True
    HANDLE_FLAT_EDGE = True
    HANDLE_FALSE_DAM = True
    idwShepardParams = [15,25]   ## refers to http://www.alglib.net/translator/man/manual.cpython.html#sub_idwbuildmodifiedshepard
    multiplier = 3             ## used for false dam detection, refers to detectFalseDam funtion in TINcreator.py
    angleThreshold = 3         ## used in FindChannelNodes
    ####      END         ####
    
    ####  DEFAULT OUTPUT  ####
    preprocessing_pts = workspace + os.sep + 'new_point.shp'
    tin_origin_Shp = workspace + os.sep + 'new_tin.shp'
    steepestpath_Shp = workspace + os.sep + 'steepest_descent_path.shp'
    channelpath_Shp = workspace + os.sep + 'channel_path.shp'
    ####      END         ####
    
    #### GLOBAL VARIABLES ####
    VertexList = []          ## VertexList stores 3D coordinates (x,y,z) of all the input points
    TriangleVertexList = []  ## TriangleList stores all the triangles, each element stores index of vertexes
    TriangleNbrIdxList = []  ## TriangleNbrIdx stores index of triangle's neighbors, if there is not neighbor, set it None
    VertexTriangleList = []  ## VertexTriangleList stores every vertex's adjacent triangles in counterclockwise
    ####      END         ####
    
    ####  TEMP VARIABLES  ####
    pts2DList = []            ## temp list to store 2D coordinates of points
    ptsInBorderIdx = []       ## index of points that line in the boundary
    SWITCH = [HANDLE_FLAT_TRIANGLE,HANDLE_PIT,HANDLE_FLAT_EDGE,HANDLE_FALSE_DAM]
    ####      END         ####
    
    ####  INTERMEDIATE    ####
    SteepestPathList = []     ## Each steepest path is consist with serveral vertexes from the centriod of triangle
    SteepestPathVertexIdx = []## Corresponding to SteepestPathList, it stores the index, if the vertex is not node, assigned -1
    ChannelNodesDict = {}     ## Dictionary of channel nodes, include downstream and upstreams
    ####      END         ####
    
    ####  MAIN FUNCTIONS  ####
    ## 1. Read input shapefile of points
    VertexList,pts2DList, ptsInBorderIdx, outletIdx = ReadPoints(ptsShp, elevField, inBorder, isOutlet)
    #print ptsInBorderIdx,len(ptsInBorderIdx)
    ## 2. Construct hydrological TIN
    dtObject = createTIN(VertexList,pts2DList)
    dtObject, pts2DList, VertexList = preprocessTIN(dtObject, VertexList, pts2DList, idwShepardParams,multiplier,SWITCH, ptsInBorderIdx, outletIdx)
    TriangleVertexList,TriangleNbrIdxList,VertexTriangleList = TINstruct(dtObject, pts2DList, ptsInBorderIdx)
    print len(TriangleNbrIdxList), TriangleNbrIdxList
    print len(VertexTriangleList), VertexTriangleList
    WritePointShp(VertexList,elevField,preprocessing_pts)
    WritePolyonShp(TriangleVertexList,VertexList,tin_origin_Shp)
    #WritePointShp(VertexList,elevField,workspace + os.sep + 'new_points_origin.shp')
    #WritePolyonShp(TriangleVertexList,VertexList,workspace + os.sep + 'new_tin_origin.shp')
    ## 3. Calculate path of steepest decent
    breakLinePts = []
    SteepestPathList,SteepestPathVertexIdx, breakLinePts = SteepestDescentPath(TriangleVertexList, VertexList, VertexTriangleList, breakLinePts)
    WriteLineShp(SteepestPathList,steepestpath_Shp)
    #WriteLineShp(SteepestPathList,workspace + os.sep + 'new_steepest_origin.shp')
    # while len(breakLinePts) > 0:
    #     breakLinePtsAdd = []
    #     for pt in breakLinePts:
    #         ptIdx = breakLinePts.index(pt)
    #         if pt not in breakLinePtsAdd:
    #             breakLinePtsAdd.append(pt)
    #     #print breakLinePtsAdd
    #     ## add points to VertexList
    #     print "---- %d points will be added as break lines" % len(breakLinePtsAdd)
    #     #print len(VertexList)
    #
    #     for pts in breakLinePtsAdd:
    #         if pts not in VertexList:
    #             VertexList.append(pts)
    #             pts2DList.append([pts[0], pts[1]])
    #     #print len(VertexList)
    #     ## run preprocessing again
    #     dtObject = reCreateTIN(dtObject, breakLinePtsAdd)
    #     dtObject, pts2DList, VertexList = preprocessTIN(dtObject, VertexList, pts2DList, idwShepardParams,multiplier,[False,False,True,True], ptsInBorderIdx, outletIdx)
    #     TriangleVertexList,TriangleNbrIdxList,VertexTriangleList = TINstruct(dtObject,pts2DList, ptsInBorderIdx)
    #     #print len(TriangleNbrIdxList), TriangleNbrIdxList
    #     #print len(VertexTriangleList), VertexTriangleList
    #     #WritePointShp(VertexList,elevField,preprocessing_pts)
    #     #WritePolyonShp(TriangleVertexList,VertexList,tin_origin_Shp)
    #     breakLinePts = []
    #     SteepestPathList,SteepestPathVertexIdx, breakLinePts = SteepestDescentPath(TriangleVertexList, VertexList, VertexTriangleList, breakLinePts)

    ## 4. Channel nodes and channel flow lines
    ChannelNodesDict, channelList = FindChannelNodes(TriangleVertexList, VertexTriangleList, VertexList, angleThreshold, outletIdx)
    channelCoors = []
    channelFields = [['streamID','strahler']]
    for curChannelList in channelList:
        for cha in curChannelList:
            channelCoors.append(cha[5])
            channelFields.append([cha[0],cha[1]])
    print ChannelNodesDict
    #print channelCoors
    #print channelFields
    WriteLineShp(channelCoors,channelpath_Shp,channelFields)

    ## 5. Delineation of source area

    ####      END         ####