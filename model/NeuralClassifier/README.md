# Instructions

This file describes how to train models using NeuralClassifier on PSC

## Copy template files

Log in on PSC using the credentials:
```
ssh yyn1228@bridges.psc.edu
Password: Dorothy2000
```

Go to the NeuralClassifier output folder:
```
cd /pylon5/sez3a3p/yyn1228/Dorothy-Ymir/model/NeuralClassifier/output
```

Copy the template folder into a new folder and make the folder name intuitive:
```
cp -R  template your_folder
```

Go to your new folder
```
cd your_folder
```


## Edit the slurm script

In your new folder, open train_eval.job and change line 13 into:
```
cd $SCRATCH/Dorothy-Ymir/model/NeuralClassifier/output/your_folder
```
You can also change the machine configurations in lines 1-6 as needed, but confirm with Yining before doing it. Please do not make any other changes.



## Edit the training configuration file

In your new folder, open train.json and change the configurations as needed according to [this file](https://github.com/yyn19951228/Dorothy-Ymir/blob/master/model/NeuralClassifier/NeuralNLP-NeuralClassifier-master/readme/Configuration.md)

If you want to change the data source, please edit the following fields:
* data.train_json_files
* data.validate_json_files
* data.test_json_files
* eval.text_file

The following training datasets are available:
* Label: subgroup level; text: title, abstract, claim
    * ../../../../../data/processed_data/train.json
    * ../../../../../data/processed_data/valid.json
    * ../../../../../data/processed_data/test.json
* Label: subgroup level; text: brief summary
    * ../../../../../data/summary_only/train.json
    * ../../../../../data/summary_only/valid.json
    * ../../../../../data/summary_only/test.json
* Label: subgroup level; text: description
    * ../../../../../data/desc_only/train.json
    * ../../../../../data/desc_only/valid.json
    * ../../../../../data/desc_only/test.json

If you change model_name, make sure you also change eval.model_dir to "checkpoint_dir_cpc/MODELNAME_best". There is no need to change other directories.


## Run the slurm job

After change the slurm script  and the training configuration file, run the slurm job using the following command:
```
sbatch train_eval.job
```

You can check the output periodically in train_eval.out. You can also track the status of the job using the following command:
```
squeue -u yyn1228
```

## Delete non-best model files

Because the model saves a model checkpoint for every epoch, which take a lot of space, make sure you delete all the non-best model files by using the following commands.

```
cd checkpoint_dir_cpc
find -not -name "*_best" -delete
```

Please double check you are in the checkpoint_dir_cpc folder before running the find command!!!

