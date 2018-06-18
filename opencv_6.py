# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 18:14:03 2018

@author: tzhou
"""

import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

def main():
    img = cv.imread('BingWallpaper-2018-06-14.jpg', 0)
    plt.hist(img.ravel(), 256, [0,256])
    plt.show()
    
if __name__ == '__main__':
    main()
