#! /usr/bin/env python
#coding=utf-8
## @Generate ESRI Shapefile from XYZ point text file.
## @author: Liang-Jun Zhu
## @Date: 2016-6-17
## @Email: zlj@lreis.ac.cn
#
import os,sys,time
from osgeo import ogr
def currentPath():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
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
def progress(percent):
    bar_length=20
    hashes = '#' * int(percent/100.0 * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("    Handling: [%s] %.1f%%\n"%(hashes + spaces, percent))
    sys.stdout.flush()
    #time.sleep(1)

def GeneratorPointShp(txtFile,outShp):
    start = time.time()
    lineCount = 0
    thefile = open(txtFile,'rb')
    while True:
        buffer = thefile.read(1024 * 8192)
        if not buffer:
            break
        lineCount += buffer.count('\n')
    thefile.close()
    print "There are %d points to be processed." % lineCount

    ## Create shapefile
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
    xField = ogr.FieldDefn("X",ogr.OFTReal)
    yField = ogr.FieldDefn("Y",ogr.OFTReal)
    zField = ogr.FieldDefn("Z",ogr.OFTReal)
    lyr.CreateField(xField)
    lyr.CreateField(yField)
    lyr.CreateField(zField)

    count = 0
    with open(txtFile) as f:
        for line in f:
            pts = line.split(',')
            if pts !=[] and len(pts) == 4:
                x = float(pts[1])
                y = float(pts[2])
                z = float(pts[3])
                #print x,y,z

                vertexGeo = ogr.Geometry(ogr.wkbPoint)
                vertexGeo.AddPoint(x,y)
                featureDefn = lyr.GetLayerDefn()
                vertexFeature = ogr.Feature(featureDefn)
                vertexFeature.SetGeometry(vertexGeo)
                vertexFeature.SetField("X", x)
                vertexFeature.SetField("Y", y)
                vertexFeature.SetField("Z", z)
                lyr.CreateFeature(vertexFeature)
                vertexFeature.Destroy()

                count += 1
                perc = float(count)/float(lineCount) * 100
                if(perc%5. == 0.):
                    progress(perc)
    ds.Destroy()
    end = time.time()
    secs = end - start
    mins = secs / 60.
    print "\nAll done, costs %.1f minutes!" % mins
if __name__ == '__main__':
    currFolder = currentPath()
    currFolder = r'e:/test/test'
    filename = "xyz.txt"
    outfilename = "test.shp"

    xyzTxtFile = currFolder + os.sep + filename
    shpFile = currFolder + os.sep + outfilename
    GeneratorPointShp(xyzTxtFile, shpFile)