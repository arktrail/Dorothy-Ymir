# from django.shortcuts import render
# from rest_framework import viewsets          # add this
from .models import Tree, Prediction, Document                     # add this
from django.http import HttpResponse
# from django.core import serializers
from .inference import Inference
from .serializers import DocumentSerializer, TreeSerializer, PredictionSerializer
import json
import pickle
import heapq
import collections

DESCRIPTION_DICT_FILENAME = 'cpc_schema_description.'
SECTION_PREDICT_RESULT_FILENAME = 'probability_1.csv'
CLASS_PREDICT_RESULT_FILENAME = 'probability_2.csv'
SUBCLASS_PREDICT_RESULT_FILENAME = 'probability_3.csv'
TRUE_LABEL_FILENAME = 'Prediction.txt'
SEPARATOR_1 = '@'
SEPARATOR_2 = ','
SECTION = 'SECTION'
CLASS = 'CLASS'
SUBCLASS = 'SUBCLASS'
INSTANCE_INDEX = 5

def index(req):
    return HttpResponse("test response for index")


def get_prediction_result(req, pred_id):
    prediction = Prediction.objects.get(pred_id=pred_id)
    return HttpResponse(prediction)


def get_document(req, document_id):
    # doc = Document.objects.get(document_id=document_id)
    # doc_serializer = DocumentSerializer(
    #     Document.objects.all(), context={'request': req}, many=True)
    # return HttpResponse(doc_serializer)

    
    description_dict = load_description_from_file()
    # run the script to predict
    tree = build_tree(description_dict)
    tree_json = json.dumps(tree)
    return HttpResponse(tree_json, content_type='application/json')


def predict(req, document_id):
    return Inference(document_id=document_id)

def load_description_from_file():
    file = open(DESCRIPTION_DICT_FILENAME, 'rb')
    # dump information to that file
    data = pickle.load(file)
    # close the file
    file.close()
    return data

def read_predict_file_to_dict(file):
    f = open(file, "r")
    labels = f.readline().split('\n')[0].split(',')
    for _ in range(INSTANCE_INDEX - 1):
        f.readline()
    preds = [float(pred) for pred in f.readline().split('\n')[0].split(',')]
    f.close()
    return dict(zip(labels, preds))

def read_true_label_from_file():
    f = open(TRUE_LABEL_FILENAME, "r")
    for _ in range(INSTANCE_INDEX):
        f.readline()
    true_labels = f.readline().split('\t')[0].split(SEPARATOR_2)
    true_labels = [true_label.replace(SEPARATOR_1,'') for true_label in true_labels]
    return set(true_labels)

def build_tree(description_dict):
    # read file to dict
    section_data = read_predict_file_to_dict(SECTION_PREDICT_RESULT_FILENAME)
    class_data = read_predict_file_to_dict(CLASS_PREDICT_RESULT_FILENAME)
    subclass_data = read_predict_file_to_dict(SUBCLASS_PREDICT_RESULT_FILENAME)
    true_labels_set = read_true_label_from_file()

    # sort subclass data
    subclass_data = dict(sorted(subclass_data.items(), key=lambda x: x[1], reverse=True))

    # get top k
    # subclass_ = heapq.nlargest(leaf_num, subclass_data, key=subclass_data.get)
    # subclass_data = {k:subclass_data[k] for k in subclass_}

    # create root, treat children as dict for quick access
    tree = {'name': 'root', 'symbol': '', 'children': {}}

    # section
    for s, prob in section_data.items():
        is_true_label = s in true_labels_set
        tree['children'][s] = create_tree_node(s, prob, description_dict, level=SECTION,  last=False, order=None, is_true_label=is_true_label)

    # class
    for c, prob in class_data.items():
        s = c.split(SEPARATOR_1)[0]
        c_ = ''.join(c.split(SEPARATOR_1))
        is_true_label = c_ in true_labels_set
        tree['children'][s]['children'][c_] = create_tree_node(c_, prob, description_dict, level=CLASS, last=False, order=None, is_true_label=is_true_label)

    # subclass
    for index, sub in enumerate(subclass_data.keys()):
        prob = subclass_data[sub]
        sub_split = sub.split(SEPARATOR_1)
        s = sub_split[0]
        c = ''.join(sub_split[:2])
        sub_ = ''.join(sub_split)
        is_true_label = sub_ in true_labels_set
        if prob == 0 and not is_true_label:
            continue
        tree['children'][s]['children'][c]['children'][sub_] = create_tree_node(sub_, prob, description_dict, level=SUBCLASS, last=True, order=index, is_true_label=is_true_label)

    # convert children dict to list and remove zero prob parent nodes
    tree_children = []
    for s in tree['children'].values():
        s_children = []
        for c in s['children'].values():
            c['children'] = list(c['children'].values())
            if len(c['children']) != 0:
                s_children.append(c)
                # add order for class
                c['order'] = min([sub['order'] for sub in c['children']])
        if len(s_children) != 0:
            s['children'] = s_children
            s['order'] = min([c['order'] for c in s['children']])
            s_children.append(c)
            tree_children.append(s)
    if tree_children != 0:
        tree['children'] = tree_children

    return tree

def create_tree_node(symbol, prob, description_dict, level, last, order, is_true_label):
    description = symbol + ' ' + description_dict[symbol]
    node = {'name': description, 'symbol': symbol, 'level': level, 'prob': prob, 'true': is_true_label}
    if last: 
        node['order'] = order
    else:
        node['children'] = {}
    return node

# class DemoView(viewsets.ModelViewSet):       # add this
#     serializer_class = DemoSerializer          # add this
#     queryset = Prediction.objects.all()
    # Create your views here.
