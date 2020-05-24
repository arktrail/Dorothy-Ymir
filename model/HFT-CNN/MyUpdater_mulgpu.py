import pdb
import copy
import cupy

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


class MyUpdater_mulgpu(training.updaters.ParallelUpdater):
    def __init__(self, iterator, optimizer, class_dim, converter=convert.concat_examples, devices=None, loss_func=None):
        if isinstance(iterator, iterator_module.Iterator):
            iterator = {'main': iterator}
        self._iterators = iterator

        if not isinstance(optimizer, dict):
            optimizer = {'main': optimizer}
        self._optimizers = optimizer

        #  if devices is not None and (isinstance(devices, dict) or devices >= 0):
        #  for optimizer in six.itervalues(self._optimizers):
        #  optimizer.target.to_gpu(devices['main'])
        #  self._models = {'main': optimizer.target}

        # copy models to other devices
        names = list(six.iterkeys(devices))
        try:
            names.remove('main')
        except ValueError:
            raise KeyError("'devices' must contain a 'main' key.")

        print(self._optimizers)
        models = {'main': self._optimizers['main'].target}

        for name in names:
            model = copy.deepcopy(self._optimizers['main'].target)
            if devices[name] >= 0:
                model.to_gpu(devices[name])
            models[name] = model
        if devices['main'] >= 0:
            self._optimizers['main'].target.to_gpu(devices['main'])

        self.converter = converter
        self.loss_func = loss_func
        self.iteration = 0
        self.class_dim = class_dim
        self._devices = devices
        self._models = models

        # used for logging
        self.device0 = cupy.cuda.Device(0)
        self.device1 = cupy.cuda.Device(1)

        # from the code below, I think the loss func is
        # loss = F.sigmoid_cross_entropy(optimizer.target(x), t)

    # need to support multi GPU here
    # https://docs.chainer.org/en/v1.24.0/_modules/chainer/training/updater.html
    def update_core(self):
        batch = self._iterators['main'].next()
        optimizer = self._optimizers['main']
        model_main = optimizer.target
        models_others = {k: v for k, v in self._models.items()
                         if v is not model_main}

        #
        # split the batch into sub-batches
        #
        batch_n = len(self._models)
        gpu_x = {}
        gpu_t = {}

        self._logging("before looping")
        for batch_i, batch_key in enumerate(six.iterkeys(self._models)):
            # self._logging("before moving gpu_x ")
            gpu_x[batch_key] = chainer.cuda.to_gpu(np.array(
                [i[0] for i in batch[batch_i::batch_n]]), device=self._devices[batch_key])
            # self._logging("after moving gpu_x ")
            labels = [l[1] for l in batch[batch_i::batch_n]]
            row_idx, col_idx, val_idx = [], [], []
            for i in range(len(labels)):
                l_list = list(set(labels[i]))
                for y in l_list:
                    row_idx.append(i)
                    col_idx.append(y)
                    val_idx.append(1)
            m = len(labels)
            n = self.class_dim
            t = sp.csr_matrix((val_idx, (row_idx, col_idx)),
                              shape=(m, n), dtype=np.int8).todense()

            # self._logging("before moving gpu_t ")
            gpu_t[batch_key] = chainer.cuda.to_gpu(
                t, device=self._devices[batch_key])
            # self._logging("after moving gpu_t ")

        # for reducing memory
        for model in six.itervalues(self._models):
            # self._logging("before clearing grads ")
            model.cleargrads()
            # self._logging("after clearing grads ")

        losses = []
        for model_key, model in six.iteritems(self._models):
            losses.append(F.sigmoid_cross_entropy(
                model(gpu_x[model_key]), gpu_t[model_key]))

        # for __ininitialized_params
        for model in six.itervalues(self._models):
            model.cleargrads()

        for loss in losses:
            chainer.reporter.report({'main/loss': loss})

        for loss in losses:
            loss.backward()

        for model in six.itervalues(models_others):
            # self._logging("before adding grads")
            model_main.addgrads(model)
            # self._logging("after adding grads")

        optimizer.update()
        for model in six.itervalues(models_others):
            # self._logging("before copying params")
            model.copyparams(model_main)
            # self._logging("after copying params")

        ##################################################
        # original impl
        # batch = self._iterators['main'].next()

        # x = chainer.cuda.to_gpu(np.array([i[0] for i in batch]))
        # labels = [l[1] for l in batch]
        # row_idx, col_idx, val_idx = [], [], []
        # for i in range(len(labels)):
        #     l_list = list(set(labels[i]))
        #     for y in l_list:
        #         row_idx.append(i)
        #         col_idx.append(y)
        #         val_idx.append(1)
        # m = len(labels)
        # n = self.class_dim
        # t = sp.csr_matrix((val_idx, (row_idx, col_idx)),
        #                   shape=(m, n), dtype=np.int8).todense()

        # t = chainer.cuda.to_gpu(t)

        # optimizer = self._optimizers['main']
        # optimizer.target.cleargrads()
        # loss = F.sigmoid_cross_entropy(optimizer.target(x), t)
        # chainer.reporter.report({'main/loss': loss})
        # loss.backward()
        # optimizer.update()
        ##################################################

    def _logging(self, log):
        print("{}: cupy: device0 cuda free mem: {} (GB), total mem: {} (GB)".format(log,
                                                                                    self.device0.mem_info[0] / (1024 ** 2), self.device0.mem_info[1] / (1024 ** 2)))
        print("{}: cupy: device1 cuda free mem: {} (GB), total mem: {} (GB)".format(log,
                                                                                    self.device1.mem_info[0] / (1024 ** 2), self.device1.mem_info[1] / (1024 ** 2)))

