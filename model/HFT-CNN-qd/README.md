HFT-CNN
==
![result](https://github.com/ShimShim46/HFT-CNN/blob/media/demo.gif)
These four code/models are Chainer based implementation for text categorization by Convolutional Neural Networks.
* Flat model: Flat non-hierarchical model
* Without Fine-tuning (WoFt) model: Hierarchical model but without Fine-tuning
* Hierarchical Fine-Tuning (HFT) model: Hierarchical and Fine-tuning model
* XML-CNN model [[Liu+'17](http://nyc.lti.cs.cmu.edu/yiming/Publications/jliu-sigir17.pdf)]


If you use any part of this code in my research, please cite my paper:
```
@inproceedings{HFT-CNN,
    title={HFT-CNN: Learning Hierarchical Category Structure for Multi-label Short Text Categorization},
    Author={Kazuya Shimura and Jiyi Li and Fumiyo Fukumoto},
    booktitle={Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing},
    pages={811--816},
    year={2018},
}
```
Contact: Kazuya Shimura, g17tk008(at)yamanashi(dot)ac(dot)jp

<!-- https://cl.cs.yamanashi.ac.jp -->

If you have further questions, please feel free to contact me.

### Features of each model

|              Feature\Method |   Flat model  |   WoFt model  |   HFT model   |    XML-CNN model    |
|-----------------------:|:-------------:|:-------------:|:-------------:|:-------------------:|
|              Hierarchical Structure |               |       ✔       |       ✔       |                     |
|            Fine-tuning |               |       ✔       |       ✔       |                     |
|                Pooling Type | 1-max pooling | 1-max pooling | 1-max pooling | dynamic max pooling |
| Compact Representation |               |               |               |          ✔          |

## Setup
In order to run the code, I recommend the following environment.
* Python 3.5.4 or higher.
* Chainer 4.0.0 or higher. ([chainer](http://chainer.org/))
* CuPy 4.0.0 or higher.  ([cupy](https://cupy.chainer.org/))

## Requirements
The code require GPU environment. Please see requirements.txt to run my code.


## Installation
1. Download code from **clone or download**
1. Install the requirements: reguriements.txt
1.  You can also use Python data science platform, [Anaconda](https://www.anaconda.com/enterprise/) as follows:
    * Download Anaconda from (https://www.anaconda.com/download/)
    * Example: Anaconda 5.1 for Linux(x86 architecture, 64bit) Installer 
        ```
        wget https://repo.continuum.io/archive/Anaconda3-5.1.0-Linux-x86_64.sh
        
        bash Anaconda3-5.1.0-Linux-x86_64.sh
        
        ## Create virtual environments with the Anaconda Python distribution ##
        conda env create -f=hft_cnn_env.yml

        source activate hft_cnn_env
        ```
1. You can run my HFT-CNN code in this environment
   
## Directory structure
```
|--CNN  ##  Directory for saving the models
|  |--LOG     ## Log files
|  |--PARAMS  ## CNN parameters
|  |--RESULT  ## Store categorization results
|--cnn_model.py  ##  CNN model
|--cnn_train.py  ##  CNN training
|--data_helper.py  ##  Data helper
|--example.sh  ##  you can run and categorize my code by using sample data
|--hft_cnn_env.yml ##  Anaconda components dependencies
|--LICENSE  ## MIT LICENSE
|--MyEvaluator.py  ##  CNN training (validation)
|--MyUpdater.py  ##  CNN training (iteration)
|--README.md  ## README
|--requirements.txt  ## Dependencies(pip)
|--Sample_data  ## Amazon sample data
|  |--sample_test.txt  ## Sample test data
|  |--sample_train.txt  ## Sample training data
|  |--sample_valid.txt  ## Sample validation data
|--train.py  ## Main
|--Tree
|  |--Amazon_all.tree  ## a hierarchical structure provided by Amazon
|--tree.py  ## Tree operation
|--Word_embedding  ## Directory of word embedding
|--xml_cnn_model.py  ##  Chainer's version of XML-CNN model [Liu+'17]
```

## Quick-start
You can categorize sample data (Amazon product reviews) by running example.sh, with the Flat model.

```
bash example.sh
--------------------------------------------------
Loading data...
Loading train data: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 465927/465927 [00:18<00:00, 24959.42it/s]
Loading valid data: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 24522/24522 [00:00<00:00, 27551.44it/s]
Loading test data: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 153025/153025 [00:05<00:00, 27051.62it/s]
--------------------------------------------------
Loading Word embedings...
```
The results are stored: 
* RESULT: categorization result
* PARAMS: obtained CNN parameters
* LOG: Log file


## Training model change
You can change a training model by modifying the "ModelType" in the file "example.sh"

```
## Network Type (XML-CNN,  CNN-Flat,  CNN-Hierarchy,  CNN-fine-tuning or Pre-process)
ModelType=XML-CNN
```
* CNN-Flat: Flat model
* CNN-Hierarchy:  WoFt model
* CNN-fine-tuning:  HTF model
* XML-CNN: XML-CNN model

Notes:

* When you choose CNN-Hierarchy or CNN-fine-tuning, learn a model by using **Pre-process**
    * Example: ``` ModelType=Pre-process => ModelType=CNN-Hierarchy```
    ![result](https://github.com/ShimShim46/HFT-CNN/blob/media/pre-process_demo.gif)
* When you choose **Pre-process**, it learns the top level of a hierarchy and stores CNN parameters. The stored parameters are used in both CNN-Hierarchy and CNN-fine-tuning.

## Word embedding
my code utilize word embedding obtained by [fastText](https://github.com/facebookresearch/fastText).
There are two options:
1.  You can simply run example.sh. In this case, ```wiki.en.vec``` is downloaded in the directory Word_embedding and is used for training.

1. You can specify your own "bin" file by making a path ```EmbeddingWeightsPath``` in the example.sh file.
```
## Embedding Weights Type (fastText .bin)
EmbeddingWeightsPath=./Word_embedding/
```

## Learning by using your own data
### Data
 
* Training data: labeled training data
* Validation data: labeled validation data
* Test data:  test data for categorization

Validation data is used to evaluate generalization error for each
epoch. It is used to find when overfitting starts during the
training. Training is then stopped before convergence to avoid the
overfitting, i.e., [early stopping](https://docs.chainer.org/en/stable/reference/generated/chainer.training.triggers.EarlyStoppingTrigger.html). The parameter whose generalization
error is the lowest among all the epochs is stored.

### Format
The data format is:
* The first column: category labels. 
    * Each label is split by ",".
* The second column: document.
    * Each word in the document is split by a space, " ".

Each column is split by Tab(\t).

Example:
```
LABEL1  I am a boy .
LABEL2,LABEL6  This is my pen .
LABEL3,LABEL1   ...
```

### Hierarchical structure
When your data has a hierarchical structure, you can use my WoFT model and HTF model. Please see "TREE/Amazon_all.tree".
You can use your own hierarchical structure by overwriting "TreefilePath" in the example.sh file.

## License
MIT

## References
[Liu+'17]

J. Liu, W-C. Chang, Y. Wu, and Y. Yang. 2017. Deep
Learning for Extreme Multi-Label Text Classifica-
tion. In Proc. of the 40th International ACM SIGIR
Conference on Research and Development in Infor-
mation Retrieval, pages 115–124.
