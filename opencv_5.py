# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 17:22:40 2018

@author: tzhou
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def gamma_trans(img, gama):
    gamma_table = [np.power(x/255.0, gama) * 255.0 for x in range(256)]
    gamma_table = np.round(np.array(gamma_table).astype(np.uint8))
    return cv2.LUT(img, gamma_table)

def main():
    img = cv2.imread('BingWallpaper-2018-06-14.jpg')

    hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
    hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
    hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
    
    plt.plot(hist_b)
    plt.plot(hist_g)
    plt.plot(hist_r)
    plt.show()
    
    img_corrected = gamma_trans(img, 0.5)
    cv2.imwrite('gamma_corrected.jpg', img_corrected)
    
    
    hist_b_corrected = cv2.calcHist([img_corrected], [0], None, [256], [0, 256])
    hist_g_corrected = cv2.calcHist([img_corrected], [1], None, [256], [0, 256])
    hist_r_corrected = cv2.calcHist([img_corrected], [2], None, [256], [0, 256])
    
    plt.plot(hist_b_corrected)
    plt.plot(hist_g_corrected)
    plt.plot(hist_r_corrected)
    plt.show()

    
    fig = plt.figure()
    pix_hists = [
            [hist_b, hist_g, hist_r],
            [hist_b_corrected, hist_g_corrected, hist_r_corrected]]
    pix_vals = range(256)
    for sub_plt, pix_hist in zip([121, 122], pix_hists):
        ax = fig.add_subplot(sub_plt, projection='3d')
        for c, z, channel_hist in zip(['b', 'g', 'r'], [20, 10, 0], pix_hist):
            cs = [c] * 256
            ax.bar(pix_vals, channel_hist, zs=z, zdir='y', color=cs, alpha=0.618,
                   edgecolor='None')
            ax.set_xlabel('Pixel values')
            ax.set_xlim([0, 256])
            ax.set_ylabel('Counts')
            ax.set_zlabel('Channels')
    plt.show()
    
if __name__ == '__main__':
    main()