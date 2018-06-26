# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 12:04:18 2018

@author: tzhou
"""

import mxnet as mx

def main():
    a = mx.sym.Variable('a')
    b = mx.sym.Variable('b')
    c = mx.sym.Variable('c')
    
    d = (a + b) * c
    input_args = {
            'a': mx.nd.array([1]),
            'b': mx.nd.array([2]),
            'c': mx.nd.array([3])}
    
    executor = d.bind(ctx=mx.cpu(), args=input_args)
    executor.forward()
    print(executor.outputs[0].asnumpy())
    
    
    grad_a = mx.nd.empty(1)
    executor = d.bind(
            ctx=mx.cpu(),
            args=input_args,
            args_grad={'a': grad_a})
    executor.backward(out_grads=mx.nd.ones(1))
    print(grad_a.asscalar)
    
if __name__ == '__main__':
    main()