#! /usr/bin/env python
#coding=utf-8
# Package   :  Constructure TIN based on CGAL-python packages 
# 
# Created By:  Liangjun Zhu
# Date From :  5/13/15
# Version   :  8/16/15 v1.0 preprocessing, Steepest flow path, and Channel extraction
               
# Email     :  zlj@lreis.ac.cn
#
### LIBRARY IMPORT ###
### CGAL: http://cgal-python.gforge.inria.fr/, used for TIN generation
### XALGLIB: http://www.alglib.net/, used for IDW interpolation with quadratic nodal functions
import CGAL
from CGAL.Triangulations_2 import *
from CGAL.Kernel import Point_2
import os,sys
import xalglib
import math

sys.setrecursionlimit(100000000) ## to avoid the error: maximum recursion depth exceeded in cmp
ZERO = 1e-9

### @function get neigborhood vertexes' index
### @params triangulation object(dt), vertex object(v), 2D coordinates list(pts2DList)
### @return vertexes List(NbrVertexIdx)
def getNbrVertexIdx(dt,v,pts2DList):
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
    NbrVertexIdx = []
    for f in finites_faces:
        for i in range(3):
            NbrVertexIdx.append(pts2DList.index([f.vertex(i).point()[0],f.vertex(i).point()[1]]))
    NbrVertexIdx = list(set(NbrVertexIdx))
    return NbrVertexIdx



### @function get neigborhood vertexes' index.
### @params start vertex index (sVertexIdx), VertexTriangleList
### @return vertexes List(NbrVertexIdx)
def getNbrVertexIdx2(sVertexIdx,VertexTriangleList,TriangleVertexList):
    adjTriangle = VertexTriangleList[sVertexIdx]
    NbrVertexIdx = []
    for tri in range(len(adjTriangle)):
        if tri is not None:
            t = TriangleVertexList[adjTriangle[tri]]
            for i in range(3):
                NbrVertexIdx.append(t[i])
    NbrVertexIdx = list(set(NbrVertexIdx))
    NbrVertexIdx.remove(sVertexIdx)
    return NbrVertexIdx

    


### @function get the adjacent triangles of an edge
### @params two indexs of vertexes, VertexTriangleList
def getAdjTriangles(p1,p2, VertexTriangleList):
    tri1 = VertexTriangleList[p1]
    tri2 = VertexTriangleList[p2]
    if None in tri1:
        tri1.remove(None)
    if None in tri2:
        tri2.remove(None)
    return list(set(tri1).intersection(set(tri2)))
### @function calculate distance between two points
### @params pt1, pt2 is 2D/3D coordinates, d is dimention which can be 2 or 3
### @return distance
def calDistance(pt1,pt2,d):
    sqrtSum = 0.
    if pt1 is not None and pt2 is not None and len(pt1) == len(pt2) == 3:
        for i in range(d):
            sqrtSum = sqrtSum + (pt1[i]-pt2[i])*(pt1[i]-pt2[i])
        return math.sqrt(sqrtSum)
    else:
        return None


