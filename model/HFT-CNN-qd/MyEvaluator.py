import copy
import pdb

import numpy as np
import scipy.sparse as sp
import six
from chainer import configuration, cuda, function
from chainer import functions as F
from chainer import link
from chainer import reporter as reporter_module
from chainer.dataset import convert
from chainer.dataset import iterator as iterator_module
from chainer.training import extension, extensions


# Loss value calculation of validation data
# =========================================================
class MyEvaluator(extensions.Evaluator):

    trigger = 1, 'epoch'
    default_name = 'validation'
    priority = extension.PRIORITY_WRITER

    name = None

    def __init__(self, iterator, target, class_dim, converter=convert.concat_examples,  
                 device=None, eval_hook=None, eval_func=None):
        if isinstance(iterator, iterator_module.Iterator):
            iterator = {'main': iterator}
        self._iterators = iterator

        if isinstance(target, link.Link):
            target = {'main': target}
        self._targets = target

        self.converter = converter
        self.device = device
        self.eval_hook = eval_hook
        self.eval_func = eval_func
        self.class_dim = class_dim

    def evaluate(self):

        iterator = self._iterators['main']
        eval_func = self.eval_func or self._targets['main']

        if self.eval_hook:
            self.eval_hook(self)

        if hasattr(iterator, 'reset'):
            iterator.reset()
            it = iterator
        else:
            it = copy.copy(iterator)

        summary = reporter_module.DictSummary()

        for batch in it:
            observation = {}
            with reporter_module.report_scope(observation):
                row_idx, col_idx, val_idx = [], [], []
                x = cuda.to_gpu(np.array([i[0] for i in batch]))
                labels = [l[1] for l in batch]
                for i in range(len(labels)):
                    l_list = list(set(labels[i]))
                    for y in l_list:
                        row_idx.append(i)
                        col_idx.append(y)
                        val_idx.append(1)
                m = len(labels)
                n = self.class_dim
                t = sp.csr_matrix((val_idx, (row_idx, col_idx)), shape=(m, n), dtype=np.int8).todense()
                t = cuda.to_gpu(t)

                with function.no_backprop_mode():
                    loss = F.sigmoid_cross_entropy(eval_func(x), t)
                    summary.add({MyEvaluator.default_name + '/main/loss':loss})
            summary.add(observation)

        return summary.compute_mean()
