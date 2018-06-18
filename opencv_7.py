# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 21:40:55 2018

@author: tzhou
"""

import numpy as np
import cv2 
from matplotlib import pyplot as plt

img = cv2.imread('BingWallpaper-2018-06-14.jpg')
color = ('b', 'g', 'r')
for i, col in enumerate(color):
    histr = cv2.calcHist([img], [i], None, [256], [0, 256])
    plt.plot(histr, color = col)
    plt.xlim([0, 256])
plt.show()