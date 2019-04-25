#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 18:15:46 2019

@author: phunh
"""

from __future__ import print_function
from shapely.geometry import Point, mapping
from shapely import wkb, wkt
import json
from utils.geo_functions import open_vector_file
from utils.geo_functions import transform_geometry, convert_length_unit

class BaseGeoObject(object):
   """Base class for a single geo object
   """
   def __init__(self, geometry, attributes=None):
      self.geom = geometry
      self.attributes = attributes
      self.wm_geom = None
      
      #Make a lookup table of case insensitive attributes
      self._attributes_lowercase = {}
      for key in self.attributes.keys():
         self._attributes_lowercase[key.lower()] = key
      
   def __repr__(self):
      raise NotImplementedError
      
   @property
   def coordinates(self):
      raise NotImplementedError
      
   def transformed_geom(self):
      """Return the geometry transformed into WorldMercator coordinate system
      """
      if not self.wm_geom:
         geom = transform_geometry(self.geom.wkb)
         self.wm_geom = wkb.loads(geom)
      return self.wm_geom
      
   def get_attribute(self, attr_name, case_sensitive=False):
      """Get an attribute by its name
      :param attr_name: The name of the attribute
      :param case_sensitive: True or False
      """
      if not case_sensitive:
         attr_name = attr_name.lower()
         attr_name = self._attributes_lowercase[attr_name]
      return self.attributes[attr_name]
   
   def export_geojson_feature(self):
      """Export this object as dictionary formatted as a GeoJSON feature
      """
      feature = {
         "type": "Feature",
         "geometry": mapping(self.geom),
         "properties": self.attributes}
      return feature

class Geocache(BaseGeoObject):
   """This class represents a single geocaching point
   """
   def __init__(self, geometry, attributes=None):
      super(Geocache, self).__init__(geometry, attributes)
      
   def __repr__(self):
      name = self.attributes.get('name', 'Unnamed')
      return "{} {} - {}".format(self.geom.x, self.geom.y, name)
   
class LineString(BaseGeoObject):
   """This class represents a single linestring
   """
   def length(self, unit='km'):
      """Convenience method that returns the length
      of the linestring in a given unit
      :param unit: The desired output unit
      """
      return convert_length_unit(self.transformed_geom().length, unit)
      
   def __repr__(self):
      unit = 'km'
      length = self.length(unit)
      return "{} ({} {})".format(self.get_attribute('name'), length, unit)
   
class Boundary(BaseGeoObject):
   """Represent a single geographic Boundary"""
   def __repr__(self):
      return self.get_attribute('name')
   
class BaseGeoCollection(object):
   """This class represents a collection of spatial data
   """
   def __init__(self, file_path=None):
      self.data = []
      self.epsg = None
      
      if file_path:
         self.import_data(file_path)
         
   def __add__(self, other):
      self.data += other.data
      return self
   
   def _parse_data(self, features):
      """Transform the data into BaseGeoObject objects
      :param features: A list of features
      """
      raise NotImplementedError
         
   def import_data(self, file_path):
      """Open a vector file compatible with OGR and parse the data
      :param str file_path: The full path to the file
      """
      features, metadata = open_vector_file(file_path)
      self._parse_data(features)
      self.epsg = metadata['epsg']
      print("File imported: {}".format(file_path))
      
   def describe(self):
      print("SRS EPSG code: {}".format(self.epsg))
      print("Number of features: {}".format(len(self.data)))
   
   def get_by_name(self, name):
      """Find an object by its name attribute and return it
      """
      for item in self.data:
         if item.get_attribute('name') == name:
            return item
      raise LookupError("Object not found with the name: {}".format(name))
      
   def filter_by_boundary(self, boundary):
      """Filter the data by a given boundary
      """
      result = []
      for item in self.data:
         if item.geom.within(boundary.geom):
            result.append(item)
      return result
   
   def filter(self, attribute, value):
      """Filter the collection by an attribute
      :param attribute: The name of the attribute to filter by
      :param value: The filtering value
      """
      result = self.__class__()
      for item in self.data:
         if item.get_attribute(attribute) == value:
            result.data.append(item)
      return result
   
   def export_geojson(self, file):
      """Export the collection to a GeoJSON file
      """
      features = [i.export_geojson_feature() for i in self.data]
      geojson = {
         "type": "FeatureCollection",
         "features": features}
      with open(file, 'w') as out_file:
         json.dump(geojson, out_file, indent=2)
      print("File exported: {}".format(file))
      
class PointCollection(BaseGeoCollection):
   """This class represents a group of vector data
   """
   def _parse_data(self, features):
      """Transform the data into Geocache objects
      :param features: A list of features
      """
      for feature in features:
         coords = feature['geometry']['coordinates']
         point = Point(float(coords[1]), float(coords[0]))
         attributes = feature['properties']
         cache_point = Geocache(point, attributes = attributes)
         self.data.append(cache_point)
         
class LineStringCollection(BaseGeoCollection):
   """This class represents a collection of linestrings
   """
   def _parse_data(self, features):
      for feature in features:
         geom = feature['geometry']['coordinates']
         attributes = feature['properties']
         line = wkt.loads(geom)
         linestring = LineString(geometry=line, attributes=attributes)
         self.data.append(linestring)
         
class BoundaryCollection(BaseGeoCollection):
   """This class represents a collection of geographic boundaries
   """
   def _parse_data(self, features):
      for feature in features:
         geom = feature['geometry']['coordinates']
         attributes = feature['properties']
         polygon = wkt.loads(geom)
         boundary = Boundary(geometry=polygon, attributes=attributes)
         self.data.append(boundary)
         
if __name__ == "__main__":
   gpx_data = PointCollection("../data/geocaching.gpx")
   gpx_data.describe()
#   shp_data = PointCollection("../data/geocaching.shp")
#   shp_data.describe()
#   merged_data = gpx_data + shp_data
#   merged_data.describe()
#   world = BoundaryCollection("../data/world_borders_simple.shp")
#   for item in world.data:
#      print(item)
#   print(world.data[0].attributes.keys())
#   usa_roads = LineStringCollection('../data/roads.shp')
#   for item in usa_roads.data:
#      print(item)
#   print(world.get_by_name('Brazil'))
#   usa_boundary = world.get_by_name('United States')
#   result = gpx_data.filter_by_boundary(usa_boundary)
#   for item in result:
#      print(item)
#   result = gpx_data.filter('difficulty', '1').filter('container', 'Virtual')
#   result = gpx_data.filter('difficulty', '1') + gpx_data.filter('difficulty', '2')
#   result.describe()
   gpx_data.export_geojson("output/data.json")