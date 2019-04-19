#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 18:15:46 2019

@author: phunh
"""

import gdal
import os
from pprint import pprint
from utils.geo_functions import open_vector_file

class Geocache(object):
   """This class represents a single geocaching point
   """
   def __init__(self, lat, lon, attributes=None):
      self.lat = lat
      self.lon = lon
      self.attributes = attributes
      
   @property
   def coordinates(self):
      return self.lat, self.lon
   
class PointCollection(object):
   """This class represents a group of vector data
   """
   def __init__(self, file_path=None):
      self.data = []
      self.epsg = None
      
      if file_path:
         self.import_data(file_path)
         
   def __add__(self, other):
      self.data += other.data
      return self
   
   def import_data(self, file_path):
      """Open a vector file compatible with OGR and parse the data
      :param str file_path: The full path to the file
      """
      features, metadata = open_vector_file(file_path)
      self._parse_data(features)
      self.epsg = metadata['epsg']
      print("File imported: {}".format(file_path))
      
   def _parse_data(self, features):
      """Transform the data into Geocache objects
      :param features: A list of features
      """
      for feature in features:
         geom = feature['geometry']['coordinates']
         attributes = feature['properties']
         cache_point = Geocache(geom[0], geom[1], attributes = attributes)
         self.data.append(cache_point)
         
   def describe(self):
      print("SRS EPSG code: {}".format(self.epsg))
      print("Number of features: {}".format(len(self.data)))

if __name__ == "__main__":
   gpx_data = PointCollection("../data/geocaching.gpx")
   gpx_data.describe()
   shp_data = PointCollection("../data/geocaching.shp")
   shp_data.describe()
   merged_data = gpx_data + shp_data
   merged_data.describe()
