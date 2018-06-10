# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 21:24:53 2018

@author: tzhou
"""

def main():
    a = 'I\'m like a {} chasing {}'
    b = a.format('dog', 'cats')
    print(b)
    
    for i in [1, 19, 256]:
        print('The index is {:0>6d}'.format(i))
        
    for x in ['*', '*****', '*'*9]:
        print('{:-<10}'.format(x))
    
    temple = '{name} is {age} years old'
    c = temple.format(name='Tom', age=10)
    print(c)
    
if __name__ == '__main__':
    main()