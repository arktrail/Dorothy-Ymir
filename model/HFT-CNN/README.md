HFT-CNN Instructions
==

This file describes how to train models using HFT-CNN on PSC

## Setup

Install the following environments.

* Python 3.5.4 or higher.
* Chainer 4.0.0 or higher. ([chainer](http://chainer.org/))
* CuPy 4.0.0 or higher.  ([cupy](https://cupy.chainer.org/))

Install the requirements: requirements.txt

## Directory structure

```
|--CNN  ##  Directory for saving the models
|  |--LOG     ## Log files
|  |--PARAMS  ## CNN parameters
|  |--RESULT  ## Store categorization results
├── cnn_model_mulgpu.py ##  CNN model on two gpu
├── cnn_model.py ##  CNN model
├── cnn_train_mulgpu.py ##  CNN training on two gpu
├── cnn_train.py ##  CNN training
├── data_helper.py ##  Data helper
├── example.sh ## configuration and running train
├── gpu_model_usage_extension.py
├── hft_cnn_env.yml ##  Anaconda components dependencies
├── LICENSE ## MIT LICENSE
├── MyEvaluator.py ##  CNN training (validation)
├── MyUpdater_mulgpu.py ##  CNN training (iteration) on two gpu
├── MyUpdater.py ##  CNN training (iteration)
├── README.md
├── requirements.txt  ## Dependencies(pip)
├── test.job ## Runing test job on PSC
├── test.py ## Test
├── test.sh ## configuration and running test
├── train.job ## Running train job on PSC
├── train_mulgpu.py ## Main on two gpu
├── train.py ## Main
├── Tree
│   ├── CPC_subclass.tree ## a hierarchical structure on subclass level
│   ├── CPC_subgroup.tree ## a hierarchical structure on subgroup level
│   └── create_tree.py
├── tree.py ## Tree operation
├── Word_embedding ## Directory of word embedding
└── xml_cnn_model.py  ##  Chainer's version of XML-CNN model [Liu+'17]
```

## Training your model

1. Open **train.sh**

2. Edit DataDIR to your data file path, make sure it contains train, valid and test json file

   The following training datasets are available:

   - **Label**: subgroup level; **text**: title, abstract, claim
     - ../../../../../data/processed_data/train.json
     - ../../../../../data/processed_data/valid.json
     - ../../../../../data/processed_data/test.json
   - **Label**: subgroup level; **text**: brief summary
     - ../../../../../data/summary_only/train.json
     - ../../../../../data/summary_only/valid.json
     - ../../../../../data/summary_only/test.json
   - **Label**: subgroup level; **text**: description
     - ../../../../../data/desc_only/train.json
     - ../../../../../data/desc_only/valid.json
     - ../../../../../data/desc_only/test.json

3. Edit USE_WORDS to determine how many words used in model for each data point

4. Edit TreefilePath using your hierarchical structure

5. Edit LabelName and InputTestName corresponding to names in your data file

6. Edit line 31 ModelType to XML-CNN,  CNN-Flat,  CNN-Hierarchy or CNN-fine-tuning

   - CNN-Flat: Flat model

   - CNN-Hierarchy:  WoFt model

   - CNN-fine-tuning:  HTF model

   - XML-CNN: XML-CNN model
   - Notes:

     * When you choose CNN-Hierarchy or CNN-fine-tuning, learn a model by using **Pre-process**
     * When you choose **Pre-process**, it learns the top level of a hierarchy and stores CNN parameters. The stored parameters are used in both CNN-Hierarchy and CNN-fine-tuning.

6. Submit **train.job** on PSC using the following command:

   ```
   sbatch train.job
   ```

7. The results are stored:
   - RESULT: categorization result
   - PARAMS: obtained CNN parameters
   - LOG: Log file

##  Test your model

1. Open **test.sh**

2. Edit My_Test to your test file path

3. Edit OutputProbPath to store output probability file

4. Submit **test.job** on PSC using the following command:

   ```
   sbatch test.job
   ```

## Feature of each model

These four code/models are Chainer based implementation for text categorization by Convolutional Neural Networks.

* Flat model: Flat non-hierarchical model
* Without Fine-tuning (WoFt) model: Hierarchical model but without Fine-tuning
* Hierarchical Fine-Tuning (HFT) model: Hierarchical and Fine-tuning model
* XML-CNN model [[Liu+'17](http://nyc.lti.cs.cmu.edu/yiming/Publications/jliu-sigir17.pdf)]

|         Feature\Method |  Flat model   |  WoFt model   |   HFT model   |    XML-CNN model    |
| ---------------------: | :-----------: | :-----------: | :-----------: | :-----------------: |
| Hierarchical Structure |               |       ✔       |       ✔       |                     |
|            Fine-tuning |               |       ✔       |       ✔       |                     |
|           Pooling Type | 1-max pooling | 1-max pooling | 1-max pooling | dynamic max pooling |
| Compact Representation |               |               |               |          ✔          |

## Word embedding

my code utilize word embedding obtained by [fastText](https://github.com/facebookresearch/fastText).
There are two options:

1.  You can simply run example.sh. In this case, `cc.en.300.vec` is downloaded in the directory Word_embedding and is used for training.

1.  You can specify your own "bin" file by making a path ```EmbeddingWeightsPath``` in the example.sh file.

```
## Embedding Weights Type (fastText .bin)
EmbeddingWeightsPath=./Word_embedding/
```

## Citation and Resources

Resources came from [HFT-CNN](https://github.com/ShimShim46/HFT-CNN).

Reference [Paper](https://www.aclweb.org/anthology/D18-1093.pdf).

Citation:

```
@inproceedings{HFT-CNN,
    title={HFT-CNN: Learning Hierarchical Category Structure for Multi-label Short Text Categorization},
    Author={Kazuya Shimura and Jiyi Li and Fumiyo Fukumoto},
    booktitle={Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing},
    pages={811--816},
    year={2018},
}
```
## License
MIT

## References
[Liu+'17]

J. Liu, W-C. Chang, Y. Wu, and Y. Yang. 2017. Deep
Learning for Extreme Multi-Label Text Classifica-
tion. In Proc. of the 40th International ACM SIGIR
Conference on Research and Development in Infor-
mation Retrieval, pages 115–124.