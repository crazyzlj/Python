# coding=gbk
# Package   :  Read and Write of ESRI Shapefile 
# 
# Created By:  Liangjun Zhu
# Date From :  5/13/15
# Version   :  5/13/15  v0.1-beta first test version.
               
# Email     :  zlj@lreis.ac.cn
#

from osgeo import ogr,gdal
from gdalconst import *
import os,sys,codecs

def ReadPoints(ptsShp, elevField, inBorderField = None, isOutlet = None):
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
        ptsInBorderIdx = []
        outletIdx = []
        lyr = ptsData.GetLayerByIndex(0)
        if lyr.GetGeomType() != 1:
            print "Error Input: Please input an point shapefile!"
            sys.exit(1)
        hasElev = False
        hasInBorder = False
        hasOutlet = False
        for field in lyr.schema:
            if field.GetName() == elevField:
                hasElev = True
            if inBorderField is not None and field.GetName() == inBorderField:
                hasInBorder = True
            if isOutlet is not None and field.GetName() == isOutlet:
                hasOutlet = True

        if not hasElev:
            print "Error Input: No field matches %s" % elevField
            sys.exit(1)
        if inBorderField is not None and hasInBorder is False:
            print "Error Input: No field matches %s" % inBorderField
            sys.exit(1)
        if isOutlet is not None and hasOutlet is False:
            print "Error Input: No field matches %s" % isOutlet
            sys.exit(1)

        lyr.ResetReading()
        for feat in lyr:
            geom = feat.GetGeometryRef()
            if geom is not None and geom.GetGeometryType() == ogr.wkbPoint:
                x = geom.GetX()
                y = geom.GetY()
                z = float(feat.GetField(feat.GetFieldIndex(elevField)))
                #print feat.GetField(feat.GetFieldIndex(inBorderField))
                VertexList.append([x,y,z])
                pts2DList.append([x,y])
                if hasInBorder:
                    if feat.GetField(feat.GetFieldIndex(inBorderField)) == 1.0:
                        ptsInBorderIdx.append(VertexList.index([x,y,z]))
                if hasOutlet:
                    if feat.GetField(feat.GetFieldIndex(isOutlet)) == 1.0:
                        outletIdx.append(VertexList.index([x,y,z]))
    ptsData = None
    del ptsData
    if hasInBorder:
        if hasOutlet:
            return (VertexList, pts2DList, ptsInBorderIdx, outletIdx)
        else:
            return (VertexList, pts2DList, ptsInBorderIdx, None)
    else:
        if hasOutlet:
            return (VertexList, pts2DList, None, outletIdx)
        else:
            return (VertexList, pts2DList, None, None)
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
    
def WritePolyonShp(vertexIdxList,vertexList,outShp, polyFieldsList = None):
    print "Write polygon shapefile: %s" % outShp
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if driver is None:
        print "ESRI Shapefile driver not available."
        sys.exit(1)
    if os.path.exists(outShp):
        driver.DeleteDataSource(outShp)
    fieldName = []
    fieldNameIdx = 0
    if polyFieldsList is not None:
        if len(vertexIdxList) != len(polyFieldsList):
            if len(vertexIdxList) + 1 == len(polyFieldsList):
                fieldName = polyFieldsList[0]
                fieldNameIdx = 1
            else:
                sys.exit(1)
        else:
            fieldLength = len(polyFieldsList[0])
            for i in range(fieldLength):
                name = 'PolyName'+str(i)
                fieldName.append(name)
            fieldNameIdx = 0
    else:
        fieldName = ['PolyName']
        fieldNameIdx = 0
    ds = driver.CreateDataSource(outShp.rpartition(os.sep)[0])
    if ds is None:
        print "ERROR Output: Creation of output file failed."
        sys.exit(1)
    lyr = ds.CreateLayer(outShp.rpartition(os.sep)[2].split('.')[0],None,ogr.wkbPolygon)
     ## create fields
    for fld in fieldName:
        nameField = ogr.FieldDefn(fld, ogr.OFTString)
        lyr.CreateField(nameField)
    for poly in vertexIdxList:
        idx = vertexIdxList.index(poly)
        polygon = ogr.Geometry(ogr.wkbLinearRing)
        if poly != []:
            for i in range(len(poly)):
                polygon.AddPoint(vertexList[poly[i]][0],vertexList[poly[i]][1])
            polygon.AddPoint(vertexList[poly[0]][0],vertexList[poly[0]][1])
            temppoly = ogr.Geometry(ogr.wkbPolygon)
            temppoly.AddGeometry(polygon)
            temppolygon = ogr.CreateGeometryFromJson(temppoly.ExportToJson())
            feature = ogr.Feature(lyr.GetLayerDefn())
            feature.SetGeometry(temppolygon)
            for fld in fieldName:
                    idx2 = fieldName.index(fld)
                    if polyFieldsList is not None:
                        if fieldNameIdx == 1:
                            fieldValue = polyFieldsList[idx + 1][idx2]
                        else:
                            fieldValue = polyFieldsList[idx][idx2]
                    else:
                        fieldValue = ' '
                    #print fieldValue
                    feature.SetField(fld, fieldValue)
            lyr.CreateFeature(feature)
            feature.Destroy()
    ds.Destroy()
    
