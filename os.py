# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 22:56:30 2018

@author: tzhou
"""
import os 

def main():
    for root, dirs, files in os.walk('./'):
        for filename in files:
            filepath = os.sep.join([root, filename])
            dirname = root.split(os.sep)[-1]
            print('{}: {}, {}'.format(filepath, dirname, filename))
    
if __name__ == '__main__':
    main()