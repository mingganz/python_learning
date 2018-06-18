# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 16:11:57 2018

@author: tzhou
"""

import cv2

def main():
    color_img = cv2.imread('BingWallpaper-2018-06-14.jpg')
    print(color_img.shape)
    
    # Read single channel
    gray_img = cv2.imread('BingWallpaper-2018-06-14.jpg', cv2.IMREAD_GRAYSCALE)
    print(gray_img.shape)
    
    cv2.imwrite('test_grayscale.jpg', gray_img)
    reload_grayscale = cv2.imread('test_grayscale.jpg')
    print(reload_grayscale.shape)
    
    cv2.imwrite('test_imwrite.jpg', color_img, (cv2.IMWRITE_JPEG_QUALITY, 10))
    
    cv2.imwrite('test_imwrite.png', color_img, (cv2.IMWRITE_PNG_COMPRESSION, 1))
    
if __name__ == '__main__':
    main()