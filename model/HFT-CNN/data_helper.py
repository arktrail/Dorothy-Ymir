import os
import pdb
import pickle
import re
from collections import defaultdict
from itertools import chain

import chakin
import numpy as np
import scipy.sparse as sp
from gensim.models import KeyedVectors
from gensim.models.wrappers.fasttext import FastText
from sklearn.metrics import classification_report, f1_score
from sklearn.preprocessing import MultiLabelBinarizer
from tqdm import tqdm


# sequence operation
# =========================================================
def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


# read data from text file
# =========================================================
def  make_data_list(data, kind_of_data, tree_info, max_sen_len, vocab, catgy, article_id, useWords):
    
    data_list = []
    for line in tqdm(data,desc="Loading " + kind_of_data + " data"):
        tmp_dict = dict()
        line = line[:-1]
        tmp_dict['text'] = ' '.join(clean_str(' '.join(line.split("\t")[1].split(" "))).split(" ")[:useWords])
        [vocab[word] for word in tmp_dict['text'].split(" ")]
        tmp_dict['num_words'] = len(tmp_dict['text'].split(" "))
        max_sen_len = max(max_sen_len, tmp_dict['num_words'])
        tmp_dict['split'] = kind_of_data
        tmp_dict['hie_info'] = list(set([tree_info[cat] for cat in line.split("\t")[0].split(",")]))
        tmp_dict['catgy'] = [cat for cat in line.split("\t")[0].split(",")]
        [catgy[cat] for cat in line.split("\t")[0].split(",")]
        tmp_dict['id'] = str(article_id)
        article_id += 1
        data_list.append(tmp_dict)
        #print(data_list)
        del tmp_dict
    #print(catgy)
    return data_list, max_sen_len, vocab, catgy, article_id

# read data
# =========================================================
def data_load(train, valid, test, tree_info, use_words):
    vocab = defaultdict( lambda: len(vocab) )
    catgy = defaultdict( lambda: len(catgy) )
    article_id = 0
    max_sen_len = 0

    train_list, max_sen_len, vocab, catgy, article_id = make_data_list(train, 'train', tree_info, max_sen_len, vocab, catgy, article_id, use_words) 
    valid_list, max_sen_len, vocab, catgy, article_id = make_data_list(valid, 'valid', tree_info, max_sen_len, vocab, catgy, article_id, use_words) 
    test_list, max_sen_len, vocab, catgy, article_id = make_data_list(test, 'test', tree_info, max_sen_len, vocab, catgy, article_id, use_words) 
    class_dim = len(catgy)

    data = {}
    data['train'] = train_list
    data['test'] = test_list
    data['valid'] = valid_list
    data['vocab'] = vocab
    data['catgy'] = catgy
    data['max_sen_len'] = max_sen_len
    data['class_dim'] = class_dim
    return data


# read word embedding
# =========================================================
def embedding_weights_load(words_map,embedding_weights_path):
    pre_trained_embedding = None
    try:
        model = FastText.load_fasttext_format(embedding_weights_path)
        pre_trained_embedding = "bin"
    except:
        print ("fastText binary file (.bin) is not found!")
        if os.path.exists("./Word_embedding/cc.en.300.vec"):
            print ("Using wikipedia(en) pre-trained word vectors.")
        else:
            print ("Downloading wikipedia(en) pre-trained word vectors.")
            chakin.download(number=2, save_dir="./Word_embedding")
        print ("Loading vectors...")
        if os.path.exists("./Word_embedding_model.pkl"):
            with open("./Word_embedding_model.pkl", mode="rb") as f:
                model = pickle.load(f)
        else:
            model =  KeyedVectors.load_word2vec_format('./Word_embedding/cc.en.300.vec')
            with open("Word_embedding_model.pkl", mode="wb") as f:
                pickle.dump(model, f)
        pre_trained_embedding = "txt"

    vocab_size = len(words_map)
    word_dimension = model['a'].shape[0]
    w = np.zeros((vocab_size,word_dimension),dtype=np.float32)

    for k,v in words_map.items():
        word = k
        word_number = v
        
        try:
                w[word_number][:] = model[word]
        except KeyError as e:
                if pre_trained_embedding == "bin":
                    w[word_number][:] = model.seeded_vector(word)
                else:
                    np.random.seed(word_number)
                    w[word_number][:] = np.random.uniform(-0.25, 0.25, word_dimension)
    return w


# Conversion from network output to label
# =========================================================
def get_catgy_mapping(network_output_order_list, test_labels, prediction,current_depth):
    
    predict_result = []
    grand_labels = []
    
    for i in range(len(test_labels)):
        predict_result.append([])
        grand_labels.append([])

    class_dim = prediction.shape[1]

    row_idx, col_idx, val_idx = [], [], []
    for i in range(len(test_labels)):
        l_list = list(set(test_labels[i]))
        for y in l_list:
            row_idx.append(i)
            col_idx.append(y)
            val_idx.append(1)
    m = max(row_idx) + 1
    n = max(col_idx) + 1
    n = max(class_dim, n)
    test_labels = sp.csr_matrix((val_idx, (row_idx, col_idx)), shape=(m, n), dtype=np.int8).todense()

    np_orderList = np.array(network_output_order_list)

    for i,j in tqdm(enumerate(prediction), desc="Generating predict labels..."):
        one_hots = np.where(j == 1)[0]
        if len(one_hots) >= 1:
            predict_result[i] = np_orderList[one_hots].tolist()

    output_grand_truth_file_name = "CNN/RESULT/grand_truth_" + current_depth + ".csv"
    with open(output_grand_truth_file_name, 'w') as f:
        f.write(','.join(network_output_order_list)+"\n")

    with open(output_grand_truth_file_name, 'a') as f:
        for i,j in tqdm(enumerate(test_labels), desc="Generating grand truth labels..."):
            one_hots = np.where(j == 1)[1]
            if len(one_hots) >= 1:
                grand_labels[i] = np_orderList[one_hots].tolist()
                f.write(",".join(grand_labels[i])+"\n")
            else:
                f.write("\n")

    return grand_labels,predict_result

