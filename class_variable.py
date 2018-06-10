# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 21:19:16 2018

@author: tzhou
"""

class SortedKeyDict(dict):
    def keys(self):
        return sorted(super(SortedKeyDict, self).keys())
    
d = SortedKeyDict({'zheng-cai':54, 'hui-jun':67, 'Xen': 89})
print(d)
print(d.keys())
