# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 19:41:02 2018

@author: tzhou
"""

class P:
    def __del__(self):
        print('P: delete')

class C(P):
    def __del__(self):
        P.__del__(self)
        print('C: delete')
        
def main():
    c1 = C()
    c2 = c1
    c3 = c1
    
    print('del c1')
    del c1
    print('del c2')
    del c2
    print('del c3')
    del c3
    
if __name__ == '__main__':
    main()