def WriteLineShp(lineList, outShp, lineFieldsList = None):
    print "Write line shapefile: %s" % outShp
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8","NO")  ## support for path in Chinese
    gdal.SetConfigOption("SHAPE_ENCODING","")           ## suppoert for field in Chinese
    ogr.RegisterAll()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if driver is None:
        print "ESRI Shapefile driver not available."
        sys.exit(1)
    if os.path.exists(outShp):
        driver.DeleteDataSource(outShp)

    fieldName = []
    fieldNameIdx = 0
    if lineFieldsList is not None:
        if len(lineList) != len(lineFieldsList):
            if len(lineList) + 1 == len(lineFieldsList):
                fieldName = lineFieldsList[0]
                fieldNameIdx = 1
            else:
                sys.exit(1)
        else:
            fieldLength = len(lineFieldsList[0])
            for i in range(fieldLength):
                name = 'lineName'+str(i)
                fieldName.append(name)
            fieldNameIdx = 0
    else:
        fieldName = ['LineName']
        fieldNameIdx = 0
    ds = driver.CreateDataSource(outShp.rpartition(os.sep)[0])
    if ds is None:
        print "ERROR Output: Creation of output file failed."
        sys.exit(1)
    lyr = ds.CreateLayer(outShp.rpartition(os.sep)[2].split('.')[0],None,ogr.wkbLineString)
    ## create fields
    for fld in fieldName:
        nameField = ogr.FieldDefn(fld, ogr.OFTString)
        lyr.CreateField(nameField)
    for l in lineList:
        idx = lineList.index(l)
        if len(l) > 1:
            line = ogr.Geometry(ogr.wkbLineString)
            for i in l:
                line.AddPoint(i[0],i[1])
            templine = ogr.CreateGeometryFromJson(line.ExportToJson())
            feature = ogr.Feature(lyr.GetLayerDefn())
            feature.SetGeometry(templine)
            for fld in fieldName:
                idx2 = fieldName.index(fld)
                if lineFieldsList is not None:
                    if fieldNameIdx == 1:
                        fieldValue = lineFieldsList[idx + 1][idx2]
                    else:
                        fieldValue = lineFieldsList[idx][idx2]
                else:
                    fieldValue = ' '
                #print fieldValue
                feature.SetField(fld, fieldValue)
            lyr.CreateFeature(feature)
            feature.Destroy()
    ds.Destroy()
def WriteChannelShp(channelList, filepath):
    channelCoors = []
    channelFields = [['streamID','strahler']]
    for curChannelList in channelList:
        for cha in curChannelList:
            channelCoors.append(cha[5])
            channelFields.append([cha[0],cha[1]])
    WriteLineShp(channelCoors,filepath,channelFields)
    return (channelCoors, channelFields)
def WriteSubbasin(subbasinInfo, vertexList, filepath):
    ## subbasinInfo format: {subbasinID: [[vertex index of every triangles]...]}
    ## for example: {[0:[[1,2,5],[2,5,8]...],...}
    subbasinVertexIdx = []
    subbasinIDs = [['subbasinID']]
    for subbasin in subbasinInfo.keys():
        for triangle in subbasinInfo.get(subbasin):
            subbasinIDs.append([subbasin])
            subbasinVertexIdx.append(triangle)
    WritePolyonShp(subbasinVertexIdx, vertexList, filepath, subbasinIDs)


