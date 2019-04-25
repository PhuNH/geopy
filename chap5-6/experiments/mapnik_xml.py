#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 17:17:08 2019

@author: phunh
"""

import mapnik

map = mapnik.Map(800, 600)
mapnik.load_map(map, 'map_style.xml')
map.zoom_all()
mapnik.render_to_file(map, '../output/world_xml.png')