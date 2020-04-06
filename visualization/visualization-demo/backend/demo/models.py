from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.


class Document(models.Model):
    document_id = models.CharField(
        max_length=20, unique=True, primary_key=True)
    document_content = models.TextField()


class Prediction(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    pred_id = models.PositiveIntegerField(primary_key=True)
    pred_title = models.CharField(max_length=200)


class Tree(MPTTModel):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, unique=False)
    symbol = models.CharField(max_length=50, unique=False)
    prob = models.FloatField()
    true = models.BooleanField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']
