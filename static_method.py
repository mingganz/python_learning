# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 20:46:33 2018

@author: tzhou
"""

class staticClass:
    @staticmethod
    def f():
        print('static f')
        
    @classmethod
    def g(cls):
        print('class g: %s' % cls.__name__)
        
        
def main():
    staticClass.f()
    staticClass.g()
    
if __name__ == '__main__':
    main()