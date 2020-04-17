# from django.shortcuts import render
# from rest_framework import viewsets          # add this
# from .models import Tree, Prediction, Document                     # add this
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
# from django.core import serializers
from .serializers import DocumentSerializer, TreeSerializer, PredictionSerializer
from .predict import predict
from .treebuilder import build_tree, load_description_from_file
from .formatter import change_format
import json
import pickle
import heapq
import collections


def index(req):
    return HttpResponse("test response for index")


def get_prediction_result(req, query):
    prediction = Prediction.objects.get(pred_id=pred_id)
    return HttpResponse(prediction)


@csrf_exempt
def get_document(req):
    # def get_document(req, query):
    # doc = Document.objects.get(document_id=document_id)
    # doc_serializer = DocumentSerializer(
    #     Document.objects.all(), context={'request': req}, many=True)
    # return HttpResponse(doc_serializer)

    print("get document and query")
    print(pretty_request(req))

    query = req.body.decode("utf-8")
    print("query is {}".format(query))

    prediction = ""
    if query is not None or len(query) > 0:
        prediction = predict(query)
    else:
        print("didn't get query, the query is {}".format(query))

    prediction = change_format(prediction=prediction)

    description_dict = load_description_from_file()
    # run the script to predict
    tree = build_tree(prediction=prediction,
                      model_type="fasttext", description_dict=description_dict)
    tree_json = json.dumps(tree)
    return HttpResponse(tree_json, content_type='application/json')


def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize()
                           for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )
