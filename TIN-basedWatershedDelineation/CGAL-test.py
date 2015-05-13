#! /usr/bin/env python
#coding=utf-8
from CGAL.Triangulations_2 import *
from CGAL.Triangulations_3 import *
from CGAL.Kernel import Point_3
from CGAL.Kernel import Point_2
from osgeo import ogr
from gdalconst import *
import os,sys
from ShapefileIO import *

pts2DList = [[1.1,2.1],[0.8,5],[5.2,1.9],[3.5,4.9],[6,7.4],[0.3,8],[-2,5.0]]
print pts2DList
dt = Delaunay_triangulation_2()

for pt in pts2DList:
    dt.insert(Point_2(pt[0],pt[1]))
#print "number of tin: %d" % dt.number_of_faces()
TriangleList = []
TriangleVertexList = []
TriangleNbrIdxList = []
VertexList = []
TriangleVertexListASC = []
#for v in dt.vertices:
#    VertexList.append([v.point()[0],v.point()[1]])
#print VertexList
for f in dt.faces:
    temppts = []
    tempPtsIdx = []
    for i in range(3):
        tempp = f.vertex(i).point()
        temppts.append([tempp[0],tempp[1]])
        tempPtsIdx.append(pts2DList.index([tempp[0],tempp[1]]))
    TriangleList.append(temppts)
    TriangleVertexList.append(tempPtsIdx)
    TriangleVertexListASC.append(sorted(tempPtsIdx))
print TriangleVertexList
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
print TriangleNbrIdxList
#
#Shp = r'E:\research\TIN-based\testtin.shp'
##WritePolyonShp(TriangleList,Shp)
VertexTriangleList = []
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
print VertexTriangleList
 

#for f in dt.faces:
#    tempNeighborIdx = []
#    for i in range(3):
#        neighborFace = f.neighbor(i)
#        for j in range(3):
#            neighborFace.vertex(j).Point
#        neighborFace
#        tempNeighborIdx.append()
#        
#    print TriangleVertexList.index(tempNeighborIdx)


#ptsShp = r'E:\research\TIN-based\Points_Elev.shp'
#elevField = "ELEV"
#tinShp = r'E:\research\TIN-based\tin.shp'
#tin3DShp = r'E:\research\TIN-based\tin3D.shp'
#if not ptsShp.endswith(".shp"):
#    print "Error Input: Please input an shapefile!"
#    sys.exit(1)
#ptsData = ogr.Open(ptsShp)
#pts3DList = []
#pts2DList = []
#dt = Delaunay_triangulation_2()
#dt3 = Delaunay_triangulation_3()
#if ptsData is None:
#    print "Error occurs when trying to open %s!" % ptsShp
#    sys.exit(1)
#else:
#    lyr = ptsData.GetLayerByIndex(0)
#    if lyr.GetGeomType() != 1:
#        print "Error Input: Please input an point shapefile!"
#        sys.exit(1)
#    hasElev = False
#    for field in lyr.schema:
#        if field.GetName() == elevField:
#            hasElev = True
#    if not hasElev:
#        print "Error Input: No field matches %s" % elevField
#        sys.exit(1)
#    lyr.ResetReading()
#    for feat in lyr:
#        geom = feat.GetGeometryRef()
#        if geom is not None and geom.GetGeometryType() == ogr.wkbPoint:
#            x = geom.GetX()
#            y = geom.GetY()
#        z = float(feat.GetField(feat.GetFieldIndex(elevField)))
#        pts3DList.append(Point_3(x,y,z))
#        pts2DList.append(Point_2(x,y))
#ptsData = None
##print len(ptsList)
#for p in pts2DList:
#    dt.insert(p)
#for p in pts3DList:
#    dt3.insert(p)
#print "2D Triangulation Numbers: %d" % dt.number_of_faces()
#print "3D Triangulation Numbers: %d" % dt3.number_of_facets()
## write shapefile
#driver = ogr.GetDriverByName("ESRI Shapefile")
#if driver is None:
#    print "ESRI Shapefile driver not available."
#    sys.exit(1)
#if os.path.exists(tinShp):
#    driver.DeleteDataSource(tinShp)
#ds = driver.CreateDataSource(tinShp.rpartition(os.sep)[0])
#if ds is None:
#    print "ERROR Output: Creation of output file failed."
#    sys.exit(1)
#lyr = ds.CreateLayer("tin",None,ogr.wkbPolygon)
#
#for f in dt.faces:
#    tempPts = []
#    tri = ogr.Geometry(ogr.wkbLinearRing)
#    for i in range(3):
#        tempp = f.vertex(i).point()
#        tri.AddPoint(tempp[0],tempp[1])
#        tempPts.append(tempp)
#        #print "x=%f,y=%f" % (tempp[0],tempp[1])
#    tri.AddPoint(tempPts[0][0],tempPts[0][1])
#    tinpoly = ogr.Geometry(ogr.wkbPolygon)
#    tinpoly.AddGeometry(tri)
#    tempTri = ogr.CreateGeometryFromJson(tinpoly.ExportToJson())
#    feature = ogr.Feature(lyr.GetLayerDefn())
#    feature.SetGeometry(tempTri)
#    lyr.CreateFeature(feature)
#    feature.Destroy()
#ds.Destroy()
