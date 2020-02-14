#!/usr/bin/env python
import os
import random
import sys
from collections import defaultdict

import numpy as np
import scipy.sparse as sp

import cnn_train
import data_helper
import tree

# Learning CNN model
# =========================================================
def train_problem(current_depth, upper_depth, class_num, fine_tuning, embedding_weight, input_data, model_type, learning_categories):
    params = {"gpu":0, 
                "out_channels":128,
                "embedding_dimensions":300, 
                "epoch":40, 
                "batchsize":100,
                "unit":1024, 
                "output_dimensions": int(class_num), 
                "fine_tuning":int(fine_tuning), 
                "current_depth": current_depth, 
                "upper_depth": upper_depth, 
                "embedding_weight": embedding_weight,
                "input_data": input_data,
                "model_type": model_type,
                "learning_categories": learning_categories
                }
    if params["model_type"] == "XML-CNN":
        params["unit"] = 512 # compact representation
    if (params["model_type"] == "CNN-fine-tuning") and (current_depth == "1st"):
        params["fine_tuning"] = 0

    if (current_depth == "1st") and ((params["model_type"] == "CNN-fine-tuning") or  (params["model_type"] == "CNN-Hierarchy")):
        network_output = cnn_train.load_top_level_weights(params)
    else:
        network_output = cnn_train.main(params)
    
    return network_output

# Creating dictionary according to each level of a hierarchy
# =========================================================
def make_labels_hie_info_dic(tree_path):
        label_hierarchical_info_dic = {}
        with open(tree_path, "r") as f:
            for line in f:
                line = line[:-1]
                category = line.split("<")[-1]
                level = len(line.split("<"))
                if category not in label_hierarchical_info_dic:
                        label_hierarchical_info_dic[category] = level
        return label_hierarchical_info_dic

# Creating dctionary with each level of a hierarchy
# =========================================================
def make_labels_hie_list_dic(labels, label_hierarchical_info_dic):
        layer_category_list_dic = {}
        for i in range(1,max(label_hierarchical_info_dic.values())+1):
                a_set = set([])
                layer_category_list_dic[i] = a_set
        for label in labels:
            layer_category_list_dic[int(label_hierarchical_info_dic[label])].add(label)

        return layer_category_list_dic

# Create a hierarchy
# =========================================================
def make_tree(tree_file_path):
    Tree = tree.make()
    with open(tree_file_path, mode="r") as f:
        for line in f:
            line = line[:-1]
            line = line.split("\t")[0]
            line = line.split("<")
            tree.add(Tree, line)
    return Tree




