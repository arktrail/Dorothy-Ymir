#!/usr/bin/env python
import os
import random
import sys
from collections import defaultdict
import numpy as np
import scipy.sparse as sp

import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np
import six
from chainer import training
from chainer.datasets import tuple_dataset
from chainer.training import extensions
from tqdm import tqdm

import cnn_model
from data_helper import *
import tree
import json 
import pickle

TEST_LAYER = 3

def load_my_test_json(test, vocab_dic, use_words, input_text_name):
    data_list = []
    for line in tqdm(test, desc="Loading " + "my_test" + " data"):
        line_data = json.loads(line)
        text_list = line_data[input_text_name][:use_words]
        tmp_text_list = []
        for word in text_list:
            if word in vocab_dic:
                tmp_text_list.append(vocab_dic[word])
            else:
                tmp_text_list.append(vocab_dic["UNK"])
        data_list.append(tmp_text_list)
        del tmp_text_list
    return data_list


def main():
    my_test = sys.argv[1]
    embedding_weight_path = sys.argv[2]
    tree_file_path = sys.argv[3]
    use_words = int(sys.argv[4])
    label_name = sys.argv[5]
    input_text_name = sys.argv[6]
    vocab_path = sys.argv[7]
    catgy_path = sys.argv[8]
    output_prob_path = sys.argv[9]

    # Read vocab
    vocab_file = open(vocab_path, "r")
    vocab_dic = json.load(vocab_file)
    vocab_file.close()
    # Read layer to leaning categories 
    catgy_file = open(catgy_path, "rb")
    category_hie_list_dic = pickle.load(catgy_file)
    catgy_file.close()

    my_test_lines = open(my_test, "r")
    test_text = load_my_test_json(my_test_lines, vocab_dic, use_words, input_text_name)
    my_test_lines.close()


    # Loading Word embeddings
    # =========================================================
    print("-"*50)
    print("Loading Word embedings...")
    embedding_weight = embedding_weights_load(
        vocab_dic, embedding_weight_path)


    depth = order_n(TEST_LAYER)
    print("-"*50)
    print("Testing of " + depth + " layer")
    learning_categories = sorted(category_hie_list_dic[layer])

    # constrace test data
    tst_padded = pad_sentences(test_text, max_length=use_words)
    x_tst = build_input_sentence_data(tst_padded)


    cnn_params = {"cudnn": 'never',
                  "out_channels": 128,
                  "row_dim": 300,
                  "batch_size": 64,
                  "hidden_dim": 1024,
                  "n_classes": len(learning_categories),
                  "embedding_weight": embedding_weight,
                  'mode': 'test-predict',
                  'load_param_node_name': depth
                  }
    model = cnn_model.CNN(**cnn_params)
    model.to_gpu()

    n_eval = len(x_tst)
    output = np.zeros([n_eval, len(learning_categories)], dtype=np.int8)

    with open(output_prob_path, 'w') as f:
            f.write(','.join(learning_categories)+"\n")

    test_batch_size = cnn_params["batch_size"]
    with chainer.using_config('train', False), chainer.no_backprop_mode():
            for i in tqdm(six.moves.range(0, n_eval, test_batch_size), desc="Predict Test loop"):
                x = chainer.Variable(chainer.cuda.to_gpu(
                    x_tst[i:i + test_batch_size]))
                net_output = F.sigmoid(model(x))

                with open(output_prob_path, 'a') as f:
                    tmp = chainer.cuda.to_cpu(net_output.data)
                    low_values_flags = tmp < 0.001
                    tmp[low_values_flags] = 0
                    np.savetxt(f, tmp, fmt='%.4g', delimiter=",")

if __name__ == '__main__':
    main()


