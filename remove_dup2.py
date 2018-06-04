# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 21:56:28 2018

@author: tzhou
"""

def dedupe2(items, key=None):
    seen = set()
    for item in items:
        val = item if key==None else key(item)
        if val not in seen:
            yield item
            seen.add(val)
            
if __name__ == '__main__':
    a =[{'x':1, 'y':2}, {'x':1, 'y':2}, {'x':1, 'y':3}, {'x':2, 'y':1}]
    b = list(dedupe2(a, key = lambda d: (d['x'], d['y'])))
    print(b)