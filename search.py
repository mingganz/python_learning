# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 08:11:39 2018

@author: tzhou
"""

import re

pattern = '\.c' 
in_file = 'log.txt'
out_f = None

with open(in_file, 'r') as f:
    all_lines = f.readlines()
    f.close()
    
    for line in all_lines:
       result = re.search(pattern, line)
       if (None != result):
           print(line)
           if(None == out_f):
               try:
                   out_f = open(in_file + '.out', 'a')
               except IOError:
                   print("Open file for output failed")
                   break
           out_f.write(line)
           