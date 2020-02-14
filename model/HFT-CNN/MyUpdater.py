import pdb

import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np
import scipy.sparse as sp
import six
from chainer import cuda
from chainer import optimizer as optimizer_module
from chainer import reporter, training
from chainer.dataset import convert
from chainer.dataset import iterator as iterator_module
from chainer.datasets import get_mnist
from chainer.training import extensions, trainer

# CNN iteration procedure
# =========================================================
class MyUpdater(training.StandardUpdater):
    def __init__(self, iterator, optimizer, class_dim, converter=convert.concat_examples,
                device=None, loss_func=None):
        if isinstance(iterator, iterator_module.Iterator):
            iterator = {'main': iterator}
        self._iterators = iterator

        if not isinstance(optimizer, dict):
            optimizer = {'main': optimizer}
        self._optimizers = optimizer

        if device is not None and device >= 0:
            for optimizer in six.itervalues(self._optimizers):
                optimizer.target.to_gpu(device)
        #print(device)
        self.converter = converter
        self.loss_func = loss_func
        #self.device = device
        self.iteration = 0
        self.class_dim = class_dim
        
    def update_core(self):
        batch = self._iterators['main'].next()

        x = chainer.cuda.to_gpu(np.array([i[0] for i in batch]))
        labels = [l[1] for l in batch] 
        row_idx, col_idx, val_idx = [], [], []
        for i in range(len(labels)):
            l_list = list(set(labels[i]))
            for y in l_list:
                row_idx.append(i)
                col_idx.append(y)
                val_idx.append(1)
        m = len(labels)
        n = self.class_dim
        t = sp.csr_matrix((val_idx, (row_idx, col_idx)), shape=(m, n), dtype=np.int8).todense()
        

        t = chainer.cuda.to_gpu(t)

        optimizer = self._optimizers['main']
        optimizer.target.cleargrads()
        loss = F.sigmoid_cross_entropy(optimizer.target(x), t)
        chainer.reporter.report({'main/loss':loss})
        loss.backward()
        optimizer.update()
