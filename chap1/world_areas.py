#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 13:48:04 2019

@author: phunh
"""

from __future__ import print_function, division
from operator import itemgetter

import ogr
import osr

def open_shapefile(file_path):
   """Open the shapefile, get the first layer and returns the ogr datasource"""
   datasource = ogr.Open(file_path)
   layer = datasource.GetLayerByIndex(0)
   print("Opening {}".format(file_path))
   print("Number of features: {}".format(layer.GetFeatureCount()))
   return datasource

def transform_geometries(datasource, src_epsg, dst_epsg):
   """Transform the coordinates of all geometries in the first layer"""
   # Part 1
   src_srs = osr.SpatialReference()
   src_srs.ImportFromEPSG(src_epsg)
   dst_srs = osr.SpatialReference()
   dst_srs.ImportFromEPSG(dst_epsg)
   transformation = osr.CoordinateTransformation(src_srs, dst_srs)
   layer = datasource.GetLayerByIndex(0)
   
   # Part 2
   geoms = []
   layer.ResetReading()
   for feature in layer:
      geom = feature.GetGeometryRef().Clone()
      geom.Transform(transformation)
      geoms.append(geom)
   return geoms

def calculate_areas(geometries, unity='km2'):
   """Calculate the area for a list of ogr geometries"""
   # Part 1
   conversion_factor = {
      'sqmi': 2589988.11,
      'km2': 1000000,
      'm': 1}
   # Part 2
   if unity not in conversion_factor:
      raise ValueError("This unity is not defined: {}".format(unity))
   # Part 3
   areas = []
   for geom in geometries:
      area = geom.Area()
      areas.append(area / conversion_factor[unity])
   return areas

def get_country_names(datasource):
   """Return a list of country names"""
   layer = datasource.GetLayerByIndex(0)
   country_names = []
   layer.ResetReading()
   for feature in layer:
      country_names.append(feature.GetFieldAsString(4))
   return country_names

def get_biggest_countries(countries, areas, elements=5):
   """Return a list of n countries sorted by area size"""
   country_list = [list(country) for country in zip(areas, countries)]
   sorted_countries = sorted(country_list, key=itemgetter(0), reverse=True)
   return sorted_countries[:5]

datasource = open_shapefile("../data/world_borders_simple.shp")
#layer = datasource.GetLayerByIndex(0)
#feature = layer.GetFeature(0)
#print("Before transformation:", feature.GetGeometryRef())
transformed_geoms = transform_geometries(datasource, 4326, 3395)
#print("After transformation:", transformed_geoms[0])

calculated_areas = calculate_areas(transformed_geoms, unity='km2')
#print(calculated_areas[1])
#print(calculate_areas(transformed_geoms, unity='km2')[1])

country_names = get_country_names(datasource)
biggest_countries = get_biggest_countries(country_names, calculated_areas)
for item in biggest_countries:
   print("{}\t{}".format(item[0], item[1]))