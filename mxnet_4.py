# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 17:48:55 2018

@author: tzhou
"""

import numpy as np
import mxnet as mx

def main():
    data = mx.sym.Variable('data')
    fc1 = mx.sym.FullyConnected(data=data, name='fc1', num_hidden=2)
    sigmoid1 = mx.sym.Activation(data=fc1, name='sigmoid1', act_type='sigmoid')
    fc2 = mx.sym.FullyConnected(data=sigmoid1, name='fc2', num_hidden=2)
    mlp = mx.sym.SoftmaxOutput(data=fc2, name='softmax')
    shape = {'data': (2,)}
    mlp_dot = mx.viz.plot_network(symbol=mlp, shape=shape)
    mlp_dot.render('simple_mlp.gv', view=True)
    
    
    import pickle
    import logging
    with open('data.pkl', 'rb') as f:
        samples, labels = pickle.load(f)
        
    logging.getLogger().setLevel(logging.DEBUG)
    
    batch_size = len(labels)
    samples = np.array(samples)
    labels = np.array(labels)
    
    train_iter = mx.io.NDArrayIter(samples, labels, batch_size)
    model = mx.model.FeedForward.create(
            symbol=mlp,
            X=train_iter,
            num_epoch=1000,
            learning_rate=0.1,
            momentum=0.99)
    print(model.predict(mx.nd.array([[0.5, 0.5]])))
    
if __name__ == '__main__':
    main()