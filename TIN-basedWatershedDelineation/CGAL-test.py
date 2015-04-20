#! /usr/bin/env python
#coding=utf-8
from CGAL.Triangulations_2 import *
from CGAL.Kernel import Point_2
dt = Triangulation_2()
Pts = [Point_2(0,0),Point_2(1,0),Point_2(0,1),Point_2(1,1)]
for p in Pts:
    dt.insert(p)
print dt.number_of_vertices(),dt.number_of_faces()