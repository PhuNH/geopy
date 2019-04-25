#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 00:01:21 2019

@author: phunh
"""

import mapnik
from models import PointCollection, BoundaryCollection

class MapDatasource(mapnik.PythonDatasource):
   """Implement Mapnik's PythonDatasource
   """
   def __init__(self, data):
      print(data)
      data_type = mapnik.DataType.Vector
      if isinstance(data, PointCollection):
         geometry_type = mapnik.GeometryType.Point
      elif isinstance(data, BoundaryCollection):
         geometry_type = mapnik.GeometryType.Polygon
      else:
         raise TypeError
         
      super(MapDatasource, self).__init__(envelope=None,
           geometry_type=geometry_type, data_type=data_type)
      self.data = data
   
   def features(self, query=None):
      keys = ['name',]
      features = []
      for item in self.data.data:
         features.append([item.geom.wkb, {'name': item.name}])
      return mapnik.PythonDatasource.wkb_features(keys, features)