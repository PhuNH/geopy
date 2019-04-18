#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 17:20:21 2019

@author: phunh
"""

from __future__ import print_function

import mapnik
import cv2

def display_map(image_file):
   """Open and display a map image file
   :param image_file: Path to the image
   """
   image = cv2.imread(image_file)
   cv2.imshow('image', image)
   cv2.waitKey(0)
   cv2.destroyAllWindows()

def create_map(shapefile, gpx_file, style_file, output_image, size=(800, 600)):
   """Create a map from an XML file and write it to an image
   :param shapefile: Shapefile containing the data for the map
   :param gpx_file: geocaching points
   :param style_file: Mapnik XML file
   :param output_image: Name of the output image file
   :param size: Size of the map in pixels
   """
   # a tuple or list is unpacked with the * symbol into an argument of Map
   map = mapnik.Map(*size)
   mapnik.load_map(map, style_file)
   layers = map.layers
   
   # Add the shapefile
   shp_source = mapnik.Shapefile(file=shapefile)
   # Check for methods of a Shapefile object
#   object_methods = [method_name for method_name in dir(data_source) if callable(getattr(data_source, method_name))]
#   print(object_methods)
   world_layer = mapnik.Layer('world')
   world_layer.datasource = shp_source
   world_layer.styles.append('style1')
   layers.append(world_layer)
#   print(layer)
#   print(layer.name)
#   print(layer.datasource)
   #print(map.layers[0].datasource)
   
   # Add the points
   pt_source = mapnik.Ogr(file=gpx_file, layer='waypoints')
   pt_layer = mapnik.Layer('geocaching_points')
   pt_layer.datasource = pt_source
   pt_layer.styles.append('style2')
   layers.append(pt_layer)
   
   map.zoom_all()
   mapnik.render_to_file(map, output_image)
   
if __name__ == '__main__':
   map_image = '../output/world_multi_ds.png'
   shp_src = '../../data/world_borders_simple.shp'
   gpx_src = '../../data/geocaching.gpx'
   style_file = 'map_style.xml'
   create_map(shp_src, gpx_src, style_file, map_image, size=(1024,500))
   display_map(map_image)
   