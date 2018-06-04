# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 21:27:35 2018

@author: tzhou
"""

def dedupe(items):
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)
            
if __name__ == '__main__':
    a = [1, 5, 2, 1, 9, 1, 5, 10]
    b = list(dedupe(a))
    print(b)