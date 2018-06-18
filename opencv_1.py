# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 14:30:25 2018

@author: tzhou
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt

img = np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        [[255, 255, 0], [255, 0, 255], [0, 255, 255]],
        [[255, 255, 255], [128, 128, 128], [0, 0, 0]],
        ], dtype = np.uint8)

plt.imsave('img_pyplot.jpg', img)
cv2.imwrite('img_cv.jpg', img)