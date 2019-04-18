#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 00:01:21 2019

@author: phunh
"""

import mapnik

class MapDataSource(mapnik.PythonDatasource):
   """Implement Mapnik's PythonDatasource
   """
   def features(self, query=None):
      