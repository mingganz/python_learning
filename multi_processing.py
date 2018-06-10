# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 21:59:31 2018

@author: tzhou
"""

from multiprocessing  import Process

def run1():
    i = 0
    if i % 1000 == 0:
        print("run1...")
        i += 1
        
def run2():
    i = 0
    if i % 1000000000 == 0:
        print("run2...")
        i += 1
        
def main():
    processes = [Process(target = {f}) for f in (run1, run2)]
    for p in processes:
        p.start()
        p.join()
        
        
if __name__ == '__main__':
    main()
    print('running...')
    