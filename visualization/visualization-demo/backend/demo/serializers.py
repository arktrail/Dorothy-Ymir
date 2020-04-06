from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from .models import Tree, Prediction, Document


class TreeSerializer(serializers.ModelSerializer):
    # children = RecursiveField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Tree
        fields = ('name', 'symbol', 'prob', 'true', 'children')

    def get_leaf_nodes(self, obj):
        return TreeSerializer(obj.get_children(), many=True).data


class PredictionSerializer(serializers.ModelSerializer):
    tree = TreeSerializer(many=True, read_only=True)

    class Meta:
        model = Prediction
        fields = ['pred_id', 'tree']


class DocumentSerializer(serializers.ModelSerializer):
    prediction = PredictionSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ['document_id', 'document_content', 'prediction']
