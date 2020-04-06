from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pred_id>', views.get_prediction_result,
         name='get_prediction_result'),
    path('<document_id>', views.get_document, name='get_document'),
]
