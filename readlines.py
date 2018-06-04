# -*- coding: utf-8 -*-
"""
Created on Mon May 28 20:55:44 2018

@author: tzhou
"""

f = open('b.txt', 'a+')

data = [line.strip() for line in f.readlines()]
print('Before adding new lines:')
for a in data:
     print(a)
#f.close()


#f = open('b.txt', 'a')
f.writelines('\n\tNiu Tingting\n')
#f.close()
print(f.tell())

f.seek(0)
#f = open('b.txt', 'r')
print('After adding new lines:')
data = [line.strip() for line in f.readlines()]
for a in data:
     print(a)
f.close()