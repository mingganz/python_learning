# -*- coding: utf-8 -*-
"""
Created on Sat May 26 21:34:08 2018

@author: tzhou
"""

#! /user/bin/env python

'readTextFile.py -- read and display text file'

#get filename
fname = input('Enter filename: ')

#attempt to open file for reading
try:
    fobj = open(fname, 'r')
except IOError:
    print('*** file open error')
else:
    #display contents to the screen
    for eachline in fobj:
        print(eachline, )
    fobj.close()