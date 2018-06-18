# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 22:12:48 2018

@author: tzhou
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt

def main():
    img = cv2.imread('BingWallpaper-2018-06-14.jpg')
    tf_1 = np.array([
            [1.6, 0, -150],
            [0, 1.6, -240]], dtype=np.float32)
    
    tf_img_1 = cv2.warpAffine(img, tf_1, (img.shape[1], img.shape[0]))
    cv2.imwrite('tf_1.jpg', tf_img_1)
    
    theta = np.tan(15*np.pi/180)
                   
    tf_2 = np.array([
            [1, theta, 0],
            [0, 1, 0]], dtype=np.float32)
    tf_img_2 = cv2.warpAffine(img, tf_2, (img.shape[1], img.shape[0]))
    cv2.imwrite('tf_2.jpg', tf_img_2)
    
    tf_3 = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0]])
    tf_img_3 = cv2.warpAffine(img, tf_3, (img.shape[1], img.shape[0]))
    cv2.imwrite('tf_3.jpg', tf_img_3)
    

    tf_4 = np.array([
            [1, 1.5, 0],
            [0.5, 2, 0]])
    tf_img_4 = cv2.warpAffine(img, tf_4, (img.shape[1], img.shape[0]))
    cv2.imwrite('tf_4.jpg', tf_img_4)
    
    
if __name__ == '__main__':
    main()

