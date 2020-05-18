#! /usr/bin/env python

import random

import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np


# CNN Network(Fla, WoFt, HFT)
# =========================================================
class CNN(chainer.Chain):

    def __init__(self, **params):
        self.in_channels = 1
        self.out_channels = params["out_channels"]
        self.row_dim = params["row_dim"]
        self.batch_size = params["batch_size"] if "batch_size" in params else 100
        self.hidden_dim = params["hidden_dim"]
        self.n_classes = params["n_classes"]
        self.mode = params["mode"] if "mode" in params else None
        self.load_param_node_name = params["load_param_node_name"] if "load_param_node_name" in params else None
        self.cudnn = params["cudnn"] if "cudnn" in params else 'never'
        self.embedding_weight = params["embedding_weight"]
        self.initializer = chainer.initializers.HeNormal()

        # Network definition for HFT model
        # =========================================================
        if self.mode == "fine-tuning":
            parameters = np.load(
                './CNN/PARAMS/parameters_for_multi_label_model_' + self.load_param_node_name + '.npz')
            super(CNN, self).__init__()
            set_seed_random(0)
            with self.init_scope():
                self.lookup_gpu0 = L.EmbedID(
                    in_size=parameters['lookup_gpu0/W'].shape[0], out_size=parameters['lookup_gpu0/W'].shape[1], initialW=parameters['lookup_gpu0/W'], ignore_label=-1).to_gpu(0)
                self.lookup_gpu1 = L.EmbedID(
                    in_size=parameters['lookup_gpu1/W'].shape[0], out_size=parameters['lookup_gpu1/W'].shape[1], initialW=parameters['lookup_gpu1/W'], ignore_label=-1).to_gpu(1)
                self.conv1_gpu0 = L.Convolution2D(self.in_channels, self.out_channels, (
                    2, self.row_dim), stride=1, initialW=parameters['conv1_gpu0/W'], initial_bias=parameters['conv1_gpu0/b']).to_gpu(0)
                self.conv1_gpu1 = L.Convolution2D(self.in_channels, self.out_channels, (
                    2, self.row_dim), stride=1, initialW=parameters['conv1_gpu1/W'], initial_bias=parameters['conv1_gpu1/b']).to_gpu(1)
                self.conv2_gpu0 = L.Convolution2D(self.in_channels, self.out_channels, (
                    3, self.row_dim), stride=1, initialW=parameters['conv2_gpu0/W'], initial_bias=parameters['conv2_gpu0/b']).to_gpu(0)
                self.conv2_gpu1 = L.Convolution2D(self.in_channels, self.out_channels, (
                    3, self.row_dim), stride=1, initialW=parameters['conv2_gpu1/W'], initial_bias=parameters['conv2_gpu1/b']).to_gpu(1)
                self.conv3_gpu0 = L.Convolution2D(self.in_channels, self.out_channels, (
                    4, self.row_dim), stride=1, initialW=parameters['conv3_gpu0/W'], initial_bias=parameters['conv3_gpu0/b']).to_gpu(0)
                self.conv3_gpu1 = L.Convolution2D(self.in_channels, self.out_channels, (
                    4, self.row_dim), stride=1, initialW=parameters['conv3_gpu1/W'], initial_bias=parameters['conv3_gpu1/b']).to_gpu(1)
                self.l1_gpu0 = L.Linear(
                    in_size=None, out_size=self.hidden_dim, initialW=self.initializer).to_gpu(0)
                self.l1_gpu1 = L.Linear(
                    in_size=None, out_size=self.hidden_dim, initialW=self.initializer).to_gpu(1)
                self.l2_gpu0 = L.Linear(
                    in_size=self.hidden_dim, out_size=self.n_classes, initialW=self.initializer).to_gpu(0)
                self.l2_gpu1 = L.Linear(
                    in_size=self.hidden_dim, out_size=self.n_classes, initialW=self.initializer).to_gpu(1)

        # Network definition for Flat and WoFt models
        # =========================================================
        elif self.mode == "scratch":
            print("I guess again, the model type for Pre-process is this")
            # change to mul gpu
            super(CNN, self).__init__()
            set_seed_random(0)
            with self.init_scope():
                self.lookup_gpu0 = L.EmbedID(
                    in_size=self.embedding_weight.shape[0], out_size=self.embedding_weight.shape[1], initialW=self.embedding_weight, ignore_label=-1).to_gpu(0)
                self.lookup_gpu1 = L.EmbedID(
                    in_size=self.embedding_weight.shape[0], out_size=self.embedding_weight.shape[1], initialW=self.embedding_weight, ignore_label=-1).to_gpu(1)
                self.conv1_gpu0 = L.Convolution2D(
                    self.in_channels, self.out_channels, (2, self.row_dim), stride=1, initialW=self.initializer).to_gpu(0)
                self.conv1_gpu1 = L.Convolution2D(
                    self.in_channels, self.out_channels, (2, self.row_dim), stride=1, initialW=self.initializer).to_gpu(1)
                self.conv2_gpu0 = L.Convolution2D(
                    self.in_channels, self.out_channels, (3, self.row_dim), stride=1, initialW=self.initializer).to_gpu(0)
                self.conv2_gpu1 = L.Convolution2D(
                    self.in_channels, self.out_channels, (3, self.row_dim), stride=1, initialW=self.initializer).to_gpu(1)
                self.conv3_gpu0 = L.Convolution2D(
                    self.in_channels, self.out_channels, (4, self.row_dim), stride=1, initialW=self.initializer).to_gpu(0)
                self.conv3_gpu1 = L.Convolution2D(
                    self.in_channels, self.out_channels, (4, self.row_dim), stride=1, initialW=self.initializer).to_gpu(1)
                self.l1_gpu0 = L.Linear(
                    in_size=None, out_size=self.hidden_dim, initialW=self.initializer).to_gpu(0)
                self.l1_gpu1 = L.Linear(
                    in_size=None, out_size=self.hidden_dim, initialW=self.initializer).to_gpu(1)
                self.l2_gpu0 = L.Linear(
                    in_size=self.hidden_dim, out_size=self.n_classes, initialW=self.initializer).to_gpu(0)
                self.l2_gpu1 = L.Linear(
                    in_size=self.hidden_dim, out_size=self.n_classes, initialW=self.initializer).to_gpu(1)

        # Network definition on test
        # =========================================================
        elif self.mode == "test-predict":
            parameters = np.load(
                './CNN/PARAMS/parameters_for_multi_label_model_' + self.load_param_node_name + '.npz')
            print("parameters keys")
            print(list(parameters.keys()))
            super(CNN, self).__init__()
            set_seed_random(0)
            with self.init_scope():
                self.lookup_gpu0 = L.EmbedID(
                    in_size=self.embedding_weight.shape[0], out_size=self.embedding_weight.shape[1], initialW=parameters['lookup_gpu0/W'], ignore_label=-1).to_gpu(0)
                self.lookup_gpu1 = L.EmbedID(
                    in_size=self.embedding_weight.shape[0], out_size=self.embedding_weight.shape[1], initialW=parameters['lookup_gpu1/W'], ignore_label=-1).to_gpu(1)
                self.conv1_gpu0 = L.Convolution2D(self.in_channels, self.out_channels, (
                    2, self.row_dim), stride=1, initialW=parameters['conv1_gpu0/W'], initial_bias=parameters['conv1_gpu0/b']).to_gpu(0)
                self.conv1_gpu1 = L.Convolution2D(self.in_channels, self.out_channels, (
                    2, self.row_dim), stride=1, initialW=parameters['conv1_gpu1/W'], initial_bias=parameters['conv1_gpu1/b']).to_gpu(1)
                self.conv2_gpu0 = L.Convolution2D(self.in_channels, self.out_channels, (
                    3, self.row_dim), stride=1, initialW=parameters['conv2_gpu0/W'], initial_bias=parameters['conv2_gpu0/b']).to_gpu(0)
                self.conv2_gpu1 = L.Convolution2D(self.in_channels, self.out_channels, (
                    3, self.row_dim), stride=1, initialW=parameters['conv2_gpu1/W'], initial_bias=parameters['conv2_gpu1/b']).to_gpu(1)
                self.conv3_gpu0 = L.Convolution2D(self.in_channels, self.out_channels, (
                    4, self.row_dim), stride=1, initialW=parameters['conv3_gpu0/W'], initial_bias=parameters['conv3_gpu0/b']).to_gpu(0)
                self.conv3_gpu1 = L.Convolution2D(self.in_channels, self.out_channels, (
                    4, self.row_dim), stride=1, initialW=parameters['conv3_gpu1/W'], initial_bias=parameters['conv3_gpu1/b']).to_gpu(1)
                self.l1_gpu0 = L.Linear(in_size=None, out_size=self.hidden_dim,
                                        initialW=parameters['l1_gpu0/W'], initial_bias=parameters['l1_gpu0/b']).to_gpu(0)
                self.l1_gpu1 = L.Linear(in_size=None, out_size=self.hidden_dim,
                                        initialW=parameters['l1_gpu1/W'], initial_bias=parameters['l1_gpu1/b']).to_gpu(1)
                self.l2_gpu0 = L.Linear(self.hidden_dim, self.n_classes,
                                        initialW=parameters['l2_gpu0/W'], initial_bias=parameters['l2_gpu0/b']).to_gpu(0)
                self.l2_gpu1 = L.Linear(self.hidden_dim, self.n_classes,
                                        initialW=parameters['l2_gpu1/W'], initial_bias=parameters['l2_gpu0/b']).to_gpu(1)

    # Forward propagation in CNN, execute from MyUpdater and MyEvaluator
    # =========================================================

    def __call__(self, x):
        with chainer.using_config('use_cudnn', self.cudnn):
            with chainer.using_config('cudnn_deterministic', True):
                h_non_static0 = F.dropout(self.lookup_gpu0(x), 0.25)
                h_non_static1 = F.dropout(self.lookup_gpu1(F.copy(x, 1)), 0.25)
                h_non_static0 = F.reshape(
                    h_non_static0, (h_non_static0.shape[0], 1, h_non_static0.shape[1], h_non_static0.shape[2]))
                h_non_static1 = F.reshape(
                    h_non_static1, (h_non_static1.shape[0], 1, h_non_static1.shape[1], h_non_static1.shape[2]))

                h10 = self.conv1_gpu0(h_non_static0)
                h11 = self.conv1_gpu1(h_non_static1)
                h20 = self.conv2_gpu0(h_non_static0)
                h21 = self.conv2_gpu1(h_non_static1)
                h30 = self.conv3_gpu0(h_non_static0)
                h31 = self.conv3_gpu1(h_non_static1)

                h10 = F.max_pooling_2d(
                    F.relu(h10), (h10.shape[2], h10.shape[3]))
                h11 = F.max_pooling_2d(
                    F.relu(h11), (h11.shape[2], h11.shape[3]))
                h20 = F.max_pooling_2d(
                    F.relu(h20), (h20.shape[2], h20.shape[3]))
                h21 = F.max_pooling_2d(
                    F.relu(h21), (h21.shape[2], h21.shape[3]))
                h30 = F.max_pooling_2d(
                    F.relu(h30), (h30.shape[2], h30.shape[3]))
                h31 = F.max_pooling_2d(
                    F.relu(h31), (h31.shape[2], h31.shape[3]))

                h0 = F.concat((h10, h20, h30), axis=2)
                h1 = F.concat((h11, h21, h31), axis=2)
                h0 = F.dropout(F.relu(self.l1_gpu0(h0)), ratio=0.5)
                h1 = F.dropout(F.relu(self.l1_gpu1(h1)), ratio=0.5)

                y0 = self.l2_gpu0(h0)
                y1 = self.l2_gpu1(h1)

                # sync
                y = y0 + F.copy(y1, 0)

                ##############################
                # original forward call
                # h_non_static = F.dropout(self.lookup(x), 0.25)
                # h_non_static = F.reshape(
                #     h_non_static, (h_non_static.shape[0], 1, h_non_static.shape[1], h_non_static.shape[2]))

                # h1 = self.conv1(h_non_static)
                # h2 = self.conv2(h_non_static)
                # h3 = self.conv3(h_non_static)

                # h1 = F.max_pooling_2d(F.relu(h1), (h1.shape[2], h1.shape[3]))
                # h2 = F.max_pooling_2d(F.relu(h2), (h2.shape[2], h2.shape[3]))
                # h3 = F.max_pooling_2d(F.relu(h3), (h3.shape[2], h3.shape[3]))

                # h = F.concat((h1, h2, h3), axis=2)
                # h = F.dropout(F.relu(self.l1(h)), ratio=0.5)

                # y = self.l2(h)

        return y

# The Setting of the seed value for random number generation
# =========================================================


def set_seed_random(seed):
    random.seed(seed)
    np.random.seed(seed)
    if chainer.cuda.available:
        chainer.cuda.cupy.random.seed(seed)