### @function linearInterpFlatEdge is aimed to solve flat edge problem
### @params curVerIdx is current vertexes of the flat edge, vernbrVerIdx is the corresponding neigborhood vertexes, pts is 3D coordinate list
### @return True or False, if True, the z-values of the current vertexes 
def linearInterpFlatEdge(curVerIdx, verNbrVerIdx, pts):
    ### 1. Assign the upstream point and downstream point according the maximum
    ###    of the surrouding elevation, or the second highest elevation
    ### 2. pt1 is the minimum that greater than the upstream point
    ###    pt2 is the upstream
    ###    pt3 is the downstream
    ###    pt4 is the minimum that less than the downstream point
    ### 3. z2 = z1 - (z1-z4)*d1/(d1+d2+d3)
    ###    z3 = z1 - (z1-z4)*(d1+d2)/(d1+d2+d3)
    ### 
    flatZ = 0.
    curVerCoor = []
    for idx in curVerIdx:
        curVerCoor.append(pts[idx])
    flatZ = curVerCoor[0][2]
    maxZ = []
    maxZIdx = []
    secMaxZ = []
    secmaxZIdx = []
    minGTZ = []
    minGTZCoor = []
    minZ = []
    minZCoor = []
    for idxs in verNbrVerIdx:
        tempNbrCoor = []
        tempMaxZ = -9999
        tempMaxZIdx = 0
        tempSecMaxZ = -9999
        tempSecMaxZIdx = 0
        tempMinGTZ = flatZ * 2
        tempminGTZCoor = None
        tempMinZ = flatZ * 2
        tempminZCoor = None
        for idx in idxs:
            tempPt = pts[idx]
            tempNbrCoor.append(tempPt)
            if tempPt[2] > tempMaxZ:
                tempMaxZ = tempPt[2]
                tempMaxZIdx = idx
            if tempPt[2] < tempMinZ:
                tempMinZ = tempPt[2]
                tempminZCoor = tempPt
        for coor in tempNbrCoor:
            if coor[2] > tempSecMaxZ and coor[2] < tempMaxZ:
                tempSecMaxZ = coor[2]
                tempSecMaxZIdx = idxs[tempNbrCoor.index(coor)]
            if coor[2] > flatZ and coor[2] < tempMinGTZ:
                tempMinGTZ = coor[2]
                tempminGTZCoor = coor
        maxZ.append(tempMaxZ)
        maxZIdx.append(tempMaxZIdx)
        secMaxZ.append(tempSecMaxZ)
        secmaxZIdx.append(tempSecMaxZIdx)
        minGTZ.append(tempMinGTZ)
        minGTZCoor.append(tempminGTZCoor)
        minZ.append(tempMinZ)
        minZCoor.append(tempminZCoor)
        #verNbrVerCoor.append(tempNbrCoor)
    if maxZ[0] > maxZ[1]:
        upstream = 0
    elif maxZ[0] < maxZ[1]:
        upstream = 1
    else:
        if secMaxZ[0] > secMaxZ[1]:
            upstream = 0
        elif secMaxZ[0] < secMaxZ[1]:
            upstream = 1
        else:
            upstream = -9999
    if upstream != -9999:
        ## [index, Coordinate]
        if len(curVerCoor) == len(curVerIdx) == len(minGTZCoor) == len(minZCoor) == 2:
            pt1 = [minGTZCoor[upstream]]
            pt2 = [curVerIdx[upstream], curVerCoor[upstream]] 
            pt3 = [curVerIdx[(upstream+1)%2], curVerCoor[(upstream+1)%2]]
            pt4 = [minZCoor[(upstream+1)%2]]
            ###    z2 = z1 - (z1-z4)*d1/(d1+d2+d3)
            ###    z3 = z1 - (z1-z4)*(d1+d2)/(d1+d2+d3)
            dimension = 3
            d1 = calDistance(pt1[0],pt2[1],dimension)
            d2 = calDistance(pt2[1],pt3[1],dimension)
            d3 = calDistance(pt3[1],pt4[0],dimension)
            if d1 is not None and d2 is not None and d3 is not None:
                z2 = pt1[0][2] - (pt1[0][2]-pt4[0][2])*d1/(d1+d2+d3)
                z3 = pt1[0][2] - (pt1[0][2]-pt4[0][2])*(d1+d2)/(d1+d2+d3)
                pts[pt2[0]][2] = z2
                pts[pt3[0]][2] = z3
                return True
            else:
                return False
        else:
            return False
    else:
        return False
        
    

### @function detect if the edge is false dam. refer to p98~100 in Nelson(1994)
### @params ptIdxs include four points' index, pts is 3D coordinates list, idwIns is an object of xalglib, multi is the amplifier
###         the function used in xalglib is introduced in http://www.alglib.net/translator/man/manual.cpython.html#sub_idwbuildmodifiedshepard
###         0,1 is the current edge, 3 and 4 is the diagonal
### @return True or False
def detectFalseDam(ptIdxs,pts,idwIns,multi):
    ptCoors = []
    for idx in ptIdxs:
        ptCoors.append(pts[idx])
    midPt1 = []
    midPt2 = []
    for i in range(3):
        midPt1.append((ptCoors[0][i]+ptCoors[1][i])/2.)
        midPt2.append((ptCoors[2][i]+ptCoors[3][i])/2.)
    idwZ1 = xalglib.idwcalc(idwIns,[midPt1[0],midPt1[1]])
    idwZ2 = xalglib.idwcalc(idwIns,[midPt2[0],midPt2[1]])
    if abs(idwZ1-midPt1[2]) > multi * abs(idwZ2-midPt2[2]):
        return True
    else:
        return False
    

