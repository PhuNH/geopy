#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:14:32 2019

@author: phunh
"""

from pprint import pprint
import requests
from os import path

def request_api_methods():
   url = "https://www.opencaching.de/okapi/services/apiref/method_index"
   result = requests.get(url)
   pprint(result.json())
   
def download_data(base_url, data_path, data_filename):
   save_file_path = path.join(data_path, data_filename)
   request = requests.get(base_url, stream=True)
   
   # Check if the file exists
   if path.isfile(save_file_path):
      print('File already available')
   
   # Save the download to the disk
   with open(save_file_path, 'wb') as save_file:
      for chunk in request.iter_content(1024):
         save_file.write(chunk)
         
if __name__ == "__main__":
   #request_api_methods()
   download_data('https://s3.amazonaws.com/geopy/geocaching.gpx',
                  '../../data',
                  'geocaching_test.gpx')