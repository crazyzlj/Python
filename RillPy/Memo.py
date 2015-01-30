#! /usr/bin/env python
#coding=utf-8
UpStreamShp = RillExtDir + os.sep + "UpStream.shp"
arcpy.CreateFeatureclass_management(RillExtDir, "UpStream.shp", "POLYLINE", "", "DISABLED", "DISABLED", "")
arcpy.Append_management(["north.shp", "south.shp", "east.shp", "west.shp"], UpStreamShp, "NO_TEST","","")
