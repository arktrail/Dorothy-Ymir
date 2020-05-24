import os
from fasttext import train_supervised
import fasttext
import sys

def print_results(N, p, r):
    print("N\t" + str(N))
    print("P@{}\t{:.3f}".format(1, p))
    print("R@{}\t{:.3f}".format(1, r))

def train_fasttext(input_directory, output_path):
    
    train_data = os.path.join(input_directory, 'train.json')
    valid_data = os.path.join(input_directory, 'valid.json')
    # train_supervised uses the same arguments and defaults as the fastText cli
    model = train_supervised(
        input=train_data, epoch=10, lr=0.5, wordNgrams=2, verbose=2, minCount=1, loss='ova'
    )
    print_results(*model.test(valid_data))
    model.save_model(output_path)


train_fasttext(sys.argv[1], sys.argv[2])
