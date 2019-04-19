#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:06:12 2019

@author: phunh
"""

print "I'm module_test.py and my name is: " + __name__

def function1():
   print "Hi, I'm inside function1"
   
if __name__ == '__main__':
   print "Calling function1 - only if I'm __main__..."
   function1()