### @function create Delaunay triangulation and solve flat triangles, pits, flat edges, and false dams automatically.
### @params pts is 3D coordinates list, pts2DList is xy coordinates of pts, multiplier is used for false dam detection, refers to detectFalseDam funtion above
def createTIN(pts,pts2DList,idwShepardParams,multiplier,SWITCH):
    ## The main steps of createTIN:
    ## 1. Create Delaunay Triangulated Irregular Network using CGAL
    ## 2. Remove Flat triangle by insert point using an inverse distance weighted interpolation with quadratic nodal functions
    ## 3. Remove pit using a recursive algorithm
    ## 4. Handle flat edges by fliping operation
    ## 5. Detect false dams and correct by swapping edge
    
    dt = Constrained_Delaunay_triangulation_2()
    #dt = Delaunay_triangulation_2()
    
    VertexList = []
    TriangleVertexList = []
    TriangleNbrIdxList = []
    VertexTriangleList = []
    print "Construct Delaunay Triangulated Irregular Network... "
    for p in pts:
        dt.insert(Point_2(p[0],p[1]))

    if SWITCH[0]:
        print "Remove Flat triangle by insert additional point..."
        idwIns = xalglib.idwbuildmodifiedshepard(pts,len(pts),2,2,idwShepardParams[0],idwShepardParams[1])
        flatTriangleNum = 9999
        handledFlatTriangle = 0
        lockedVertexIdx = []
        while flatTriangleNum != 0:
            for f in dt.faces:
                tempPtsIdx = []
                for i in range(3):
                    tempp = f.vertex(i).point()
                    tempPtsIdx.append(pts2DList.index([tempp[0],tempp[1]]))
                p1Coor = pts[tempPtsIdx[0]]
                p2Coor = pts[tempPtsIdx[1]]
                p3Coor = pts[tempPtsIdx[2]]
                if p1Coor[2] == p2Coor[2] == p3Coor[2]:
                    #print p1Coor,p2Coor,p3Coor
                    #print tempPtsIdx[0],tempPtsIdx[1],tempPtsIdx[2]
                    flatTriangleNum = 1
                    ## Insert additional point
                    insertPt = []
                    insertPt.append((p1Coor[0]+p2Coor[0]+p3Coor[0])/3.)
                    insertPt.append((p1Coor[1]+p2Coor[1]+p3Coor[1])/3.)
                    zValue = xalglib.idwcalc(idwIns, insertPt)
                    #print zValue
                    #print xalglib.idwcalc(idwIns,[719532.147, 21198.921])
                    insertPt.append(zValue)
                    #print insertPt
                    pts.append(insertPt)
                    pts2DList.append([insertPt[0],insertPt[1]])
                    lockedVertexIdx.append(len(pts2DList)-1) ## to avoid be modified in PitRemove
                    dt.insert_in_face(Point_2(insertPt[0],insertPt[1]),f)
                    idwIns = xalglib.idwbuildmodifiedshepard(pts,len(pts),2,2,idwShepardParams[0],idwShepardParams[1])
                    ## End insert
                    #### when one flat triangle is handled, update the dt, and restart!
                    handledFlatTriangle = handledFlatTriangle + 1
                    print "    %d flat triangle is handled!" % handledFlatTriangle
                    break
            #### if the code run to this line, it implies there are no flat triangles.
            flatTriangleNum = 0
        
    if SWITCH[1]:
        print "Remove pit using a recursive algorithm..."
        pitNum = 9999
        previousPitNum = 0
        maxLoop = 10
        loop = 0
        while (pitNum != 0 and pitNum != previousPitNum) and loop < maxLoop:
            previousPitNum = pitNum
            handledPit = 0
            for v in dt.vertices:
                curVertexIdx = pts2DList.index([v.point()[0],v.point()[1]])
                if curVertexIdx not in lockedVertexIdx:
                    NbrVertexIdx = getNbrVertexIdx(dt,v,pts2DList)
                    NbrVertexIdx.remove(curVertexIdx)
                    flag = True
                    curZ = pts[curVertexIdx][2]
                    arrZ = []
                    for verIdx in NbrVertexIdx:
                        tempZ = pts[verIdx][2]
                        if tempZ <= curZ:
                            flag = False
                            break
                        else:
                            arrZ.append(tempZ)
                    if flag:
                        lockedVertexIdx.append(curVertexIdx)
                        arrZ.sort()
                        curZ = float(arrZ[0]+arrZ[1])/2.
                        pts[curVertexIdx][2] = curZ
                        handledPit = handledPit + 1
            print "    %d pits have been removed!" % handledPit
            pitNum = handledPit
            loop = loop + 1
            #print pitNum, previousPitNum
            
    if SWITCH[2]:
        print "Handle flat edges by swapping edges or linear interpolation..."
        flatEdge = 0
        for f in dt.faces:
            vertexZ = [] ## 3 vertexes of triangle f
            for i in range(3):
                tempp = f.vertex(i).point()
                idx = pts2DList.index([tempp[0],tempp[1]])
                vertexZ.append(pts[idx][2])
            for i in range(3):
                if vertexZ[i] == vertexZ[(i+1)%3]: ## the i-th edge is flat edge
                    for j in range(3):
                        nbrF = f.neighbor(j)       ## the j-th neighbor triangle of f,  dt.is_infinite(nbrF) == False means nbrF is not None
                        if dt.is_infinite(nbrF) == False and nbrF.has_vertex(f.vertex(i)) and nbrF.has_vertex(f.vertex((i+1)%3)):
                            ### the followed code is for Constrained_Delaunay_triangulation_2
                            ### Note: Delaunay_triangulation_2 does not have the .is_flipable method
                            if dt.is_flipable(f,j):
                                dt.flip(f,j)
                                flatEdge = flatEdge +1
                                break
                            else:
                                ### TODO: the original algorithm is as follows.
                                ### 1. if the adjacent triangles both flow to the edge
                                ### 2. if the two vertex flow out, then flip the edge.
                                ###    BE CAUTION, before flip, do check the four points to be a convex hull
                                ### 3. if one vertex flow out and the other does not, then the flow in vertex's
                                ###    elevation need to be modified.
                                ### However, the original algorithm is a little bit complex
                                ### In current implementation, I use a simple rule to distinguish which vertex
                                ###   is upstream and which is downstream. Then a linear interpolation is used
                                ###   to modifiy the elevations of vertexes
                                verList = [f.vertex(i),f.vertex((i+1)%3)]
                                curVerIdx = []
                                curVerCoor = []
                                verNbrVerIdx = []
                                verNbrVerCoor = []
                                for ver in verList:
                                    temp = ver.point()
                                    current = pts2DList.index([temp[0],temp[1]])
                                    curVerIdx.append(current)
                                    neighbor = getNbrVertexIdx(dt,ver,pts2DList)
                                    neighbor.remove(current)
                                    verNbrVerIdx.append(neighbor)
                                #print curVerIdx
                                #print verNbrVerIdx
                                if linearInterpFlatEdge(curVerIdx, verNbrVerIdx, pts):
                                    flatEdge = flatEdge +1
                                break
        print "    %d flat edges have been fliped!" % flatEdge
                                
    if SWITCH[3]:
        print "Detect flase Dams and correct by swapping edges..."
        idwIns = xalglib.idwbuildmodifiedshepard(pts,len(pts),2,2,idwShepardParams[0],idwShepardParams[1])
        falseDam = 0
        for f in dt.faces:
            #      p1
            #    / | \
            #p4 /  |  \ p3
            #   \  |  /
            #    \ | /
            #      p2
            for i in range(3):
                p1 = f.vertex(i)
                p1Idx = pts2DList.index([p1.point()[0],p1.point()[1]])
                p2 = f.vertex((i+1)%3)
                p2Idx = pts2DList.index([p2.point()[0],p2.point()[1]])
                p3 = f.vertex((i+2)%3)
                p3Idx = pts2DList.index([p3.point()[0],p3.point()[1]])
                for j in range(3):
                    nbrF = f.neighbor(j)
                    if dt.is_infinite(nbrF) == False:
                        nbrFver = [nbrF.vertex(0), nbrF.vertex(1), nbrF.vertex(2)]
                        if p1 in nbrFver and p2 in nbrFver:
                            nbrFver.remove(p1)
                            nbrFver.remove(p2)
                            p4 = nbrFver[0]
                            if dt.is_infinite(p4) == False and [p4.point()[0],p4.point()[1]] in pts2DList:
                                p4Idx = pts2DList.index([p4.point()[0],p4.point()[1]])
                                dam = detectFalseDam([p1Idx,p2Idx,p3Idx,p4Idx],pts,idwIns, multiplier)
                                if dam:
                                    ### the follow code is to figure out if the four points construct a convex hull and the edge can be swapped
                                    fourPt = [p1.point(),p2.point(),p3.point(),p4.point()]
                                    ch = CGAL.Convex_hull_2.convex_hull_2(fourPt)
                                    if len(ch) == 4:
                                        dt.flip(f,j)
                                        falseDam = falseDam + 1
                                        break
                break
        print "    %d false dams have been modified!" % falseDam

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
            nbrF = f.neighbor(i)
            if dt.is_infinite(nbrF) == False:
                for j in range(3):
                    tempFaceIdx.append(pts2DList.index([nbrF.vertex(j).point()[0],nbrF.vertex(j).point()[1]]))
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
    return (TriangleVertexList,TriangleNbrIdxList,VertexTriangleList,pts)

