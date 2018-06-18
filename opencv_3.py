# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 16:18:19 2018

@author: tzhou
"""

import cv2

def main():
    img = cv2.imread('BingWallpaper-2018-06-14.jpg')

    img_200x200 = cv2.resize(img, (200, 200))
    cv2.imwrite('200x200.jpg', img_200x200)
    
    img_half = cv2.resize(img, (0, 0 ), fx=0.5, fy=0.5, 
                          interpolation=cv2.INTER_NEAREST)
    cv2.imwrite('half.jpg', img_half)
    print(img_half.shape)
    
    img_border = cv2.copyMakeBorder(img_half, 50, 50, 10, 10, 
                                    cv2.BORDER_CONSTANT, value=(255, 255, 128))
    cv2.imwrite('border.jpg', img_border)
    
    patch_img = img[20: 450, -480:-10]
    cv2.imwrite('patch.jpg', patch_img)
    
if __name__ == '__main__':
    main()