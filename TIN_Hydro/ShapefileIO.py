#! /usr/bin/env python
#coding=utf-8
# Package   :  Read and Write of ESRI Shapefile 
# 
# Created By:  Liangjun Zhu
# Date From :  5/13/15
# Version   :  5/13/15  v0.1-beta first test version.
               
# Email     :  zlj@lreis.ac.cn
#

from osgeo import ogr
from gdalconst import *
import os,sys

def ReadPoints(ptsShp,elevField):
    print "Reading XYZ coordinate of points..."
    if not ptsShp.endswith(".shp"):
        print "Error Input: Please input an shapefile!"
        sys.exit(1)
    ptsData = ogr.Open(ptsShp)  
    if ptsData is None:
        print "Error occurs when trying to open %s!" % ptsShp
        sys.exit(1)
    else:
        VertexList = []
        pts2DList = []
        lyr = ptsData.GetLayerByIndex(0)
        if lyr.GetGeomType() != 1:
            print "Error Input: Please input an point shapefile!"
            sys.exit(1)
        hasElev = False
        for field in lyr.schema:
            if field.GetName() == elevField:
                hasElev = True
        if not hasElev:
            print "Error Input: No field matches %s" % elevField
            sys.exit(1)
        lyr.ResetReading()
        for feat in lyr:
            geom = feat.GetGeometryRef()
            if geom is not None and geom.GetGeometryType() == ogr.wkbPoint:
                x = geom.GetX()
                y = geom.GetY()
            z = float(feat.GetField(feat.GetFieldIndex(elevField)))
            VertexList.append([x,y,z])
            pts2DList.append([x,y])
    ptsData = None
    del ptsData
    return (VertexList,pts2DList)
def WritePointShp(vertexList,zFieldName,outShp):
    print "Write point shapefile: %s" % outShp
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if driver is None:
        print "ESRI Shapefile driver not available."
        sys.exit(1)
    if os.path.exists(outShp):
        driver.DeleteDataSource(outShp)
    ds = driver.CreateDataSource(outShp.rpartition(os.sep)[0])
    if ds is None:
        print "ERROR Output: Creation of output file failed."
        sys.exit(1)
    lyr = ds.CreateLayer(outShp.rpartition(os.sep)[2].split('.')[0],None,ogr.wkbPoint)
    zField = ogr.FieldDefn(zFieldName,ogr.OFTReal)
    lyr.CreateField(zField)
    
    #vertexGeo = ogr.Geometry(ogr.wkbMultiPoint)
    for vertex in vertexList:
        vertexGeo = ogr.Geometry(ogr.wkbPoint)
        vertexGeo.AddPoint(vertex[0],vertex[1])
        featureDefn = lyr.GetLayerDefn()
        vertexFeature = ogr.Feature(featureDefn)
        vertexFeature.SetGeometry(vertexGeo)
        vertexFeature.SetField(zFieldName, vertex[2])
        lyr.CreateFeature(vertexFeature)
        vertexFeature.Destroy()
    ds.Destroy()
    
def WritePolyonShp(vertexIdxList,vertexList,outShp):
    print "Write polygon shapefile: %s" % outShp
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if driver is None:
        print "ESRI Shapefile driver not available."
        sys.exit(1)
    if os.path.exists(outShp):
        driver.DeleteDataSource(outShp)
    ds = driver.CreateDataSource(outShp.rpartition(os.sep)[0])
    if ds is None:
        print "ERROR Output: Creation of output file failed."
        sys.exit(1)
    lyr = ds.CreateLayer(outShp.rpartition(os.sep)[2].split('.')[0],None,ogr.wkbPolygon)
    
    for poly in vertexIdxList:
        polygon = ogr.Geometry(ogr.wkbLinearRing)
        for i in range(len(poly)):
            polygon.AddPoint(vertexList[poly[i]][0],vertexList[poly[i]][1])
        polygon.AddPoint(vertexList[poly[0]][0],vertexList[poly[0]][1])
        temppoly = ogr.Geometry(ogr.wkbPolygon)
        temppoly.AddGeometry(polygon)
        temppolygon = ogr.CreateGeometryFromJson(temppoly.ExportToJson())
        feature = ogr.Feature(lyr.GetLayerDefn())
        feature.SetGeometry(temppolygon)
        lyr.CreateFeature(feature)
        feature.Destroy()
    ds.Destroy()
    
def WriteLineShp(lineList,outShp):
    print "Write line shapefile: %s" % outShp
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if driver is None:
        print "ESRI Shapefile driver not available."
        sys.exit(1)
    if os.path.exists(outShp):
        driver.DeleteDataSource(outShp)
    ds = driver.CreateDataSource(outShp.rpartition(os.sep)[0])
    if ds is None:
        print "ERROR Output: Creation of output file failed."
        sys.exit(1)
    lyr = ds.CreateLayer(outShp.rpartition(os.sep)[2].split('.')[0],None,ogr.wkbLineString)
    
    for l in lineList:
        if len(l) > 1:
            line = ogr.Geometry(ogr.wkbLineString)
            for i in l:
                line.AddPoint(i[0],i[1])
            templine = ogr.CreateGeometryFromJson(line.ExportToJson())
            feature = ogr.Feature(lyr.GetLayerDefn())
            feature.SetGeometry(templine)
            lyr.CreateFeature(feature)
            feature.Destroy()
    ds.Destroy()
    