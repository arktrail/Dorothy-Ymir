#! /bin/bash
DataDIR=../../../data/summary_only_nonstop
Train=${DataDIR}/train.json
Test=${DataDIR}/test.json
Valid=${DataDIR}/valid.json

## Embedding Weights Type (fastText .bin)
EmbeddingWeightsPath=./Word_embedding/
### the limit of the sequence 
USE_WORDS=300
### Tree file path
TreefilePath=./Tree/CPC_subclass.tree
### Data info
LabelName=doc_label
InputTextName=doc_token

### Don`t change the OutputDIR folder here!
OutputDIR=CNN 
mkdir -p ${OutputDIR}
mkdir -p ${OutputDIR}/PARAMS
mkdir -p ${OutputDIR}/LOG
mkdir -p ${OutputDIR}/RESULT
mkdir -p Word_embedding

### Preprocess Use only when model type is CNN-Hierarchy or CNN-fine-tuning
ModelType=Pre-process
python train.py ${Train} ${Test} ${Valid} ${EmbeddingWeightsPath} ${ModelType} ${TreefilePath} ${USE_WORDS} ${LabelName} ${InputTextName}
### Training model
## Network Type (XML-CNN,  CNN-Flat,  CNN-Hierarchy,  CNN-fine-tuning)
ModelType=CNN-Hierarchy
python train.py ${Train} ${Test} ${Valid} ${EmbeddingWeightsPath} ${ModelType} ${TreefilePath} ${USE_WORDS} ${LabelName} ${InputTextName}