# Main processing
# ==================================================================
def main():
    random.seed(0)
    np.random.seed(0)

    # Loading data
    # ==========================================================
    print ("-"*50)
    print ("Loading data...")
    train = sys.argv[1]
    test = sys.argv[2]
    validation = sys.argv[3]
    embedding_weight_path = sys.argv[4]
    model_type = sys.argv[5]
    tree_file_path = sys.argv[6]
    use_words = int(sys.argv[7])

    f_train = open(train, "r")
    train_lines = f_train.readlines()
    f_test = open(test, "r")
    test_lines = f_test.readlines()
    f_valid = open(validation, "r")
    valid_lines = f_valid.readlines()
    f_train.close()
    f_test.close()
    f_valid.close()

    # Building Hierarchical information
    # =========================================================
    category_hie_info_dic = make_labels_hie_info_dic(tree_file_path)
    input_data_dic = data_helper.data_load(train_lines, valid_lines, test_lines, category_hie_info_dic, use_words)
    category_hie_list_dic = make_labels_hie_list_dic(list(input_data_dic["catgy"].keys()), category_hie_info_dic)
    # Loading Word embeddings
    # =========================================================
    print ("-"*50)
    print ("Loading Word embedings...")
    embedding_weight = data_helper.embedding_weights_load(input_data_dic["vocab"], embedding_weight_path)

    # Conditions of each model
    # =========================================================
    fine_tuning = 0
    if model_type == "XML-CNN" or model_type == "CNN-Flat":
        categorization_type="flat"
        fine_tuning = 0
    elif model_type == "CNN-Hierarchy":
        categorization_type="hierarchy"
        fine_tuning = 0
    elif model_type == "CNN-fine-tuning":
        categorization_type="hierarchy"
        fine_tuning = 1
    elif model_type == "Pre-process":
        categorization_type = "pre-process"
        fine_tuning = 0
    else:
        raise TypeError("Unknown model type: %s!" % model_type)

    # Processing in case of pro-processing
    # ========================================================
    if categorization_type == "pre-process":
        print ("-"*50)
        print ("Pre-process for hierarchical categorization...")
        Tree = make_tree(tree_file_path)
        layer = 1
        depth = data_helper.order_n(1)
        upper_depth = None
        learning_categories = sorted(category_hie_list_dic[layer])
        x_trn, y_trn, x_val, y_val, x_tst, y_tst =  data_helper.build_problem(learning_categories=learning_categories,depth=depth, input_data_dic=input_data_dic)
        input_network_data = {"x_trn":x_trn, "y_trn":y_trn, "x_val":x_val, "y_val":y_val, "x_tst":x_tst, "y_tst":y_tst}
        y_pred = train_problem(current_depth=depth, upper_depth=upper_depth, class_num=len(learning_categories), fine_tuning=fine_tuning, embedding_weight=embedding_weight, input_data=input_network_data, model_type=model_type, learning_categories=learning_categories)
        print ("Please change model-type to CNN-Hierarchy of CNN-fine-tuning.")
    
    
    # Processing in case of flat categorization
    # ========================================================
    elif categorization_type == "flat":
        print ("-"*50)
        print ("Processing in case of flat categorization...")
        from itertools import chain
        learning_categories = sorted(input_data_dic["catgy"].keys()) ## this order is network"s output order.
        x_trn, y_trn, x_val, y_val, x_tst, y_tst =  data_helper.build_problem(learning_categories=learning_categories,depth="flat", input_data_dic=input_data_dic)
        input_network_data = {"x_trn":x_trn, "y_trn":y_trn, "x_val":x_val, "y_val":y_val, "x_tst":x_tst, "y_tst":y_tst}
        y_pred = train_problem(current_depth="flat", upper_depth=None, class_num=len(learning_categories), fine_tuning=fine_tuning, embedding_weight=embedding_weight, input_data=input_network_data, model_type=model_type, learning_categories=learning_categories)
        grand_labels, pred_result = data_helper.get_catgy_mapping(learning_categories, y_tst, y_pred, "flat")
        data_helper.write_out_prediction(grand_labels, pred_result, input_data_dic)
        
    # Processing in case of hierarchical categorization
    # ========================================================
    elif categorization_type == "hierarchy":
        if not os.path.exists("./CNN/PARAMS/parameters_for_multi_label_model_1st.npz"):
            raise FileNotFoundError('Please change _tModelType=CNN-Hierarchy" or _tModelType=CNN-fine-tuning" to _tModelType=Pre-process" in example.sh.')
        print ("-"*50)
        print ("Processing in case of hierarchical categorization...")
        upper_depth = None
        y_tst_concat = [[] for i in range(len(input_data_dic["test"]))]
        y_pred_concat = [[] for i in range(len(input_data_dic["test"]))]
        all_categories = []
        Tree = make_tree(tree_file_path)
        layers = list(category_hie_list_dic.keys())
        for layer in layers:
            depth = data_helper.order_n(layer)
            print ("-"*50)
            print ("Learning and categorization processing of " + depth + " layer")
            learning_categories = sorted(category_hie_list_dic[layer])
            x_trn, y_trn, x_val, y_val, x_tst, y_tst =  data_helper.build_problem(learning_categories=learning_categories,depth=depth, input_data_dic=input_data_dic)
            input_network_data = {"x_trn":x_trn, "y_trn":y_trn, "x_val":x_val, "y_val":y_val, "x_tst":x_tst, "y_tst":y_tst}
            y_pred = train_problem(current_depth=depth, upper_depth=upper_depth, class_num=len(learning_categories), fine_tuning=fine_tuning, embedding_weight=embedding_weight, input_data=input_network_data, model_type=model_type, learning_categories=learning_categories)
            grand_labels, pred_result = data_helper.get_catgy_mapping(learning_categories, y_tst, y_pred, depth)
            upper_depth = depth
            for i in range(len(input_data_dic["test"])):
                y_tst_concat[i].extend(grand_labels[i])
            for i in range(len(input_data_dic["test"])):
                for y in pred_result[i]:
                    if (tree.search_parent(Tree, y) in y_pred_concat[i]) or (tree.search_parent(Tree, y) == "root"):
                        y_pred_concat[i].append(y)

            all_categories += learning_categories
        
        print ("-"*50)
        print ("Final Result")
        data_helper.write_out_prediction(y_tst_concat, y_pred_concat, input_data_dic)

if __name__ == "__main__":
    main()
