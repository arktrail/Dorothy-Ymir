#!/usr/bin/env python


import os.path
import random
import shutil

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
import xml_cnn_model
from MyEvaluator import MyEvaluator
from MyUpdater import MyUpdater

USE_CUDNN = 'never' ## always, auto, or never

# Extraction of enurons whose threshold values are larger than 0.5 
# =========================================================
def select_function(scores):
    scores = chainer.cuda.to_cpu(scores)
    np_predicts = np.zeros(scores.shape,dtype=np.int8)
    for i in tqdm(range(len(scores)),desc="select labels based on threshold loop"):
        np_predicts[i] = (scores[i] >= 0.3)
    return np_predicts

# The Setting of the seed value for random number generation
# =========================================================
def set_seed_random(seed):
        random.seed(seed)
        np.random.seed(seed)
        if chainer.cuda.available:
            chainer.cuda.cupy.random.seed(seed)

# Main process of CNN learning
# =========================================================
def main(params):
    print("")   
    print('# gpu: {}'.format(params["gpu"]))
    print('# unit: {}'.format(params["unit"]))
    print('# batch-size: {}'.format(params["batchsize"]))
    print('# epoch: {}'.format(params["epoch"]))
    print('# number of category: {}'.format(params["output_dimensions"]))
    print('# embedding dimension: {}'.format(params["embedding_dimensions"]))
    print('# current layer: {}'.format(params["current_depth"]))
    print('# model-type: {}'.format(params["model_type"]))
    print('')


    f = open('./CNN/LOG/configuration_' + params["current_depth"] + '.txt', 'w')
    f.write('# gpu: {}'.format(params["gpu"])+"\n")
    f.write('# unit: {}'.format(params["unit"])+"\n")
    f.write('# batch-size: {}'.format(params["batchsize"])+"\n")
    f.write('# epoch: {}'.format(params["epoch"])+"\n")
    f.write('# number of category: {}'.format(params["output_dimensions"])+"\n")
    f.write('# embedding dimension: {}'.format(params["embedding_dimensions"])+"\n")
    f.write('# current layer: {}'.format(params["current_depth"])+"\n")
    f.write('# model-type: {}'.format(params["model_type"])+"\n")
    f.write("\n")
    f.close()

    embedding_weight = params["embedding_weight"]
    embedding_dimensions = params["embedding_dimensions"]
    input_data = params["input_data"]
    x_train = input_data['x_trn']
    x_val = input_data['x_val']
    y_train = input_data['y_trn']
    y_val = input_data['y_val']

    cnn_params = {"cudnn":USE_CUDNN, 
                "out_channels":params["out_channels"],
                "row_dim":embedding_dimensions, 
                "batch_size":params["batchsize"],
                "hidden_dim":params["unit"],
                "n_classes":params["output_dimensions"],
                "embedding_weight":embedding_weight,
                }
    if params["fine_tuning"] == 0:
        cnn_params['mode'] = 'scratch'
    elif params["fine_tuning"] == 1:
        cnn_params['mode'] = 'fine-tuning'
        cnn_params['load_param_node_name'] = params['upper_depth']
        
    if params["model_type"] == "XML-CNN":
        model = xml_cnn_model.CNN(**cnn_params)
    else:
        model = cnn_model.CNN(**cnn_params)

    if params["gpu"] >= 0:
        chainer.cuda.get_device_from_id(params["gpu"]).use()
        model.to_gpu()
    
    # Learning CNN by training and validation data
    # =========================================================

    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)

    train = tuple_dataset.TupleDataset(x_train, y_train)
    val = tuple_dataset.TupleDataset(x_val, y_val)
    
    train_iter = chainer.iterators.SerialIterator(train, params["batchsize"], repeat=True, shuffle=False)
    val_iter = chainer.iterators.SerialIterator(val, params["batchsize"], repeat = False, shuffle=False)
    

    # The setting of Early stopping validation refers to a loss value (validation/main/loss) obtained by validation data
    # =========================================================
    stop_trigger = training.triggers.EarlyStoppingTrigger(
    monitor='validation/main/loss',
    max_trigger=(params["epoch"], 'epoch'))


    
    updater = MyUpdater(train_iter, optimizer, params["output_dimensions"], device=params["gpu"])
    trainer = training.Trainer(updater, stop_trigger, out='./CNN/')


    trainer.extend(MyEvaluator(val_iter, model, class_dim=params["output_dimensions"], device=params["gpu"]))
    trainer.extend(extensions.dump_graph('main/loss'))

    trainer.extend(extensions.snapshot_object(model, 'parameters_for_multi_label_model_' + params["current_depth"] + '.npz'),trigger=training.triggers.MinValueTrigger('validation/main/loss',trigger=(1,'epoch')))

    trainer.extend(extensions.LogReport(log_name='LOG/log_' + params["current_depth"] + ".txt", trigger=(1, 'epoch')))

    trainer.extend(extensions.PrintReport(
        ['epoch', 'main/loss', 'validation/main/loss',
         'elapsed_time']))    
    trainer.extend(extensions.ProgressBar())

    trainer.extend(
    extensions.PlotReport(['main/loss', 'validation/main/loss'],
                          'epoch', file_name='LOG/loss_' + params["current_depth"] + '.png'))
    
    trainer.run()


    filename = 'parameters_for_multi_label_model_' + params["current_depth"] + '.npz'
    src = './CNN/'
    dst = './CNN/PARAMS'
    shutil.move(os.path.join(src, filename), os.path.join(dst, filename))


    # Prediction process for test data.
    # =========================================================
    print ("-"*50)
    print ("Testing...")
    
    x_tst = input_data['x_tst']
    y_tst = input_data['y_tst']
    n_eval = len(x_tst)

    cnn_params['mode'] = 'test-predict'
    cnn_params['load_param_node_name'] = params["current_depth"]
    
    if params["model_type"] == "XML-CNN":
        model = xml_cnn_model.CNN(**cnn_params)
    else:
        model = cnn_model.CNN(**cnn_params)

    model.to_gpu()
    output = np.zeros([n_eval,params["output_dimensions"]],dtype=np.int8)
    output_probability_file_name = "CNN/RESULT/probability_" + params["current_depth"] + ".csv"
    with open(output_probability_file_name, 'w') as f:
        f.write(','.join(params["learning_categories"])+"\n")
 
    test_batch_size = params["batchsize"]
    with chainer.using_config('train', False), chainer.no_backprop_mode():
        for i in tqdm(six.moves.range(0, n_eval, test_batch_size),desc="Predict Test loop"):
            x = chainer.Variable(chainer.cuda.to_gpu(x_tst[i:i + test_batch_size]))
            t = y_tst[i:i + test_batch_size]
            net_output = F.sigmoid(model(x))
            output[i: i + test_batch_size] = select_function(net_output.data)
            with open(output_probability_file_name , 'a') as f:
                tmp = chainer.cuda.to_cpu(net_output.data)
                low_values_flags = tmp < 0.001
                tmp[low_values_flags] = 0
                np.savetxt(f,tmp,fmt='%.4g',delimiter=",")
    return output

