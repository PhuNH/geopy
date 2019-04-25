#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:08:55 2019

@author: phunh
"""

from utils.geo_functions import transform_points
from models import PointCollection, BoundaryCollection

import numpy as np
import math

class GeocachingApp(object):
   def __init__(self, geocaching_file=None, boundary_file=None, my_location=None):
      """Application class
      :param geocaching_file: An OGR compatible file with geocaching points
      :param boundary_file: A file with boundaries
      :param my_location: Coordinates of your location
      """
      self.geocaching_data = PointCollection(geocaching_file)
      self.boundaries = BoundaryCollection(boundary_file)
      self._my_location = None
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
   
   def filter_by_country(self, name):
      """Filter by a country with a given name
      :param name: The name of the boundary (ex. country name)
      :return: PointCollection
      """
      boundary = self.boundaries.get_by_name(name)
      return self.geocaching_data.filter_by_boundary(boundary)

if __name__ == "__main__":
   geocaching_file = '../data/geocaching.gpx'
   boundary_file = '../data/world_borders_simple.shp'
   # geocaching_file, [-73.0, 43.0]
   my_app = GeocachingApp(geocaching_file, boundary_file)
   result = my_app.filter_by_country('United States')
   print(result)