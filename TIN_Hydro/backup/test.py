# coding=utf-8
import os,sys
from ShapefileIO import *
from TINcreator import *

def findIntersectIdx(v,v0,A,B,C): ## v is three vertexes of a triangle, v0 is a point in the steepest descent vector
### the basic idea is OC=xOA+yOB, when x>0 and y>0, then OC is between OA and OB
    ##  intersect is the first point's index of the intersected edges
    for i in range(3):
        ## OA, OB vector
        o1 = [v[i][0]-v0[0],v[i][1]-v0[1]]
        o2 = [v[(i+1)%3][0]-v0[0],v[(i+1)%3][1]-v0[1]]
        ## if OA and OB are collinear?
        k  = o1[1]*o2[0]-o1[0]*o2[1]
        if k == 0:
            ## if deepest flow path vector (A/C, B/C) is also collinear?
            k1 = o1[1]*A/C - o1[0]*B/C
            k2 = o2[1]*A/C - o2[0]*B/C
            if k1==0 and k2==0:
                intersect = i
        else:
            m  = (o2[0]*B/C-o2[1]*A/C) / k
            if o2[0] != 0:
                n = (A/C-m*o1[0])/o2[0]
            else:
                n = (B/C-m*o1[1])/o2[1]
            if m > 0 and n > 0:
                intersect = i
    return intersect
def tranglePlane(p1,p2,p3):
    A = p1[1]*(p2[2]-p3[2])+p2[1]*(p3[2]-p1[2])+p3[1]*(p1[2]-p2[2]) ## A = y1(z2-z3)+y2(Z3-Z1)+y3(Z1-Z2)
    B = p1[2]*(p2[0]-p3[0])+p2[2]*(p3[0]-p1[0])+p3[2]*(p1[0]-p2[0]) ## B = Z1(x2-x3)+z2(x3-x1)+z3(x1-x2)
    C = p1[0]*(p2[1]-p3[1])+p2[0]*(p3[1]-p1[1])+p3[0]*(p1[1]-p2[1]) ## C = x1(y2-y3)+x2(y3-y1)+x3(y1-y2)
    D = -1*A*p1[0]-B*p1[1]-C*p1[2]                                  ## D = -Ax1-By1-Cz1
    #print A,B,C,D
    return (float(A),float(B),float(C),float(D))

if __name__ == '__main__':
    ####     INPUT        ####
    ptsShp = r'E:\research\TIN-based\20150811\flat_triangle_pts.shp'
    #elevField = "ELEV"
    elevField = "Z"
    workspace = r'E:\research\TIN-based\20150811'
    ####      END         ####
    
    ####  DEFAULT OUTPUT  ####
    preprocessing_pts = workspace + os.sep + 'flat_triangle_new_point.shp'
    tin_origin_Shp = workspace + os.sep + 'flat_triangle_tin_origin.shp'
    preprocessing_tin = workspace + os.sep + 'flat_triangle_tin_preprocessed.shp'
    steepestpath_Shp = workspace + os.sep + 'test_steepestpath.shp' 
    ####      END         ####
    
    #### GLOBAL VARIABLES ####
    VertexList = []          ## VertexList stores 3D coordinates (x,y,z) of all the input points
    TriangleVertexList = []  ## TriangleList stores all the triangles, each element stores index of vertexes
    TriangleNbrIdxList = []  ## TriangleNbrIdx stores index of triangle's neighbors, if there is not neighbor, set it None
    VertexTriangleList = []  ## VertexTriangleList stores every vertex's adjacent triangles in counterclockwise
    ####      END         ####
    
    ####  TEMP VARIABLES  ####
    pts2DList = []   ## temp list to store 2D coordinates of points
    
    ####      END         ####
    
    ####  MAIN FUNCTIONS  ####
    VertexList,pts2DList = ReadPoints(ptsShp,elevField)  ## Read input shapefile of points
    ## Ready to construct hydrological TIN
    ## 1. Create Delaunay Triangulated Irregular Network
    ## 2. Remove Flat triangle by insert additional point using an inverse distance weighted interpolation with quadratic nodal functions
    ## 3. Remove pit by using a recursive algorithm
    ## 4. Handle flat edges by fliping operation

    TriangleVertexList,TriangleNbrIdxList,VertexTriangleList,VertexList = createTIN(VertexList,pts2DList)
    #print VertexList[len(VertexList)-1]
    WritePointShp(VertexList,elevField,preprocessing_pts)
    WritePolyonShp(TriangleVertexList,VertexList,tin_origin_Shp)
    del pts2DList
    
    ###
#    flatTriangle = [] ## store vertexes index of flat triangles
#    for tri in TriangleVertexList:
#        p1 = VertexList[tri[0]]
#        p2 = VertexList[tri[1]]
#        p3 = VertexList[tri[2]]
#        if p1[2] == p2[2] and p2[2] == p3[2]:
#            flatTriangle.append(tri)
#            #flatTriangle.append(TriangleVertexList.index(tri))
#    print flatTriangle
#    for flatT in flatTriangle:
#        for flatV in flatT: 
#            ${0}
#    v = [[1,1,4],[1,-1,3],[-1,-1,2]]
#    A,B,C,D = tranglePlane(v[0],v[1],v[2])
#    print A,B,C,D
#    v0 = [1.,-1.,3.]
#    #v0 = [(v[0][0]+v[1][0]+v[2][0])/3.,(v[0][1]+v[1][1]+v[2][1])/3.,(v[0][2]+v[1][2]+v[2][2])/3.]
#    if C != 0: ## if C is 0, then the triangle is on the XY plane which need to be pitremoved!
#        intersect = findIntersectIdx(v,v0,A,B,C)
#        print intersect




###beifen###
#                fitPtsIdx = [] ## [[[,,]...],[[,,]...],[[,,]...]]
#                fitPtsIdx.append([tempPtsIdx[0]])
#                fitPtsIdx.append([tempPtsIdx[1]])
#                fitPtsIdx.append([tempPtsIdx[2]])
#                for i in range(3):
#                    tempVertex = f.vertex(i)
#                    cir_faces = dt.incident_faces(tempVertex)
#                    finites_faces = []
#                    f1 = cir_faces.next()
#                    if dt.is_infinite(f1) == False:
#                        finites_faces.append(f1)
#                    for f2 in cir_faces:
#                        if f2 == f1:
#                            break
#                        else:
#                            if dt.is_infinite(f2) == False:
#                                finites_faces.append(f2)
#                    for f2 in finites_faces:
#                        for j in range(3):
#                            fitPtsIdx[i].append(pts2DList.index([f2.vertex(j).point()[0],f2.vertex(j).point()[1]]))
#                fitPtsIdxUnique = []
#                for temp in fitPtsIdx:
#                    fitPtsIdxUnique.append(list(set(temp)))
#                print fitPtsIdxUnique
#                fitPtsCoor = []
#                for ptsIdx in fitPtsIdxUnique:
#                    tempPtsCoor = []
#                    for inividualIdx in ptsIdx:
#                        tempPtsCoor.append(pts[inividualIdx])
#                    fitPtsCoor.append(tempPtsCoor)
#                print fitPtsCoor
