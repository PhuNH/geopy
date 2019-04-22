#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 02:22:08 2019

@author: phunh
"""

import cv2
import mapnik
import platform
import tempfile
from models import BoundaryCollection, PointCollection
from map_maker.my_datasource import MapDatasource

class MapMakerApp(object):
   def __init__(self, output_image="output/map.png",
                style_file="map_maker/styles.xml",
                map_size=(800, 600)):
      """Application class
      :param output_image: Path to the image output of the map
      :param style_file: Mapnik XML file containing only the style for the map
      :param map_size: Size of the map in pixels
      """
      self.output_image = output_image
      self.style_file = style_file
      self.map_size = map_size
      self._layers = {}
      
   def display_map(self):
      """Open and display a map image file
      """
      image = cv2.imread(self.output_image)
      cv2.imshow('image', image)
      cv2.waitKey(0)
      cv2.destroyAllWindows()
      
   def create_map(self):
      """Create a map and write it to an image file
      """
      # a tuple or list is unpacked with the * symbol into an argument of Map
      map = mapnik.Map(*self.map_size)
      mapnik.load_map(map, self.style_file)
      layers = map.layers
      for name, layer in self._layers.iteritems():
         new_layer = mapnik.Layer(name)
         new_layer.datasource = layer["data_source"]
         new_layer.styles.append(layer['style'])
         layers.append(new_layer)
         
      map.zoom_all()
      mapnik.render_to_file(map, self.output_image)
      
   def add_layer(self, geo_data, name, style='style1'):
      """Add data to the map to be displayed in a layer with a given style
      :param geo_data: a BaseGeoCollection subclass instance
      """
      if platform.system() == "Windows":
         print("Windows system")
      #else:
         #data_source = mapnik.Python(factory='MapDatasource', data='geo_data')
      temp_file, filename = tempfile.mkstemp(dir="temp")
      geo_data.export_geojson(filename)
      data_source = mapnik.GeoJSON(file=filename)
      
      layer = {
         "data_source": data_source,
         "data": geo_data,
         "style": style}
      self._layers[name] = layer
      
if __name__ == '__main__':
   shp_file = '../data/world_borders_simple.shp'
   #gpx_src = '../data/geocaching.gpx'
   world_borders = BoundaryCollection(shp_file)
   countries = world_borders.filter('name', 'Brazil') +\
               world_borders.filter('name', 'Russia') +\
               world_borders.filter('name', 'India') +\
               world_borders.filter('name', 'China')
   map_app = MapMakerApp()
   map_app.add_layer(countries, 'countries')
   map_app.create_map()
   map_app.display_map()