### @function calculate parameters of the plane
### @params coordinates of the three points
### @return four variables defined by the equation such as Ax+By+Cz+D=0
def tranglePlane(p1,p2,p3):
    A = p1[1]*(p2[2]-p3[2])+p2[1]*(p3[2]-p1[2])+p3[1]*(p1[2]-p2[2]) ## A = y1(z2-z3)+y2(Z3-Z1)+y3(Z1-Z2)
    B = p1[2]*(p2[0]-p3[0])+p2[2]*(p3[0]-p1[0])+p3[2]*(p1[0]-p2[0]) ## B = Z1(x2-x3)+z2(x3-x1)+z3(x1-x2)
    C = p1[0]*(p2[1]-p3[1])+p2[0]*(p3[1]-p1[1])+p3[0]*(p1[1]-p2[1]) ## C = x1(y2-y3)+x2(y3-y1)+x3(y1-y2)
    D = -1*A*p1[0]-B*p1[1]-C*p1[2]                                  ## D = -Ax1-By1-Cz1
    #print A,B,C,D
    return (float(A),float(B),float(C),float(D))

### @function Calculate which edge will be the steepest descent intersect
### @parms three vertexes of a triangle (v), a point which is the begin of the steepest descent vector (v0)
### @return the first point's index of the intersected edge or None
def findIntersectIdx(v,v0,A,B,C):
### the basic idea is OC=xOA+yOB, when x>0 and y>0, then OC is between OA and OB
### and be careful, this function can not handle the situation that v0 is one in v!
    intersect = []##  intersect is the first point's index of the intersected edges
    edge = -1
    for i in range(3):
        ## OA, OB vector
        o1 = [v[i][0]-v0[0],v[i][1]-v0[1]]
        o2 = [v[(i+1)%3][0]-v0[0],v[(i+1)%3][1]-v0[1]]
        ## if OA and OB are collinear?
        k  = o1[1]*o2[0]-o1[0]*o2[1]
        if abs(k) <= ZERO:
            ## if deepest flow path vector (A/C, B/C) is also collinear?
            k1 = o1[1]*A/C - o1[0]*B/C
            k2 = o2[1]*A/C - o2[0]*B/C
            if abs(k1) <= ZERO and abs(k2) <= ZERO:
                intersect.append(i)
            edge = i
        else:
            m  = (o2[0]*B/C-o2[1]*A/C) / k
            if o2[0] != 0:
                n = (A/C-m*o1[0])/o2[0]
            else:
                n = (B/C-m*o1[1])/o2[1]
            if m > 0 and n > 0:
                intersect.append(i)
    if len(intersect) > 0:
        return intersect[0]
    elif edge != -1:
        return edge
    else:
        return None


