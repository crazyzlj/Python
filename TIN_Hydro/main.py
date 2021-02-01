# coding=utf-8
# Package   :  TIN-based Hydrological Analysis
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
    elevField = "elev"
    inBorder = "isBorder"   ## if do not want to create concave TIN, set inBorder to be None.
    isOutlet = "isOutlet"   ## This is aimed to avoid the outlet be filled as a sink.
    workspace = r'E:\test\lyg\20160218'
    ####    OPTIONAL      ####
    HANDLE_FLAT_TRIANGLE = True
    HANDLE_PIT = True
    HANDLE_FLAT_EDGE = True
    HANDLE_FALSE_DAM = True
    idwShepardParams = [15,25] ## refers to http://www.alglib.net/translator/man/manual.cpython.html#sub_idwbuildmodifiedshepard
    multiplier = 3             ## used for false dam detection, refers to detectFalseDam funtion in TINcreator.py
    angleThreshold = 0         ## used in FindChannelNodes
    ####      END         ####
    
    ####  DEFAULT OUTPUT  ####
    preprocessing_pts = workspace + os.sep + 'points_for_channel.shp'
    tin_origin_Shp = workspace + os.sep + 'tin_for_channel.shp'
    steepestDownPath_Shp = workspace + os.sep + 'steepest_descent_path.shp'
    channelpath_Shp = workspace + os.sep + 'channel_path.shp'
    steepestUpPath_Shp = workspace + os.sep + 'steepest_ascent_path.shp'
    added_node_Shp = workspace + os.sep + 'added_node_for_subbasin.shp'
    pts_update_Shp = workspace + os.sep + 'points_for_watershed.shp'
    tin_update_Shp = workspace + os.sep + 'tin_for_watershed.shp'
    newSteepestDownPath_Shp = workspace + os.sep + 'new_steepest_descent_path.shp'
    subbasin_Shp = workspace + os.sep + 'subbasin.shp'
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
    SteepestDescentPathList = []     ## Each steepest path is consist with serveral vertexes from the centriod of triangle
    SteepestDescentPathVertexIdx = []## Corresponding to SteepestPathList, it stores the index, if the vertex is not node, assigned -1
    ChannelNodesDict = {}     ## Dictionary of channel nodes, include downstream and upstreams
    ####      END         ####
    
    ####  MAIN PROCEDURES  ####
    ## 1. Read input shapefile of points
    VertexList,pts2DList, ptsInBorderIdx, outletIdx = ReadPoints(ptsShp, elevField, inBorder, isOutlet)
    #print ptsInBorderIdx,len(ptsInBorderIdx)

    ## 2. Construct hydrological TIN
    dtObject = createTIN(VertexList,pts2DList)
    dtObject, pts2DList, VertexList = preprocessTIN(dtObject, VertexList, pts2DList, idwShepardParams,multiplier,SWITCH, ptsInBorderIdx, outletIdx)
    TriangleVertexList,TriangleNbrIdxList,VertexTriangleList = TINstruct(dtObject, pts2DList, ptsInBorderIdx)
    #print len(TriangleNbrIdxList), TriangleNbrIdxList
    #print len(VertexTriangleList), VertexTriangleList
    WritePointShp(VertexList,elevField,preprocessing_pts)
    WritePolyonShp(TriangleVertexList,VertexList,tin_origin_Shp)

    ## 3. Trace steepest decent paths
    SteepestDescentPathList, SteepestDescentPathVertexIdx, breakLinePts = SteepestDescentPath(TriangleVertexList, VertexList, VertexTriangleList)
    WriteLineShp(SteepestDescentPathList, steepestDownPath_Shp)

    ## 4. Channel nodes and channel flow lines
    ChannelNodesDict, channelList, delimitPts, channelNodes = FindChannelNodes(TriangleVertexList, VertexTriangleList, VertexList, angleThreshold, outletIdx)
    #print delimitPts ## index of delimiting nodes with upstream and downstream nodes
    #print channelNodes
    #print ChannelNodesDict
    #print channelCoors
    #print channelFields
    channelCoors, channelFields = WriteChannelShp(channelList, channelpath_Shp)

    ## 5. Delineation of source area
    SteepestAscentPathList,SteepestAscentPathVertexIdx, breakLinePts, breakPtsInBorderIdx = SteepestAscentPath(delimitPts, channelNodes, TriangleVertexList, VertexList, VertexTriangleList, ptsInBorderIdx)
    # print len(breakLinePts)
    # print len(breakPtsInBorderIdx)
    WritePointShp(breakLinePts,elevField,added_node_Shp)
    WriteLineShp(SteepestAscentPathList, steepestUpPath_Shp)
    dtUpdate, newPts2DList, newVertexList, newPtsInBorderIdx = SubdivisionTIN(dtObject, breakLinePts, pts2DList, VertexList, ptsInBorderIdx, breakPtsInBorderIdx)
    dtUpdate, newPts2DList, newVertexList = preprocessTIN(dtUpdate, newVertexList, newPts2DList, idwShepardParams,multiplier,[False,False,False,False], newPtsInBorderIdx, outletIdx)
    newTriangleVertexList,newTriangleNbrIdxList,newVertexTriangleList = TINstruct(dtUpdate,newPts2DList, newPtsInBorderIdx)
    WritePointShp(newVertexList, elevField, pts_update_Shp)
    WritePolyonShp(newTriangleVertexList,newVertexList,tin_update_Shp)

    ## 6. Grouping triangles to subbasins
    subbasinInfo, newSteepestDescentPathList = GroupTriangles(channelCoors, channelFields, newTriangleVertexList, newVertexList, newVertexTriangleList)
    WriteLineShp(newSteepestDescentPathList, newSteepestDownPath_Shp)
    WriteSubbasin(subbasinInfo, newVertexList, subbasin_Shp)
    ####      END         ####