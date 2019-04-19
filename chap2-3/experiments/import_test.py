#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:05:52 2019

@author: phunh
"""

print "I'm import_test.py and my name is: " + __name__

print "Importing module_test"
import module_test

print "Calling function1 from within import_test"
module_test.function1()