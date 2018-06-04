# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 21:18:55 2018

@author: tzhou
"""
import remove_dup

a = {
     'x':1,
     'y':2,
     'z':3
}

b = {
     'w':10,
     'x':11,
     'y':2
}

# Find keys in common
c = a.keys() & b.keys()
print(c)

d = a.keys() - b.keys()
print(d)

e = a.items() & b.items()
print(e)

f = {key:a[key] for key in a.keys() - {'z', 'w'}}
print(f)
print(__name__)