# Categorization of the top level of a hierarchy by using WoFt and HFT models
# =========================================================
def  load_top_level_weights(params):
    print ("-"*50)
    print ("Testing...")

    embedding_weight = params["embedding_weight"]
    embedding_dimensions = params["embedding_dimensions"]
    input_data = params["input_data"]

    cnn_params = {"cudnn":USE_CUDNN, 
                "out_channels":params["out_channels"],
                "row_dim":embedding_dimensions, 
                "batch_size":params["batchsize"],
                "hidden_dim":params["unit"],
                "n_classes":params["output_dimensions"],
                "embedding_weight":embedding_weight,
                }

    x_tst = input_data['x_tst']
    y_tst = input_data['y_tst']
    n_eval = len(x_tst)

    cnn_params['mode'] = 'test-predict'
    cnn_params['load_param_node_name'] = params["current_depth"]
    if params["model_type"] == "XML-CNN":
        model = xml_cnn_model.CNN(**cnn_params)
    else:
        model = cnn_model.CNN(**cnn_params)

    model.to_gpu()
    output = np.zeros([n_eval,params["output_dimensions"]],dtype=np.int8)
    output_probability_file_name = "CNN/RESULT/probability_" + params["current_depth"] + ".csv"
    with open(output_probability_file_name, 'w') as f:
        f.write(','.join(params["learning_categories"])+"\n")
        
    test_batch_size = params["batchsize"]
    with chainer.using_config('train', False), chainer.no_backprop_mode():
        for i in tqdm(six.moves.range(0, n_eval, test_batch_size),desc="Predict Test loop"):
            x = chainer.Variable(chainer.cuda.to_gpu(x_tst[i:i + params["batchsize"]]))
            t = y_tst[i:i + test_batch_size]
            net_output = F.sigmoid(model(x))
            output[i: i + test_batch_size] = select_function(net_output.data)
            with open(output_probability_file_name , 'a') as f:
                tmp = chainer.cuda.to_cpu(net_output.data)
                low_values_flags = tmp < 0.001
                tmp[low_values_flags] = 0
                np.savetxt(f,tmp,fmt='%.4g',delimiter=",")
    return output
