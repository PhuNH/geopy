#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 22:58:06 2019

@author: phunh
"""

import ogr

# Open the shapefile and get the first layer
datasource = ogr.Open("../data/world_borders_simple.shp")
layer = datasource.GetLayerByIndex(0)
print("Number of feature: {}".format(layer.GetFeatureCount()))

# Inspect the fields available in the layer
feature_def = layer.GetLayerDefn()
for field_index in range(feature_def.GetFieldCount()):
   field_def = feature_def.GetFieldDefn(field_index)
   print("\t{}\t{}\t{}".format(field_index, field_def.GetTypeName(), field_def.GetName()))

# Print a list of country names
layer.ResetReading()
for feature in layer:
   print(feature.GetFieldAsString(4))