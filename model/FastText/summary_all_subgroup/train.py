import os
from fasttext import train_supervised


def print_results(N, p, r):
    print("N\t" + str(N))
    print("P@{}\t{:.3f}".format(1, p))
    print("R@{}\t{:.3f}".format(1, r))

if __name__ == "__main__":
    directory = "/pylon5/sez3a3p/yyn1228/data/all_summary_fasttext_subgroup"
    train_data = os.path.join(directory, 'train.json')
    valid_data = os.path.join(directory, 'valid.json')

    # train_supervised uses the same arguments and defaults as the fastText cli
    model = train_supervised(
        input=train_data, epoch=30, lr=0.2, wordNgrams=2, verbose=1, minCount=5, loss="hs", dim=300, pretrainedVectors="/pylon5/sez3a3p/yyn1228/Dorothy-Ymir/model/FastText/summary_all_group/group.vec"
    )
    print_results(*model.test(valid_data))
    model.save_model("fasttext_model.bin")
