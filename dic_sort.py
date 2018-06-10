# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 20:22:44 2018

@author: tzhou
"""

from collections import OrderedDict
import json

d = OrderedDict()
d['foo'] = 1
d['bar'] = 2
d['spam'] = 3
d['grok'] = 4

for key in d:
    print(key, d[key])

j = json.dumps(d)
print(j)