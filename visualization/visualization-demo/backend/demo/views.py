from django.shortcuts import render
from rest_framework import viewsets          # add this
from .models import Tree, Prediction, Document                     # add this
from django.http import HttpResponse
from django.core import serializers
from .inference import Inference
from .serializers import DocumentSerializer, TreeSerializer, PredictionSerializer


def index(req):
    return HttpResponse("test response for index")


def get_prediction_result(req, pred_id):
    prediction = Prediction.objects.get(pred_id=pred_id)
    return HttpResponse(prediction)


def get_document(req, document_id):
    doc = Document.objects.get(document_id=document_id)
    doc_serializer = DocumentSerializer(
        Document.objects.all(), context={'request': req}, many=True)
    return HttpResponse(doc_serializer)


def predict(req, document_id):
    return Inference(document_id=document_id)


# class DemoView(viewsets.ModelViewSet):       # add this
#     serializer_class = DemoSerializer          # add this
#     queryset = Prediction.objects.all()
    # Create your views here.
