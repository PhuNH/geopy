#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:08:55 2019

@author: phunh
"""

from utils.geo_functions import open_vector_file, transform_points, transform_geometries

import numpy as np
import math

class GeocachingApp(object):
   def __init__(self, data_file=None, my_location=None):
      """Application class
      :param data_file: An OGR compatible file with geocaching points
      :param my_location: Coordinates of your location
      """
      # Part 1
      self._datasource = None
      self._transformed_geoms = None
      self._my_location = None
      self.distances = None
      
      # Part 2
      if data_file:
         self.open_file(data_file)
      if my_location:
         self._my_location = my_location
         
   @property
   def my_location(self):
      return self._my_location
   
   @my_location.setter
   def my_location(self, coordinates):
      self._my_location = transform_points([coordinates])[0]
         
   def open_file(self, file_path):
      """Open a file containing geocaching data and prepare it for use
      :param file_path:
      """
      self._datasource = open_vector_file(file_path)
      self._transformed_geoms = transform_geometries(self._datasource, 4326, 3395)

   def calculate_distances(self):
      """Calculate the distance between a set of points and a give location
      :return: A list of distances in the same order as the points
      """
      xa = self.my_location[0]
      ya = self.my_location[1]
      points = self._transformed_geoms
      distances = []
      for geom in points:
         point_distance = math.sqrt((geom.GetX() - xa)**2 + (geom.GetY() - ya)**2)
         distances.append(point_distance)
      return distances
   
   def find_closest_point(self):
      """Find the closest point to a given location and return the cache that's on the point
      :return: OGR feature containing the point
      """
      # Part 1
      distances = self.calculate_distances()
      index = np.argmin(distances)
      
      # Part 2
      layer = self._datasource.GetLayerByIndex(0)
      feature = layer.GetFeature(index)
      print "Closest point at: {}m".format(distances[index])
      return feature

if __name__ == "__main__":
   my_app = GeocachingApp('../data/geocaching.gpx', [-73.0, 43.0])
   my_app.find_closest_point()