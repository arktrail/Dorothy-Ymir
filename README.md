# Dorothy AI Patent Classifier
This github repository includes code for Dorothy AI Patent Classifier
## Table of Contents

* [Data generation and preprocesss](#data)
* [Machine learning model](#ml)
    * [FastText](#fasttext)
    * [Tencent's NeuralClassifier](#tencent)
    * [HFT-CNN](#hftcnn)
* [Evaluation](#eval)
* [Visualization](#visual)
* [Web app](#webapp)

## Data generation and preprocess <a id="sys-arc"></a>

First we ??? [Yining to fill]

Second we parse the cpc field into labels we need (section, classs, subclass, etc.), convert the text into a list of tokens, and split the data into train, valid, and test datasets. This step also removes all punctuations and convert all uppercase letters into lower case. This can be done by running the  file, for example:
[data_preprocess/text_preprocess.py][https://github.com/yyn19951228/Dorothy-Ymir/blob/master/data_preprocess/text_preprocess.py]
```sh
$ python3 -u data_preprocess/text_preprocess.py /pylon5/sez3a3p/yyn1228/data/json_reparse /pylon5/sez3a3p/yyn1228/data/all_data
```

## Machine learning model <a id="ml"></a>

### FastText <a id="fasttext"></a>
### Tencent's NeuralClassifier <a id="tencent"></a>
### HFT-CNN <a id="hftcnn"></a>

## Evaluation <a id="eval"></a>

## Visualization <a id="visual"></a>

## Web app <a id="webapp"></a>

[Yining or Zhixuan] Add something to describe it or add a link to another README?


