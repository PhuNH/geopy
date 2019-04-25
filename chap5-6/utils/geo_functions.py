#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:38:35 2019

@author: phunh
"""

import ogr
import osr
import gdal
import os
import xmltodict
from pprint import pprint

def read_gpx_file(file_path):
   """Read a GPX file containing geocaching points
   :param str file_path: The full path to the file
   """
   with open(file_path) as gpx_file:
      gpx_dict = xmltodict.parse(gpx_file.read())
#   print("Waypoint:")
#   print(gpx_dict['gpx']['wpt'][0].keys())
#   print("Geocache:")
#   print(gpx_dict['gpx']['wpt'][0]['geocache'].keys())
   output = []
   for wpt in gpx_dict['gpx']['wpt']:
      geometry = [wpt.pop('@lat'), wpt.pop('@lon')]
      # If geocache is not on the dict, skip this wpt
      try:
         geocache = wpt.pop('geocache')
      except KeyError:
         continue
      attributes = {'status': geocache.pop('@status')}
      # Merge the dictionaries
      attributes.update(wpt)
      # Some properties are overwritten
      attributes.update(geocache)
      # Construct a GeoJSON feature and append to the list
      feature = {
         "type": "Feature",
         "geometry": {
            "type": "Point",
            "coordinates": geometry},
         "properties": attributes}
      output.append(feature)
   return output

def read_ogr_features(layer):
   """Convert OGR features from a layer into dictionaries
   :param layer: OGR layer
   """
   features = []
   layer_defn = layer.GetLayerDefn()
   layer.ResetReading()
   type = ogr.GeometryTypeToName(layer.GetGeomType())
   for item in layer:
      attributes = {}
      for index in range(layer_defn.GetFieldCount()):
         field_defn = layer_defn.GetFieldDefn(index)
         key = field_defn.GetName()
         value = item.GetFieldAsString(index)
         attributes[key] = value
      feature = {
         "type": "Feature",
         "geometry": {
            "type": type,
            "coordinates": item.GetGeometryRef().ExportToWkt()},
         "properties": attributes}
      features.append(feature)
   return features

def get_datasource_information(datasource, print_results=False):
   """Get information about the first layer in the datasource
   :param datasource: An OGR datasource
   :param bool print_results: True to print the results on the screen
   """
   info = {}
   layer = datasource.GetLayerByIndex(0)
   bbox = layer.GetExtent()
   # bounding box: upper-left and lower-right
   info['bbox'] = dict(xmin=bbox[0], xmax=bbox[1], ymin=bbox[2], ymax=bbox[3])
   srs = layer.GetSpatialRef()
   if srs:
      info['epsg'] = srs.GetAttrValue('authority', 1)
   else:
      info['epsg'] = 'not available'
   info['type'] = ogr.GeometryTypeToName(layer.GetGeomType())
   # Get the attributes names
   info['attributes'] = []
   layer_definition = layer.GetLayerDefn()
   for index in range(layer_definition.GetFieldCount()):
      info['attributes'].append(layer_definition.GetFieldDefn(index).GetName())
   # Print the results
   if print_results:
      pprint(info)
   return info

def open_vector_file(file_path):
   """Open a vector file compatible with OGR or a GPX file.
   Return a list of features and information about the file
   :param str file_path: The full path to the file
   """
   datasource = ogr.Open(file_path)
   # Check if the file was opened
   if not datasource:
      if not os.path.isfile(file_path):
         message = "Wrong path"
      else:
         message = "File format is invalid"
      raise IOError('Error opening the file {}\n{}'.format(file_path, message))
   
   metadata = get_datasource_information(datasource)
   file_name, file_extension = os.path.splitext(file_path)
   # Check if it's a GPX and read it if so
   if file_extension.lower() == '.gpx':
      features = read_gpx_file(file_path)
   # If not, use OGR to get the features
   else:
      features = read_ogr_features(datasource.GetLayerByIndex(0))
   return features, metadata

def convert_length_unit(value, unit='km', decimal_places=2):
   """Convert the length unit of a given value.
   The input is in meters and the output is set by the unit argument
   :param value: Input value in meters
   :param unit: The desired output unit
   :param decimal_places: Number of decimal places of the output
   """
   conversion_factor = {
      'mi': 0.000621371192,
      'km': 0.001,
      'm': 1.0}
   
   if unit not in conversion_factor:
      raise ValueError("This unit is not defined: {}".format(unit))
   
   return round(value * conversion_factor[unit], decimal_places)

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

def create_transform(src_epsg, dst_epsg):
   """Create an OSR transformation
   :param src_epsg: EPSG code for the source geometry
   :param dst_epsg: EPSG code for the destination geometry
   :return: osr.CoordinateTransformation
   """
   src_srs = osr.SpatialReference()
   src_srs.ImportFromEPSG(src_epsg)
   dst_srs = osr.SpatialReference()
   dst_srs.ImportFromEPSG(dst_epsg)
   return osr.CoordinateTransformation(src_srs, dst_srs)

def transform_points(points, src_epsg=4326, dst_epsg=3395):
   """Transform the coordinate reference system of a list of coordinates (a list of points)
   :param src_epsg: EPSG code for the source geometry
   :param dst_epsg: EPSG code for the destination geometry
   """
   transformation = create_transform(src_epsg, dst_epsg)
   points = transformation.TransformPoints(points)
   return points

def transform_geometries(datasource, src_epsg, dst_epsg):
   """Transform the coordinates of all geometries in the first layer"""
   # Part 1
   transformation = create_transform(src_epsg, dst_epsg)
   layer = datasource.GetLayerByIndex(0)
   
   # Part 2
   geoms = []
   layer.ResetReading()
   for feature in layer:
      geom = feature.GetGeometryRef().Clone()
      geom.Transform(transformation)
      geoms.append(geom)
   return geoms

def transform_geometry(geom, src_epsg=4326, dst_epsg=3395):
   """Transform a single wkb geometry
   :param geom: wkb geom
   :param src_epsg: EPSG code for the source geometry
   :param dst_epsg: EPSG code for the destination geometry
   """
   ogr_geom = ogr.CreateGeometryFromWkb(geom)
   ogr_transformation = create_transform(src_epsg, dst_epsg)
   ogr_geom.Transform(ogr_transformation)
   return ogr_geom.ExportToWkb()

if __name__ == "__main__":
   shp_file = "../../data/geocaching.shp"
   gpx_file = "../../data/geocaching.gpx"
   # Suppress warnings about empty date fields in features
   #gdal.PushErrorHandler('CPLQuietErrorHandler')
   points, metadata = open_vector_file(shp_file)
   print points[0]['properties'].keys()
   points, metadata = open_vector_file(gpx_file)
   print points[0]['properties'].keys()