### @function Calculate the intersected point
### @params point (p0) and vector (normal) is one line, and p1, p2 consist the other
### @return if succeed, return xy values, else return None
def intersectPoint(p0,normal,p1,p2):
    A = normal[0]
    B = normal[1]
    if p1[0] == p2[0]:
        if A != 0:
            xx = p1[0]
            yy = p0[1]+(xx-p0[0])*B/A
        else:
            xx = None
            yy = None
    else:
        k = (p1[1]-p2[1])/(p1[0]-p2[0])
        if A == 0:
            xx = p0[0]
            yy = p1[1]+(xx-p1[0])*k
        else:
            if k != 0:
                if B/A != k:
                    xx = (p1[1]-p0[1]-k*p1[0]+B/A*p0[0])/(B/A-k)
                    yy = (xx-p1[0])*k+p1[1]
                else:
                    xx = None
                    yy = None
            else:
                if B != 0:
                    yy = p1[1]
                    xx = (yy-p0[1])*A/B+p0[0]
                else:
                    xx = None
                    yy = None
    return (xx,yy)

### @function calculate the steepest flow path from the centriod of a triangle to one of the edges
### @params index of the triangle(curTriangleIdx), TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx
### @return the coordinate of the intersected points (interPt), and the next triangle index
def firstSegmentSteepestPath(curTriangleIdx,TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx):
    ## the plane equation is defined as Ax+By+Cz+D=0
    t = TriangleVertexList[curTriangleIdx]
    v = [VertexList[t[0]],VertexList[t[1]],VertexList[t[2]]]
    #print v
    A,B,C,D = tranglePlane(v[0],v[1],v[2])
    ## centriod point v0
    v0 = [(v[0][0]+v[1][0]+v[2][0])/3.,(v[0][1]+v[1][1]+v[2][1])/3.,(v[0][2]+v[1][2]+v[2][2])/3.]
    curPath.append(v0)
    curVerIdx.append(-1)  ## -1 means the vertex in the flow path is not a node in TIN
    #print v0
    ## the steepest descent equation is (x-v0[0])/(A/C)=(y-v0[1])/(B/C)
    ## 2D line equation format (x-x1)/(x1-x2)=(y-y1)/(y1-y2)
    ## firstly, decide which edge will be the steepest descent intersect
    if C != 0: ## C = 0 means a flat triangle, which is handled in createTIN function.
        intersect = findIntersectIdx(v,v0,A,B,C)  ## the first point's index of the intersected edge
        ## calculate the endpoint
        if intersect is not None:
            (xx,yy) = intersectPoint(v0,[A/C,B/C],v[intersect],v[(intersect+1)%3])
            if xx is not None and yy is not None:
                zz = -1*(A*xx+B*yy+D)/C
                interPt = [xx,yy,zz]
                curPath.append(interPt)
                curVerIdx.append(-1)
                ## find the next adjacent trangle
                ## edgeTriangle find the common trangles among two vertexes
                edgeTriangle = list(set(VertexTriangleList[t[intersect]]).intersection(set(VertexTriangleList[t[(intersect+1)%3]])))
                edgeTriangle.remove(curTriangleIdx)
                if len(edgeTriangle) != 0: ## len(edgeTriangle) == 0 means a terminal
                    #print curTriangleIdx, edgeTriangle[0]
                    #print curPath
                    return (interPt,edgeTriangle[0])
                else:
                    return (interPt,None)
            else:
                return None,None
        else:
            return None,None
    else:
        return None,None

### @function Figure out if a point is one a line
### @params point (pt0), line is consists of pt1 and pt2
### @return True or False
def pointInLine(pt0, pt1, pt2): ## if pt0 on the line determined by pt1 and pt2
    if pt1[0] == pt2[0]:
        if pt0[0] == pt1[0]:
            return True
        else:
            return False
    elif pt1[1] == pt2[1]:
        if pt0[1] == pt1[1]:
            return True
        else:
            return False
    else:
        if abs((pt0[0]-pt1[0])*(pt1[1]-pt2[1])-(pt0[1]-pt1[1])*(pt1[0]-pt2[0])) <= ZERO:
            return True
        else:
            return False
        

### @function Figure out if the steepest flow direction is towards the edge
### @params start (pt1) and end(pt2) vertex coordinate of the edge, v is triangleVertexes
### @return value which indicates whether flow in or out of the edge
def flow2edge(pt1,pt2,v):
    A,B,C,D = tranglePlane(v[0],v[1],v[2])
    if C != 0:
        edge = [pt2[0]-pt1[0],pt2[1]-pt1[1]]
        m = A/C*edge[1] - B/C * edge[0]
        return m


