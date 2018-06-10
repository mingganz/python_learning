# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 20:37:08 2018

@author: tzhou
"""

def fibonacci(n):
    a = 0
    b = 1
    while b < n:
        yield b
        a, b = b, a + b
    else:
        return 'NO more ...'
    
if __name__ == '__main__':
    a = fibonacci(3)
    print(next(a))
    print(next(a))
    print(next(a))
    print(next(a))
    