## Debug code
if __name__ == '__main__':
    #lines = [[[2,3],[4,5],[7,7]],[[12,3],[4,15],[7.8,7]],[[2,13],[14,5],[27,7]]]
    #linesName = [['line1','1'],['line2','12'],['line3','22']]
    #lines = [[[564735.0, 3830830.0, 1211.25500488], [565193.6396103068, 3830220.0, 1198.71704102], [565765.0, 3829680.0, 1195.00097656], [565945.0, 3829410.0, 1190.0]], [[563730.0, 3829745.0, 1433.50805664], [563995.0, 3830130.0, 1381.54602051], [564429.2206891857, 3830455.748818954, 1259.2590332], [564735.0, 3830830.0, 1211.25500488]], [[564417.3223304703, 3831097.67766953, 1214.96398926], [564735.0, 3830830.0, 1211.25500488]], [[563132.5735931288, 3831670.0, 1244.45495605], [563862.9289321881, 3831420.0, 1228.2130127], [564417.3223304703, 3831097.67766953, 1214.96398926]], [[561825.0, 3832530.0, 1275.48706055], [562263.8908729652, 3832181.109127035, 1274.91699219], [562635.0, 3831870.0, 1261.18603516], [563132.5735931288, 3831670.0, 1244.45495605]], [[562161.8688786502, 3833838.5306034745, 1443.22497559], [562105.0, 3833450.0, 1384.99401855], [561915.3553390594, 3833010.355339059, 1324.83605957], [561825.0, 3832530.0, 1275.48706055]], [[561451.4569534351, 3834326.93880206, 1655.70300293], [562037.5467917377, 3834309.1785039296, 1577.0579834], [562161.8688786502, 3833838.5306034745, 1443.22497559]], [[562410.5130524755, 3834397.9799945815, 1638.39599609], [562161.8688786502, 3833838.5306034745, 1443.22497559]], [[561125.0, 3832700.0, 1289.95898438], [561456.8198051534, 3832588.180194847, 1283.73999023], [561825.0, 3832530.0, 1275.48706055]], [[560810.8578643763, 3832235.857864376, 1332.89501953], [561125.0, 3832700.0, 1289.95898438]], [[561155.0733063644, 3831239.2398615256, 1493.02099609], [560810.8578643763, 3832235.857864376, 1332.89501953]], [[560304.6602810435, 3831416.426585843, 1460.4420166], [560505.0, 3831800.0, 1399.62902832], [560810.8578643763, 3832235.857864376, 1332.89501953]], [[560180.0, 3830945.0, 1574.4630127], [560304.6602810435, 3831416.426585843, 1460.4420166]], [[559790.0, 3830985.0, 1585.28894043], [560304.6602810435, 3831416.426585843, 1460.4420166]], [[560575.0, 3833050.0, 1304.41101074], [560832.9289321881, 3832860.0, 1299.24597168], [561125.0, 3832700.0, 1289.95898438]], [[560805.0, 3834120.0, 1420.62402344], [560575.0, 3833050.0, 1304.41101074]], [[561282.7341211966, 3834682.1447646674, 1555.85803223], [561007.4495001757, 3834282.538056734, 1455.66003418], [560805.0, 3834120.0, 1420.62402344]], [[561420.0, 3835085.0, 1758.93005371], [561282.7341211966, 3834682.1447646674, 1555.85803223]], [[561760.0, 3834815.0, 1781.44299316], [561282.7341211966, 3834682.1447646674, 1555.85803223]], [[560741.04502822, 3834646.6241684067, 1502.06494141], [560805.0, 3834120.0, 1420.62402344]], [[560860.0, 3835255.0, 1775.2989502], [560741.04502822, 3834646.6241684067, 1502.06494141]], [[560439.1199600035, 3834868.6278950367, 1584.47802734], [560741.04502822, 3834646.6241684067, 1502.06494141]], [[559920.0, 3835325.0, 1801.9699707], [560439.1199600035, 3834868.6278950367, 1584.47802734]], [[560400.0, 3835425.0, 1790.9329834], [560439.1199600035, 3834868.6278950367, 1584.47802734]], [[559947.0710678119, 3833220.0, 1322.34301758], [560575.0, 3833050.0, 1304.41101074]], [[559305.0, 3833380.0, 1334.52600098], [559947.0710678119, 3833220.0, 1322.34301758]], [[558995.0, 3832480.0, 1415.69396973], [559305.0, 3833380.0, 1334.52600098]], [[558786.1547908961, 3831833.793591907, 1523.96203613], [558995.0, 3832480.0, 1415.69396973]], [[558173.424505398, 3832109.0782129276, 1534.7869873], [558786.1547908961, 3831833.793591907, 1523.96203613]], [[558820.0, 3831265.0, 1633.85900879], [558786.1547908961, 3831833.793591907, 1523.96203613]], [[559336.7240329378, 3832011.3965732106, 1508.97595215], [558995.0, 3832480.0, 1415.69396973]], [[558390.0, 3832265.0, 1575.83203125], [558995.0, 3832480.0, 1415.69396973]], [[557985.0, 3833650.0, 1356.92895508], [558474.6446609406, 3833670.0, 1339.99499512], [558995.0, 3833610.0, 1334.98999023], [559305.0, 3833380.0, 1334.52600098]], [[557265.0, 3833090.0, 1395.604740854091], [557651.464466094, 3833366.464466094, 1375.521017002312], [557985.0, 3833650.0, 1356.92895508]], [[555485.0, 3832030.0, 1495.46801758], [555765.0, 3832340.0, 1462.61096191], [556271.5685424949, 3832706.568542495, 1433.85900879], [556865.0, 3832930.0, 1413.82299805], [557265.0, 3833090.0, 1395.604740854091]], [[554996.7959923933, 3832314.9075862602, 1595.16101074], [555485.0, 3832030.0, 1495.46801758]], [[555650.0, 3831035.0, 1696.64501953], [555556.2453835001, 3831620.590931226, 1600.30297852], [555485.0, 3832030.0, 1495.46801758]], [[555160.0111280108, 3831900.959283413, 1555.08105469], [555485.0, 3832030.0, 1495.46801758]], [[557225.0, 3831870.0, 1478.87194824], [557305.0, 3832496.568542495, 1431.15905762], [557265.0, 3833090.0, 1395.604740854091]], [[556655.7188396339, 3831548.809726281, 1599.14599609], [557225.0, 3831870.0, 1478.87194824]], [[556820.0, 3831185.0, 1625.14294434], [557225.0, 3831870.0, 1478.87194824]], [[557670.0, 3831065.0, 1610.42797852], [557596.2148161607, 3831602.9097162117, 1603.54797363], [557225.0, 3831870.0, 1478.87194824]], [[557320.0, 3831255.0, 1610.01196289], [557225.0, 3831870.0, 1478.87194824]], [[556040.3553390594, 3834410.0, 1424.26794434], [556795.0, 3834380.0, 1399.99902344], [557135.0, 3834212.5, 1387.13195801], [557548.2106781186, 3834090.0, 1385.18701172], [557875.0, 3833770.0, 1371.20202637], [557916.464466094, 3833698.535533906, 1363.34399414], [557985.0, 3833650.0, 1356.92895508]], [[554695.0, 3834260.0, 1453.35205078], [554915.0, 3834300.0, 1448.96496582], [555275.0, 3834350.0, 1438.5670166], [556040.3553390594, 3834410.0, 1424.26794434]], [[554200.0, 3831915.0, 1734.1159668], [554165.4344327097, 3832344.9667366724, 1638.20898438], [554209.8351780357, 3832771.2138918014, 1565.23706055], [554315.0, 3833210.0, 1540.2295532225], [554525.0, 3833722.573593129, 1515.222045895], [554695.0, 3834260.0, 1453.35205078]], [[553555.0, 3834540.0, 1483.37402344], [554122.0710678119, 3834440.0, 1467.63598633], [554695.0, 3834260.0, 1453.35205078]], [[552945.0, 3833300.0, 1548.74401855], [553141.6116523517, 3833976.6116523515, 1510.06201172], [553555.0, 3834540.0, 1483.37402344]], [[552190.0, 3832885.0, 1766.67004395], [552611.4083463016, 3833117.5397053435, 1624.66601563], [552945.0, 3833300.0, 1548.74401855]], [[553090.9363958219, 3832877.7756805834, 1629.60998535], [552945.0, 3833300.0, 1548.74401855]], [[553370.0, 3832575.0, 1755.58496094], [553090.9363958219, 3832877.7756805834, 1629.60998535]], [[553070.0, 3832395.0, 1752.17700195], [553090.9363958219, 3832877.7756805834, 1629.60998535]], [[551635.0, 3834900.0, 1535.43103027], [552305.0, 3834950.0, 1520.02404785], [552522.3223304703, 3834977.32233047, 1514.68701172], [552715.0, 3835000.0, 1509.9720459], [553155.0, 3834820.0, 1498.68701172], [553374.6446609406, 3834720.355339059, 1490.76000977], [553555.0, 3834540.0, 1483.37402344]], [[551545.790458479, 3833987.794313732, 1629.69299316], [551607.9515019354, 3834547.2437048387, 1573.0], [551635.0, 3834900.0, 1535.43103027]], [[551285.5921605353, 3833822.1945038, 1726.13000488], [551545.790458479, 3833987.794313732, 1629.69299316]], [[551838.5052645799, 3833568.1533478876, 1789.25500488], [551545.790458479, 3833987.794313732, 1629.69299316]], [[550905.0, 3835000.0, 1559.76904297], [551635.0, 3834900.0, 1535.43103027]], [[549863.1801948466, 3835061.819805153, 1586.42700195], [550305.0, 3835010.0, 1574.27404785], [550905.0, 3835000.0, 1559.76904297]], [[549814.1613907671, 3835639.5020398577, 1644.53100586], [549863.1801948466, 3835061.819805153, 1586.42700195]], [[548606.4611179013, 3834858.048922121, 1629.84094238], [549228.0715524645, 3834955.730561838, 1611.1739502], [549863.1801948466, 3835061.819805153, 1586.42700195]], [[548220.0, 3834505.0, 1709.73400879], [548606.4611179013, 3834858.048922121, 1629.84094238]], [[547970.0, 3835125.0, 1710.39404297], [548606.4611179013, 3834858.048922121, 1629.84094238]], [[549920.0, 3834385.0, 1710.55505371], [549863.1801948466, 3835061.819805153, 1586.42700195]], [[550792.4534461171, 3834382.579406548, 1712.13000488], [550905.0, 3835000.0, 1559.76904297]], [[550959.7006201764, 3835355.3372697714, 1593.78503418], [550905.0, 3835000.0, 1559.76904297]], [[550977.4609183068, 3835825.9851702265, 1655.41894531], [550959.7006201764, 3835355.3372697714, 1593.78503418]], [[551390.0, 3835555.0, 1691.47998047], [550959.7006201764, 3835355.3372697714, 1593.78503418]], [[556048.0260345298, 3834813.6481767944, 1513.50598145], [556040.3553390594, 3834410.0, 1424.26794434]], [[555994.7451401387, 3835266.535779119, 1632.44299316], [556048.0260345298, 3834813.6481767944, 1513.50598145]], [[556380.0, 3835475.0, 1766.16503906], [555994.7451401387, 3835266.535779119, 1632.44299316]], [[555480.0, 3835265.0, 1770.6739502], [555994.7451401387, 3835266.535779119, 1632.44299316]], [[556050.0, 3835565.0, 1753.31103516], [555994.7451401387, 3835266.535779119, 1632.44299316]], [[556440.0, 3834985.0, 1747.23498535], [556048.0260345298, 3834813.6481767944, 1513.50598145]], [[559336.7240329378, 3832011.3965732106, 1508.97595215], [559834.0123805885, 3832499.804771796, 1443.31298828], [559870.0, 3832895.0, 1390.48303223], [559947.0710678119, 3833220.0, 1322.34301758]], [[562950.0, 3830915.0, 1401.5760498], [563132.5735931288, 3831670.0, 1244.45495605]], [[564330.0, 3832825.0, 1536.9239502], [564559.5091262514, 3832373.3060077177, 1385.0], [564506.2282318603, 3831929.298554458, 1298.55200195], [564417.3223304703, 3831097.67766953, 1214.96398926]]]
    #linesName = [['streamID', 'strahler'], [0, 4], [1, 1], [2, 4], [3, 4], [4, 4], [5, 2], [6, 1], [7, 1], [8, 4], [9, 2], [10, 1], [11, 2], [12, 1], [13, 1], [14, 4], [15, 3], [16, 2], [17, 1], [18, 1], [19, 2], [20, 1], [21, 2], [22, 1], [23, 1], [24, 4], [25, 4], [26, 2], [27, 2], [28, 1], [29, 1], [30, 1], [31, 1], [32, 4], [33, 3], [34, 2], [35, 1], [36, 1], [37, 1], [38, 2], [39, 1], [40, 1], [41, 1], [42, 1], [43, 3], [44, 3], [45, 1], [46, 3], [47, 2], [48, 1], [49, 2], [50, 1], [51, 1], [52, 3], [53, 2], [54, 1], [55, 1], [56, 2], [57, 2], [58, 1], [59, 2], [60, 1], [61, 1], [62, 1], [63, 1], [64, 2], [65, 1], [66, 1], [67, 2], [68, 2], [69, 1], [70, 1], [71, 1], [72, 1], [73, 1], [74, 1], [75, 1]]
    #WriteLineShp(lines, r'E:\test\line.shp', linesName)
    polysIdx = [[0,1,2],[3,4,5],[6,7,8]]
    polysCoors = [[2,3],[4,5],[7,7],[12,3],[4,15],[7.8,7],[2,13],[14,5],[27,7]]
    polysName = [['poly1','1'],['poly2','12'],['poly3','22']]
    WritePolyonShp(polysIdx, polysCoors, r'E:\test\polys.shp', polysName)