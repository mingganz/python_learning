# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 19:53:15 2018

@author: tzhou
"""

def move_up(x):
    x[1] += 1

def move_down(x):
    x[1] -= 1
    
def move_left(x):
    x[0] -= 1
    
def move_right(x):
    x[0] += 1
    
moves = ['up', 'left', 'down', 'right']
actions = {
        'up': move_up,
        'down': move_down,
        'left': move_left,
        'right': move_right
        }


    
def main():
    coord = [0, 0]
    for move in moves:
        print(move)
        actions[move](coord)
        print(coord)
        
if __name__ == '__main__':
    main()