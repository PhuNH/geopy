#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 15:00:04 2019

@author: phunh
"""
import numpy as np
import cv2
from math import ceil

def open_raster_file(file_path, unchanged=True):
   """Open a raster file
   :param file_path: Path of the raster file or np array
   :param unchanged: Set to true to keep the original format
   """
   if isinstance(file_path, np.ndarray):
      return file_path
   flags = cv2.IMREAD_UNCHANGED if unchanged else -1
   image = cv2.imread(file_path, flags=flags)
   return image

def combine_images(input_images, shape, output_image):
   """Combine images in a mosaic
   :param input_images: Path to the input images
   :param shape: Shape of the mosaic in columns and rows
   :param output_image: Path to the output image mosaic
   """
   if len(input_images) != shape[0] * shape[1]:
      raise ValueError("Number of images doesn't match the mosaic shape.")
   images = []
   for item in input_images:
      images.append(open_raster_file(item))
   rows = []
   for row in range(shape[0]):
      start = row * shape[1]
      end = start + shape[1]
      rows.append(np.concatenate(images[start:end], axis=1))
   mosaic = np.concatenate(rows, axis=0)
   print mosaic
   print mosaic.shape
   cv2.imwrite(output_image, mosaic)
   
def adjust_values(input_image, output_image, img_range=None):
   """Create a visualization of the data in the input_image by projecting
   a range of values into a grayscale image
   :param input_image: Array containing the data or path to an image
   :param output_image: The image path to write the output
   :param img_range: Specified range of values or None to use
   the range of the image (minimum and maximum)
   """
   image = open_raster_file(input_image)
   min = img_range[0] if img_range else image.min()
   max = img_range[1] if img_range else image.max()
   interval = max - min
   factor = 256.0 / interval
   output = image * factor
   cv2.imwrite(output_image, output)
   
def crop_image(input_image, image_extent, bbox, output_image):
   """Crop an image by a bounding box.
   bbox and image_extent format: (xmin, ymin, xmax, ymax)
   :param input_image: Array containing the data or path to an image
   :param image_extent: The geographic extent of the image
   :param output_image: The image path to write the output
   :param bbox: The bounding box of the region of interest
   """
   input_image = open_raster_file(input_image)
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
   
   output = input_image[y_min:y_max, x_min:x_max]
   cv2.imwrite(output_image, output)
   
def create_hillshade(input_image, output_image, azimuth=90, angle_altitude=60):
   """Create a shaded relief image from a digital elevation model
   :param azimuth: Simulated sun azimuth
   :param angle_altitude: Sun altitude angle
   """
   input_image = open_raster_file(input_image)
   # gradients in 2 dimension x and y
   # gradients: first difference at ends, central difference at others
   x, y = np.gradient(input_image)
   slope = np.pi / 2 - np.arctan(np.sqrt(x*x + y*y))
   aspect = np.arctan2(-x, y)
   az_rad = azimuth * np.pi / 180
   alt_rad = angle_altitude * np.pi / 180
   a = np.sin(alt_rad) * np.sin(slope)
   b = np.cos(alt_rad) * np.cos(slope) * np.cos(az_rad - aspect)
   output = 255 * (a + b + 1) / 2
   cv2.imwrite(output_image, output)

if __name__ == '__main__':
#   image = open_raster_file('../../data/sample_image.tiff')
#   print(image) # OpenCV color byte order: B-G-R
#   print(type(image))
#   print(image.shape)
#   print(image.dtype)
   elevation_data = [
      '../../data/ASTGTM2_S22W048_dem.tif', '../../data/ASTGTM2_S22W047_dem.tif',
      '../../data/ASTGTM2_S23W048_dem.tif', '../../data/ASTGTM2_S23W047_dem.tif']
#   print("first")
#   print open_raster_file(elevation_data[0])
#   print("second")
#   print open_raster_file(elevation_data[1])
#   print("third")
#   print open_raster_file(elevation_data[2])
#   print("fourth")
#   print open_raster_file(elevation_data[3])
   output_img = '../output/mosaic.png'
#   combine_images(elevation_data, shape=(2,2), output_image=output_img)
#   image = open_raster_file(output_img)
#   print(image.min(), image.max())
   mosaic_grey_img = '../output/mosaic_grey.png'
#   adjust_values(output_img, mosaic_grey_img)
#   roi = (-46.8, -21.7, -46.3, -22.1) # region of interest
#   img_extent = (-48, -21, -46, -23)
   cropped_img = '../output/cropped.png'
#   crop_image(mosaic_grey_img, img_extent, roi, cropped_img)
   hillshade_img = '../output/hillshade.png'
   create_hillshade(cropped_img, hillshade_img)
   