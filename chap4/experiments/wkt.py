#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 02:36:48 2019

@author: phunh
"""
"""
import ogr

wkt_rectangle = "POLYGON ((1 1, 1 9, 8 9, 8 1, 1 1))"
geometry = ogr.CreateGeometryFromWkt(wkt_rectangle)
print(geometry.__class__)
print(geometry.Area())
print(8*7)

wkt_rectangle2 = "POLYGON ((1 1, 8 1, 8 9, 1 9, 1 1), (4 2, 7 2, 7 5, 4 5, 4 2))"
geometry2 = ogr.CreateGeometryFromWkt(wkt_rectangle2)
print(geometry2.__class__)
print(geometry2.Area())
print(8*7 - 3*3)
"""

from shapely.geometry import Polygon

print('Example with Shapely')
polygon1 = Polygon([(1, 1), (8, 1), (8, 9), (1, 9), (1, 1)])
print(polygon1.__class__)
print(polygon1.area)

polygon2 = Polygon([(1, 1), (8, 1), (8, 9), (1, 9), (1, 1)],
                    [[(4, 2), (7, 2), (7, 5), (4, 5), (4, 2)]])
print(polygon2.__class__)
print(polygon2.area)