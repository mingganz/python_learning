# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 15:03:19 2018

@author: tzhou
"""

import os
import pickle, gzip
from matplotlib import pyplot as plt

def main():
    # Read out MNIST data from original .gz file
    print('Loading data from mnist.pkl.gz ...')
    with gzip.open('mnist.pkl.gz', 'rb') as f:
        train_set, valid_set, test_set = pickle.load(f, encoding='iso-8859-1')
        
    #Create mnist file folder
    imgs_dir = 'mnist'
    os.system('mkdir -p {}'.format(imgs_dir))
    datasets = {'train': train_set, 'val': valid_set, 'test': test_set}
    
    #Convert train, val and test dataset
    for dataname, dataset in datasets.items():
        print('Converting {} dataset ...'.format(dataname))
        data_dir = os.sep.join([imgs_dir, dataname])
        
        # Create sub folder in mnist folder
        os.system('mkdir -p {}'.format(data_dir))
        
        #i stands for the index of data, use zip() function to read picture and label at index
        for i, (img, label) in enumerate(zip(*dataset)):
            filename = '{:0>6d}_{}.jpg'.format(i, label)
            filepath = os.sep.join([data_dir, filename])
            
            #Restore the one dimensional array to two dimensional array
            img = img.reshape(28, 28)
            plt.imsave(filepath, img, cmap='gray')
            if (i+1) % 10000 == 0:
                print('{} images converted!'.format(i+1))
                
if __name__ == '__main__':
    main()