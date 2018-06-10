# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 21:14:57 2018

@author: tzhou
"""

def main():
    iter_odd = (x for x in range(1, 6) if x % 2)
    print (type(iter_odd))
    iter_odd = {x for x in range(1, 6) if x % 2}
    print (type(iter_odd))
    iter_odd = {x: x for x in range(1, 6) if x % 2}
    print (type(iter_odd))
    
if __name__ == '__main__':
    main()