# Write results to a file
# =========================================================
def write_out_prediction(GrandLabels, PredResult, input_data_dic):

    # Writing out prediction
    # ===================================================
    print ("-"*50)
    print ("Writing out prediction...")
    test_data = input_data_dic['test']
    result_file = open("./CNN/RESULT/Prediction.txt", mode="w")
    result_file.write("Grand-truth-label\tPrediction-labels\tInput-text\n")
    for g,p,t in zip(GrandLabels, PredResult, test_data):
        result_file.write("{}\t{}\t{}\n".format(','.join(sorted(g)), ','.join(sorted(p)), t['text']))
    result_file.close()

# conversion of data
#========================================================

# conversion from text data to ndarray
# =========================================================
def build_input_sentence_data(sentences):
    x = np.array(sentences)
    return x

# conversion from sequence label to the number
# =========================================================
def build_input_label_data(labels, class_order):
    from sklearn.preprocessing import MultiLabelBinarizer
    from itertools import chain

    bml = MultiLabelBinarizer(classes=class_order, sparse_output=True)
    indexes = sp.find(bml.fit_transform(labels)) 
    y = []

    for i in range(len(labels)):
        y.append([])
    for i,j in zip(indexes[0], indexes[1]):
        y[i].append(j)
    return y

# padding operation
# =========================================================
def pad_sentences(sentences, padding_word=-1, max_length=50):
    sequence_length = max(max(len(x) for x in sentences), max_length)
    padded_sentences = []
    for i in range(len(sentences)):
        sentence = sentences[i]
        if len(sentence) < max_length:
            num_padding = sequence_length - len(sentence)
            new_sentence = sentence + [padding_word] * num_padding
        else:
            new_sentence = sentence[:max_length]
        padded_sentences.append(new_sentence)
    return padded_sentences

# conversion from documents and labels to the numbers
# =========================================================
def build_problem(learning_categories, depth, input_data_dic):

    train_data = input_data_dic['train']
    validation_data = input_data_dic['valid']
    test_data = input_data_dic['test']
    vocab = input_data_dic['vocab']
    max_sen_len = input_data_dic['max_sen_len']

    if depth == "flat":
        trn_text = [[vocab[word] for word in doc['text'].split()] for doc in train_data]
        trn_labels = [doc['catgy'] for doc in train_data]
        val_text = [[vocab[word] for word in doc['text'].split()] for doc in validation_data]
        val_labels = [doc['catgy'] for doc in validation_data]
        tst_text = [[vocab[word] for word in doc['text'].split()] for doc in test_data]
        tst_labels = [doc['catgy'] for doc in test_data]

    else:
        layer = int(depth[:-2])
        trn_text = [[vocab[word] for word in doc['text'].split()] for doc in train_data if (layer in doc['hie_info']) or ((layer-1) in doc['hie_info'])]
        trn_labels = [list( set(doc['catgy']) & set(learning_categories)) for doc in train_data if (layer in doc['hie_info']) or ((layer-1) in doc['hie_info'])]
        val_text = [[vocab[word] for word in doc['text'].split()] for doc in validation_data if (layer in doc['hie_info']) or ((layer-1) in doc['hie_info'])]
        val_labels = [list( set(doc['catgy']) & set(learning_categories)) for doc in validation_data if (layer in doc['hie_info']) or ((layer-1) in doc['hie_info'])]
        tst_text = [[vocab[word] for word in doc['text'].split()] for doc in test_data]
        tst_labels = [list( set(doc['catgy']) & set(learning_categories)) if layer in doc['hie_info'] else [] for doc in test_data]

    trn_padded = pad_sentences(trn_text, max_length=max_sen_len)
    val_padded = pad_sentences(val_text, max_length=max_sen_len)
    tst_padded = pad_sentences(tst_text, max_length=max_sen_len)
    x_trn = build_input_sentence_data(trn_padded)
    x_val = build_input_sentence_data(val_padded)
    x_tst = build_input_sentence_data(tst_padded)
    y_trn = build_input_label_data(trn_labels,learning_categories)
    y_val = build_input_label_data(val_labels, learning_categories)
    y_tst = build_input_label_data(tst_labels, learning_categories)

    return x_trn, y_trn, x_val, y_val, x_tst, y_tst


# conversion from the number to an ordinal number
# =========================================================
def order_n(i): return {1:"1st", 2:"2nd", 3:"3rd"}.get(i) or "%dth"%i
