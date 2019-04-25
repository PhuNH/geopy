#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 01:40:31 2019

@author: phunh
"""

import cv2
import numpy as np
from math import ceil

class RasterData(object):
   def __init__(self, input_data, unchanged=True, shape=None):
      """Represent a raster data in the form of an array
      :param input_data: Raster files or Numpy array
      :param unchanged: True to keep the original format
      :param shape: When using multiple input data,
      this determines the shape of the composition
      """
      self.data = None
      if isinstance(input_data, list) or isinstance(input_data, tuple):
         self.combine_images(input_data, shape)
      else:
         self.import_data(input_data, unchanged)
         
   def import_data(self, image, unchanged=True):
      """Open a raster file
      :param image: Path of the raster file or np array
      :param unchanged: Set to true to keep the original format
      """
      if isinstance(image, np.ndarray):
         self.data = image
         return image
      flags = cv2.IMREAD_UNCHANGED if unchanged else -1
      self.data = cv2.imread(image, flags=flags)
      
   def write_image(self, output_image):
      """Write the data to an image
      :param output_image: Path and name of the output image
      """
      cv2.imwrite(output_image, self.data)
      return self
   
   def combine_images(self, input_images, shape):
      """Combine images in a mosaic
      :param input_images: Path to the input images
      :param shape: Shape of the mosaic in columns and rows
      :param output_image: Path to the output image mosaic
      """
      if len(input_images) != shape[0] * shape[1]:
         raise ValueError("Number of images doesn't match the mosaic shape.")
      images = []
      for item in input_images:
         if isinstance(item, RasterData):
            images.append(item.data)
         else:
            images.append(RasterData(item).data)
      rows = []
      for row in range(shape[0]):
         start = row * shape[1]
         end = start + shape[1]
         rows.append(np.concatenate(images[start:end], axis=1))
      mosaic = np.concatenate(rows, axis=0)
      self.data = mosaic
      return self
   
   def adjust_values(self, img_range=None):
      """Create a visualization of the data in the input_image by projecting
      a range of values into a grayscale image
      :param img_range: Specified range of values or None to use
      the range of the image (minimum and maximum)
      """
      image = self.data
      min = img_range[0] if img_range else image.min()
      max = img_range[1] if img_range else image.max()
      interval = max - min
      factor = 256.0 / interval
      self.data = image * factor
      return self
      
   def crop_image(self, image_extent, bbox):
      """Crop an image by a bounding box.
      bbox and image_extent format: (xmin, ymin, xmax, ymax)
      :param image_extent: The geographic extent of the image
      :param bbox: The bounding box of the region of interest
      """
      input_image = self.data
      img_shape = input_image.shape
      img_geo_width = abs(image_extent[2] - image_extent[0])
      img_geo_height = abs(image_extent[3] - image_extent[1])
      
      # How many pixels are contained in one geographic unit
      pixel_width = img_shape[1] / img_geo_width
      pixel_height = img_shape[0] / img_geo_height
      
      # Index of the pixel to cut
      x_min = int(ceil(abs(bbox[0] - image_extent[0]) * pixel_width))
      x_max = int(ceil(abs(bbox[2] - image_extent[0]) * pixel_width))
      y_min = int(ceil(abs(bbox[1] - image_extent[1]) * pixel_height))
      y_max = int(ceil(abs(bbox[3] - image_extent[1]) * pixel_height))
      
      self.data = input_image[y_min:y_max, x_min:x_max]
      return self
      
   def create_hillshade(self, azimuth=90, angle_altitude=60):
      """Create a shaded relief image from a digital elevation model
      :param azimuth: Simulated sun azimuth
      :param angle_altitude: Sun altitude angle
      """
      input_image = self.data
      # gradients in 2 dimension x and y
      # gradients: first difference at ends, central difference at others
      x, y = np.gradient(input_image)
      slope = np.pi / 2 - np.arctan(np.sqrt(x*x + y*y))
      aspect = np.arctan2(-x, y)
      az_rad = azimuth * np.pi / 180
      alt_rad = angle_altitude * np.pi / 180
      a = np.sin(alt_rad) * np.sin(slope)
      b = np.cos(alt_rad) * np.cos(slope) * np.cos(az_rad - aspect)
      self.data = 255 * (a + b + 1) / 2
      return self
   
if __name__ == '__main__':
   elevation_data = [
      '../../data/ASTGTM2_S22W048_dem.tif', '../../data/ASTGTM2_S22W047_dem.tif',
      '../../data/ASTGTM2_S23W048_dem.tif', '../../data/ASTGTM2_S23W047_dem.tif']
   roi = (-46.8, -21.7, -46.3, -22.1) # region of interest
   img_extent = (-48, -21, -46, -23)
   pipeline_output = '../output/pipeline.png'
   RasterData(elevation_data, shape=(2,2)).adjust_values()\
      .crop_image(img_extent, roi).create_hillshade().write_image(pipeline_output)
      