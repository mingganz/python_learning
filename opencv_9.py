# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 22:40:05 2018

@author: tzhou
"""

import numpy as np
import cv2

def main():
    canvas = np.zeros((400, 600, 3), dtype=np.uint8) +255
    cv2.circle(canvas, (200,300), 75, (0,0,255), 5)
    cv2.imshow('Basic drawing with CV', canvas)
    #cv2.waitKey()
    
if __name__ == '__main__':
    main()