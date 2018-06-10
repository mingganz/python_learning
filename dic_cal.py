# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 20:16:22 2018

@author: tzhou
"""

prices ={
        'ACME': 45.23,
        'AAPL': 612.78,
        'IBM': 205.55,
        'FB': 10.75
        }

min_price = min(zip(prices.values(), prices.keys()))
print(min_price)

max_price = max(zip(prices.keys(), prices.values()))
print(max_price)
