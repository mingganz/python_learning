# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 21:58:55 2018

@author: tzhou
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['xtick.labelsize'] = 24
mpl.rcParams['ytick.labelsize'] = 24

np.random.seed(42)

x = np.linspace(0, 5, 100)
y = 2 * np.sin(x) + 0.3 * x**2
y_data = y + np.random.normal(scale=0.3, size=100)

data = plt.figure('data')
#data.subplots_adjust(top=10)
ax1 = data.add_subplot(1, 1, 1)
ax1.set_ylabel('Y_data')
ax1.set_title('Original data')
plt.plot(x, y_data, '.')

plt.figure('model')
plt.plot(x, y)

plt.figure('data & model')
plt.plot(x, y, 'k', lw =3)

#plt.scatter(x, y_data)
plt.plot(x, y_data, '.')
plt.savefig('result.png')
plt.show()