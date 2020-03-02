#! /bin/bash
DataDIR=./My_data
Train=${DataDIR}/train.json
Test=${DataDIR}/test.json
Valid=${DataDIR}/valid.json

## Embedding Weights Type (fastText .bin)
EmbeddingWeightsPath=./Word_embedding/
## Network Type (XML-CNN,  CNN-Flat,  CNN-Hierarchy,  CNN-fine-tuning or Pre-process)
ModelType=Pre-process
### the limit of the sequence 
USE_WORDS=150
### Tree file path
TreefilePath=./Tree/CPC_new.tree

mkdir -p CNN
mkdir -p CNN/PARAMS
mkdir -p CNN/LOG
mkdir -p CNN/RESULT
mkdir -p Word_embedding

python3.5 ./train.py ${Train} ${Test} ${Valid} ${EmbeddingWeightsPath} ${ModelType} ${TreefilePath} ${USE_WORDS}
