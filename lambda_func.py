# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 20:15:17 2018

@author: tzhou
"""

def get_val_at_pos_1(x):
    return x[1]

def main():
    heros = [
       ('Superman', 99),
       ('Batman', 100),
       ('Joker', 85)
            ]
    
    sorted_pairs0 = sorted(heros, key = get_val_at_pos_1)
    sorted_pairs1 = sorted(heros, key = lambda x: x[1])
    
    print(sorted_pairs0)
    print(sorted_pairs1)

def lambda_fun():
    some_ops = lambda x, y: x + y + x*y + x**y
    print(some_ops(2, 3))

if __name__ == '__main__':
    main()
    lambda_fun()