### @function Continue the calculation of steepest flow path, begin with a node in the TIN
### @params start node index (sVertexIdx), TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx
### @return No return and this a recursive function
def continuedVertexSteepestPath(sVertexIdx,TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx):
    adjTriangle = VertexTriangleList[sVertexIdx]
    ## if both triangles slopes towards the edge and the edge flow away
    ## from the sVertexIdx, then the path continues to be channel
    flag2 = True  ## the next segement is overland flow
    flag1 = True  ## the next segement is channel flow
    
    edgeDownslp = []
    for tri in range(len(adjTriangle)):
        tri2 = (tri+1)%len(adjTriangle)
        t1 = TriangleVertexList[adjTriangle[tri]]
        t2 = TriangleVertexList[adjTriangle[tri2]]
        if t1 is not None and t2 is not None:
            v1 = [VertexList[t1[0]],VertexList[t1[1]],VertexList[t1[2]]]
            v2 = [VertexList[t2[0]],VertexList[t2[1]],VertexList[t2[2]]]
            startVertex = VertexList[sVertexIdx]
            endVertexIdxList = list(set([t1[0],t1[1],t1[2]]).intersection(set([t2[0],t2[1],t2[2]])))
            #print sVertexIdx,endVertexIdxList
            endVertexIdxList.remove(sVertexIdx)
            if len(endVertexIdxList) == 1:
                endVertexIdx = endVertexIdxList[0]
                endVertex = VertexList[endVertexIdx]
                leftFlag = leftTriangle(startVertex,endVertex,v1)
                if leftFlag == True:
                    m1 = flow2edge(startVertex,endVertex,v1)
                    m2 = flow2edge(startVertex,endVertex,v2)
                else:
                    m1 = flow2edge(startVertex,endVertex,v2)
                    m2 = flow2edge(startVertex,endVertex,v1)
                if (m1 > 0 and m2 < 0) or (m1 > 0 and abs(m2) < ZERO) or (m2 < 0 and abs(m1) < ZERO):
                    if endVertex[2] < startVertex[2]:
                        edgeDownslp.append([endVertexIdx,startVertex[2] - endVertex[2]])
    if len(edgeDownslp) != 0:
        maxElevDiff = -9999.0
        for elem in edgeDownslp:
            if elem[1] > maxElevDiff:
                maxElevDiff = elem[1]
                endVertexIdx = elem[0]
        curPath.append(VertexList[endVertexIdx])
        curVerIdx.append(endVertexIdx)
        continuedVertexSteepestPath(endVertexIdx,TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx)
    else:
        flag1 = False
    
    

    if flag1 == False:
        ## the next flow is not a channel
        ## figure out which triangle it should flow over
        edgeDownslp = []
        for tri in range(len(adjTriangle)):
            t = TriangleVertexList[adjTriangle[tri]]
            if t is not None:
                v = [VertexList[t[0]],VertexList[t[1]],VertexList[t[2]]]
                A,B,C,D = tranglePlane(v[0],v[1],v[2])
                startVertex = VertexList[sVertexIdx]
                if C != 0:
                    intersect = findIntersectIdx(v,startVertex,A,B,C)
                    if intersect is not None and t[intersect] != sVertexIdx and t[(intersect+1)%3] != sVertexIdx:
                        pti = v[intersect]
                        ptj = v[(intersect+1)%3]
                        (xx,yy) = intersectPoint(startVertex,[A/C,B/C],pti,ptj)
                        if xx is not None and yy is not None:
                            zz = -1*(A*xx+B*yy+D)/C
                            interPt = [xx,yy,zz]
                            edgeDownslp.append([interPt,t[intersect],t[(intersect+1)%3],adjTriangle[tri],startVertex[2]-zz])
        if len(edgeDownslp) != 0:
            maxElevDiff = -9999.0
            for elem in edgeDownslp:
                if elem[4] > maxElevDiff:
                    maxElevDiff = elem[4]
                    interPt = elem[0]
                    startIdx = elem[1]
                    endIdx = elem[2]
                    triID = elem[3]
            curPath.append(interPt)
            curVerIdx.append(-1)
            ## find the next adjacent trangle
            ## edgeTriangle find the common trangles among two vertexes
            edgeTriangle = list(set(VertexTriangleList[startIdx]).intersection(set(VertexTriangleList[endIdx])))
            edgeTriangle.remove(triID)
            if len(edgeTriangle) != 0: ## len(edgeTriangle) == 0 means a terminal
                continuedSteepestPath(interPt, edgeTriangle[0], TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx)
        else:
            flag2 = False
        
        
        
        
    if flag1 == False and flag2 == False: ## flow to the lowest elevation's direction
        nextIdx = getNbrVertexIdx2(sVertexIdx,VertexTriangleList,TriangleVertexList)
        if nextIdx != []:
            maxElevDiff = -9999
            startVertex = VertexList[sVertexIdx]
            endVertexIdx = -9999
            for idx in nextIdx:
                coor = VertexList[idx]
                if startVertex[2] > coor[2] and startVertex[2] - coor[2] > maxElevDiff:
                    maxElevDiff = startVertex[2] - coor[2]
                    endVertexIdx = idx
            if endVertexIdx != -9999:
                curPath.append(VertexList[endVertexIdx])
                curVerIdx.append(endVertexIdx)
                continuedVertexSteepestPath(endVertexIdx,TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx)
               




