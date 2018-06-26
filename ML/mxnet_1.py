# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 11:46:45 2018

@author: tzhou
"""

import mxnet as mx

def main():
    a = mx.nd.array([1])
    b = mx.nd.array([2])
    c = mx.nd.array([3])
    
    d = (a + b) * c
    print(d.asnumpy())
    print(d.asscalar())
    
if __name__ == '__main__':
    main()