#! /usr/bin/env python
#coding=utf-8
# Package   :  Constructure TIN based on CGAL-python packages 
# 
# Created By:  Liangjun Zhu
# Date From :  5/13/15
# Version   :  
               
# Email     :  zlj@lreis.ac.cn
#
from CGAL.Triangulations_2 import *
from CGAL.Kernel import Point_2
import os,sys

def createTIN(pts,pts2DList):
    dt = Delaunay_triangulation_2()
    
    VertexList = []
    TriangleVertexList = []
    TriangleNbrIdxList = []
    VertexTriangleList = []
    print "Construct Delaunay Triangulated Irregular Network... "
    for p in pts:
        dt.insert(Point_2(p[0],p[1]))
    print "Construct Triangle Vertexes Index List..."
    for f in dt.faces:
        tempPtsIdx = []
        for i in range(3):
            tempp = f.vertex(i).point()
            tempPtsIdx.append(pts2DList.index([tempp[0],tempp[1]]))
        TriangleVertexList.append(tempPtsIdx)
    print "Construct Neighbor of Triangle Index List..."
    for f in dt.faces:
        NbrFaceIdx = []
        for i in range(3):
            tempFaceIdx = []
            if dt.is_infinite(f.neighbor(i)) == False:
                for j in range(3):
                    tempFaceIdx.append(pts2DList.index([f.neighbor(i).vertex(j).point()[0],f.neighbor(i).vertex(j).point()[1]]))
                NbrFaceIdx.append(TriangleVertexList.index(tempFaceIdx))
            else:
                NbrFaceIdx.append(None)
        value = NbrFaceIdx.pop(2)
        NbrFaceIdx.insert(0,value)
        TriangleNbrIdxList.append(NbrFaceIdx)
    #print TriangleNbrIdxList
    print "Construct Vertex Adjacent Triangles Index List..."    
    for v in dt.vertices:
        #print v.point()
        cir_faces = dt.incident_faces(v)
        finites_faces = []
        f1 = cir_faces.next()
        if dt.is_infinite(f1) == False:
            finites_faces.append(f1)
        for f in cir_faces:
            if f == f1:
                break
            else:
                if dt.is_infinite(f) == False:
                    finites_faces.append(f)
        finites_faces_idx = []
        for f in finites_faces:
            tempFaceIdx = []
            for i in range(3):
                tempFaceIdx.append(pts2DList.index([f.vertex(i).point()[0],f.vertex(i).point()[1]]))
            finites_faces_idx.append(TriangleVertexList.index(tempFaceIdx))
        VertexTriangleList.append(finites_faces_idx)
    #print VertexTriangleList
    
    return (TriangleVertexList,TriangleNbrIdxList,VertexTriangleList)
    