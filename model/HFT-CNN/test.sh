#! /bin/bash
My_Test=../processed_data/test.json

## Embedding Weights Type (fastText .bin)
EmbeddingWeightsPath=./Word_embedding/
### the limit of the sequence 
USE_WORDS=300
### Tree file path
TreefilePath=./Tree/CPC_subclass.tree
### Data info
LabelName=doc_label
InputTextName=doc_token
VocabPath=./vocab.pkl
CatgyPath=./catgy.pkl
OutputProbPath=./test.csv

python3.5 test.py ${My_Test} ${EmbeddingWeightsPath} ${TreefilePath} ${USE_WORDS} ${LabelName} ${InputTextName} ${VocabPath} ${CatgyPath} ${OutputProbPath}
