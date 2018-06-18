# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 16:49:26 2018

@author: tzhou
"""

import cv2

def main():
    img = cv2.imread('BingWallpaper-2018-06-14.jpg')
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Turn the image greener
    turn_green_hsv = img_hsv.copy()
    turn_green_hsv[:, :, 0] = (turn_green_hsv[:, :, 0] + 15) % 180
    turn_green_img = cv2.cvtColor(turn_green_hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite('gree.jpg', turn_green_img)
    
    
    # Decrease saturation
    colorless_hsv = img_hsv.copy()
    colorless_hsv[:, :, 1] = colorless_hsv[:, :, 1] * 0.5
    colorless_img = cv2.cvtColor(colorless_hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite('colorless.jpg', colorless_img)
    
    #Decease value to make it darker
    darker_hsv = img_hsv.copy()
    darker_hsv[:, :, 2] = darker_hsv[:, :, 2] * 0.7
    darker_img = cv2.cvtColor(darker_hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite('darker.jpg', darker_img)
    
if __name__ == '__main__':
    main()