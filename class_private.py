# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 20:43:09 2018

@author: tzhou
"""

class A:
    __version = 1.0
    def __init__(self):
        self.__myname= 'A'
    def __func(self):
        print(self.__myname)
        
class B(A):
    def f(self):
        self._A__func()
        print('version is %d ' % self._A__version)
        
def main():
    b = B()
    b.f()
    
if __name__ == '__main__':
    main()