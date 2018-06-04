# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#! /usr/bin/env python
'makeTextFile.py -- create text file'

import os
ls = os.linesep

#get filename
fname = input("Pleaes input a new file name: ")
while True:
    if os.path.exists(fname):
        print("ERROR: '%s' already exists" % fname)
    else:
        break
    
#get file content (text) lines
all = []
print("Enter lines('.' by itself to quit).")

#loop until user terminates input
while True:
    entry = input('> ')
    if entry == '.':
        break
    else:
        all.append(entry)
        
# Write lines to file with proper line-ending
fobj = open(fname, 'w')
fobj.writelines(['%s%s' % (x, ls) for x in all])
fobj.close()
print("DONE!")