### @function Continue the calculation of steepest flow path, begin with a point on the edge of a triangle
### @params point (secPt), the adjacent triangle (secTriIdx), TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx
### @return No return and this a recursive function
def continuedSteepestPath(secPt, secTriIdx, TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx):
    t = TriangleVertexList[secTriIdx]
    v = [VertexList[t[0]],VertexList[t[1]],VertexList[t[2]]]
    A,B,C,D = tranglePlane(v[0],v[1],v[2])
    intersectCurrent = -1
    for i in range(3):
        if pointInLine(secPt, v[i], v[(i+1)%3]):
            intersectCurrent = i
            break
    ## the vector of steepest path is [A/C, B/C, D/C]
    ##ij = [ptj[0]-pti[0],ptj[1]-pti[1],ptj[2]-pti[2]]
    if C != 0 and intersectCurrent != -1:
        intersect = findIntersectIdx(v,secPt,A,B,C)
        if intersect is not None:
            pti = v[intersect]
            ptj = v[(intersect+1)%3]
            if intersect != intersectCurrent: ## overland flow
                (xx,yy) = intersectPoint(secPt,[A/C,B/C],pti,ptj)
                if xx is not None and yy is not None:
                    zz = -1*(A*xx+B*yy+D)/C
                    interPt = [xx,yy,zz]
                    curPath.append(interPt)
                    curVerIdx.append(-1)
                    ## find the next adjacent trangle
                    ## edgeTriangle find the common trangles among two vertexes
                    edgeTriangle = list(set(VertexTriangleList[t[intersect]]).intersection(set(VertexTriangleList[t[(intersect+1)%3]])))
                    edgeTriangle.remove(secTriIdx)
                    if len(edgeTriangle) != 0: ## len(edgeTriangle) == 0 means a terminal
                        #print curTriangleIdx, edgeTriangle[0]
                        #print curPath
                        continuedSteepestPath(interPt, edgeTriangle[0], TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx)
            else: ## current edge is channel
                if pti[2] > ptj[2]:
                    interPt = ptj
                    sVertexIdx = t[(intersect+1)%3]
                    #eVertexIdx = t[intersect]
                else:
                    interPt = pti
                    sVertexIdx = t[intersect]
                    #eVertexIdx = t[(intersect+1)%3]
                curPath.append(interPt)
                curVerIdx.append(sVertexIdx)
                continuedVertexSteepestPath(sVertexIdx,TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx)
                    

### @function calculate a single steepest downslope flow path
### @params index of the triangle(curTriangleIdx), TriangleVertexList,VertexList,VertexTriangleList
### @return current flowpath, both coordinates (curPath) and the index (curVerIdx)
def singleSteepestPath(curTriangleIdx,TriangleVertexList,VertexList,VertexTriangleList):
    curPath = []
    curVerIdx = []
    secPt, secTriIdx = firstSegmentSteepestPath(curTriangleIdx,TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx)
    if secPt is not None and secTriIdx is not None:
        continuedSteepestPath(secPt, secTriIdx, TriangleVertexList,VertexList,VertexTriangleList,curPath,curVerIdx)
    return (curPath,curVerIdx)

### @function calculate all steepest downslope flow paths, begin from the centroid of each triangles
### @params TriangleVertexList, VertexList, VertexTriangleList
### @return SteepestPathList,SteepestPathVertexIdx
def SteepestDescentPath(TriangleVertexList, VertexList, VertexTriangleList):
    SteepestPathList = []
    SteepestPathVertexIdx = []
#    loop=0 ## debug code
    for t in TriangleVertexList: ## Loop every triangle
        ##curPath store the 3D coordinate of each vertex of the steepest path
        curTriangleIdx = TriangleVertexList.index(t)
        curPath,curVerIdx = singleSteepestPath(curTriangleIdx,TriangleVertexList,VertexList,VertexTriangleList)
        SteepestPathList.append(curPath)
        SteepestPathVertexIdx.append(curVerIdx)
#        loop=loop+1   ## debug codes
#        if loop == 160:
#            print "error"
    return (SteepestPathList,SteepestPathVertexIdx)

def leftTriangle(startVertex,endVertex,triangle):
    ### http://blog.csdn.net/modiz/article/details/9928553
    temp = triangle[:]
    temp.remove(startVertex)
    temp.remove(endVertex)
    pt = temp[0]
    s2e = [endVertex[0]-startVertex[0],endVertex[1]-startVertex[1]]
    s2p = [pt[0]-startVertex[0],pt[1]-startVertex[1]]
    m = s2e[0]*s2p[1]-s2e[1]*s2p[0]
    if m > 0:
        return True
    else:
        return False
def angle(pt1,pt2,v):
    A,B,C,D = tranglePlane(v[0],v[1],v[2])
    if C != 0:
        edge = [pt2[0]-pt1[0],pt2[1]-pt1[1]]
        m = A/C*edge[1] - B/C * edge[0]
        dist = math.sqrt(edge[0]*edge[0]+edge[1]*edge[1])
        dist = dist * math.sqrt((A/C)*(A/C)+(B/C)*(B/C))
        cosV = (edge[0]*A/C+edge[1]*B/C)/dist
        #print cosV
        if cosV >= 1.0:
            cosV = 1.0
        if cosV <= -1.0:
            cosV = -1.0
        return math.acos(cosV)*180./math.pi

def addChannelNode2Dict(NodesDict, curNode, downStream, upStream):
    if len(NodesDict) == 0 or not NodesDict.has_key(curNode):  
    ## if the NodesDict is empty, or does not have curNode
        NodesDict[curNode] = [[downStream],[upStream]]
    else:
        NodesDict[curNode][0].append(downStream)
        NodesDict[curNode][1].append(upStream)
def cleanNodeDict(NodesDict):
    for node in NodesDict:
        tempDown = NodesDict[node][0][:]
        tempUp = NodesDict[node][1][:]
        tempDown = list(set(tempDown))
        tempUp = list(set(tempUp))
        if len(tempDown) > 1 and None in tempDown:
            tempDown.remove(None)
        if len(tempUp) > 1 and None in tempUp:
            tempUp.remove(None)
        NodesDict[node][0] = tempDown[:]
        NodesDict[node][1] = tempUp[:]
def flowDirection(NodesDict,sVertexIdx,endVertexIdx,TriangleVertexList,VertexTriangleList,VertexList,thresh):
    adjTri = getAdjTriangles(sVertexIdx,endVertexIdx, VertexTriangleList)
    if len(adjTri) == 2:
        t1 = TriangleVertexList[adjTri[0]]
        t2 = TriangleVertexList[adjTri[1]]
        v1 = [VertexList[t1[0]],VertexList[t1[1]],VertexList[t1[2]]]
        v2 = [VertexList[t2[0]],VertexList[t2[1]],VertexList[t2[2]]]
        startVertex = VertexList[sVertexIdx]
        endVertex = VertexList[endVertexIdx]
        leftFlag = leftTriangle(startVertex,endVertex,v1)
        if leftFlag == True:
            m1 = flow2edge(startVertex,endVertex,v1)
            m2 = flow2edge(startVertex,endVertex,v2)
            ang1 = angle(startVertex,endVertex,v1)
            ang2 = angle(startVertex,endVertex,v2)
        else:
            m1 = flow2edge(startVertex,endVertex,v2)
            m2 = flow2edge(startVertex,endVertex,v1)
            ang1 = angle(startVertex,endVertex,v2)
            ang2 = angle(startVertex,endVertex,v1)
            
        if (m1 > 0 and m2 < 0) or (m1 > 0 and (abs(m2) < ZERO or ang2 <= thresh)) or (m2 < 0 and (abs(m1) < ZERO or ang1 < thresh)):
            if endVertex[2] < startVertex[2]: ## startVertex is the upstream of endVertex
                addChannelNode2Dict(NodesDict, sVertexIdx, endVertexIdx, None)
                addChannelNode2Dict(NodesDict, endVertexIdx, None, sVertexIdx)
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
### @function Calculate channel flow
### @params VertexTriangleList, VertexTriangleList, VertexList
### @return NodesDict and channelList
def FindChannelNodes(TriangleVertexList, VertexTriangleList, VertexList,thresh):
    NodesDict = {}
    channelList = []
    ## the format of channelNodesDict is:
    ##    {vertexIndex:[[downStream],[upStream]]}
    for f in TriangleVertexList:
        for i in range(3): ## edge: f[i],f[(i+1)%3]
            sVertexIdx = f[i]
            endVertexIdx = f[(i+1)%3]
#            if sVertexIdx == 86 and endVertexIdx == 80:
#                print "error"
            
            flag = flowDirection(NodesDict,sVertexIdx,endVertexIdx,TriangleVertexList,VertexTriangleList,VertexList,thresh)
            if flag == False:
                flag = flowDirection(NodesDict,endVertexIdx,sVertexIdx,TriangleVertexList,VertexTriangleList,VertexList,thresh)
    cleanNodeDict(NodesDict)
    outlets = []
    for node in NodesDict:
        if NodesDict[node][0] == [None]:
            outlets.append(node)
    ## channelList stores coordinates of each channel
    for outlet in outlets:
        curCha = []
        backupChannelNodes(outlet,curCha,NodesDict,VertexList,channelList)
    
    return (NodesDict,channelList)
    
    
#    for steepestPath in SteepestPathVertexIdx:
#        steepestPath.reverse()
#        verNum = len(steepestPath)
#        if steepestPath[0] != -1: ## the end vertex is Node
#            if verNum > 1:
#                if steepestPath[1] != -1: ## the end Node has a upstream node
#                    downStream = None
#                    curNode = steepestPath[0]
#                    upStream = steepestPath[1]
#                    addChannelNode2Dict(NodesDict, curNode, downStream, upStream)
#                    downStream = curNode
#                    for idx in range(1,verNum):
#                        curNode =steepestPath[idx]
#                        if curNode != -1:
#                            if idx+1 < verNum and steepestPath[idx+1] != -1:
#                                upStream = steepestPath[idx+1]
#                                addChannelNode2Dict(NodesDict, curNode, downStream, upStream)
#                            else:
#                                upStream = None
#                                addChannelNode2Dict(NodesDict, curNode, downStream, upStream)
#                            downStream = curNode
#                        else:
#                            break
#    cleanNodeDict(NodesDict)

    
    

def backupChannelNodes(curNode,curCha,NodesDict,pts,channelList):
    curCha.append(pts[curNode])
    upNodes = NodesDict[curNode][1]
    if upNodes != [None]:
        if len(upNodes) == 1:
            curNode = upNodes[0]
            curCha.append(pts[curNode])
            backupChannelNodes(curNode,curCha,NodesDict,pts,channelList)
        else:
            channelList.append(curCha)
            for upNode in upNodes:
                curCha = []
                curCha.append(pts[curNode])
                backupChannelNodes(upNode,curCha,NodesDict,pts,channelList)
    else:
        channelList.append(curCha)