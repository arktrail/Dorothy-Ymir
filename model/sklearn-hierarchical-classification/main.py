import pickle
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
from sklearn.decomposition import TruncatedSVD
from sklearn_hierarchical_classification.classifier import HierarchicalClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import SGDClassifier
from numpy import where
from sklearn.metrics import accuracy_score
from joblib import parallel_backend

from model_data_preprocess import build_tree_and_labels_from_data_multiple_label
from model_data_preprocess import SUB_CLASS

from model_evaluation import eval_top1_exist, eval_hard_thr

# ignore warnings
import warnings


def warn(*args, **kwargs):
    pass


warnings.warn = warn

RANDOM_STATE = 42
SCRATCH = "/pylon5/sez3a3p/yyn1228/sklearn_model/"


def read_data(path):
    data = []
    if isinstance(path, list):
        print("read data from list {}".format(len(path)))
        for p in path:
            data += pickle.load(open(p, "rb"))
        return data
    return pickle.load(open(path, "rb"))


def load_full_tree(tree_file_path):
    '''
    load the whole CPC tree, and convert for our format
    '''
    tree = pickle.load(open(tree_file_path, 'rb'))
    print(type(tree))
    cnt = 0
    for k, v in tree.items():
        print(k)
        print(v)
        cnt += 1
        if cnt == 5:
            break


def save_to_file_format(result, file_path):
    with open(file_path, "w") as file:
        for res in result:
            if len(res) == 0:
                file.write(res)
            else:
                for label in res:
                    file.write(label)
                    file.write(";")
            file.write("\n")


def main(dataFilePath):
    # read data
    print("start read data")
    data = read_data(dataFilePath)
    class_hierarchy, samples, labels, all_labels = build_tree_and_labels_from_data_multiple_label(
        data)
    print("finish read data")

    # print("class_hierarchy: ", class_hierarchy)

    # build model
    print("start build model!")
    # base_estimator = make_pipeline(
    #     MultinomialNB()
    #     TruncatedSVD(n_components=24),
    #     svm.SVC(
    #         gamma=0.001,
    #         kernel="rbf",
    #         probability=True
    #     )
    # )

    vectorizer = TfidfVectorizer(
        strip_accents=None,
        lowercase=True,
        analyzer="word",
        ngram_range=(1, 3),
        max_df=1.0,
        min_df=0.0,
        binary=False,
        use_idf=True,
        smooth_idf=True,
        sublinear_tf=True,
        max_features=70000
    )
    binary_clf = OneVsRestClassifier(SGDClassifier(
        shuffle=True,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        penalty='elasticnet',
        loss='modified_huber'))
    base_estimator = make_pipeline(CountVectorizer(
        max_df=1.0,
        min_df=0.0,
        ngram_range=((1, 3))
    ), TfidfTransformer(
        use_idf=True,
        smooth_idf=True,
        sublinear_tf=True
    ), binary_clf)

    mlb = MultiLabelBinarizer()
    clf = HierarchicalClassifier(
        base_estimator=base_estimator,
        class_hierarchy=class_hierarchy,
        mlb=mlb,
        feature_extraction="raw",
        use_decision_function=True
    )

    X = samples
    y = mlb.fit_transform(labels)

    mlb_classes = list(mlb.classes_)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.1,
        random_state=RANDOM_STATE
    )

    print("train size", len(X_train))
    print("test size", len(X_test))

    print("start training")
    clf.fit(X_train, y_train)

    # test save and load model
    # save the model to disk
    print("start saving model")
    model_path = SCRATCH + "base_model.sav"
    pickle.dump(clf, open(model_path, 'wb'))

    print("start loading model")
    loaded_clf = pickle.load(open(model_path, 'rb'))

    print("start predicting")
    y_pred = loaded_clf.predict_proba(X_test)
    # print("y_pred", y_pred[0])
    # print("y_test", y_test[0])

    # Calculate accuracy

    y_pred[where(y_pred == 0)] = -1
    top1_acc = eval_top1_exist(
        y_pred, y_test, mlb_classes, all_labels[SUB_CLASS])
    print("top1 accuracy", top1_acc)

    # accuracy = accuracy_score(y_test, y_pred > -0.2)
    # print(accuracy)


def go(path):
    # read data
    print("start read data")
    data = read_data(path)
    class_hierarchy, samples, labels, all_labels = build_tree_and_labels_from_data_multiple_label(
        data)
    print("finish read data")
    print(class_hierarchy)


def run_metrics(dataFilePath):
    # read data
    print("start read data")
    train_data_path = dataFilePath[0:13]
    test_data_path = dataFilePath[13:16]
    train_data = read_data(train_data_path)
    test_data = read_data(test_data_path)
    #  train_data_path = dataFilePath
    #  test_data_path = dataFilePath
    #  train_data = read_data(train_data_path)[0:100]
    #  test_data = read_data(test_data_path)[101:120]
    class_hierarchy, _, _, all_labels = build_tree_and_labels_from_data_multiple_label(
        train_data + test_data)
    _, train_samples, train_labels, _ = build_tree_and_labels_from_data_multiple_label(
        train_data)
    _, test_samples, test_labels, _ = build_tree_and_labels_from_data_multiple_label(
        test_data)
    len_train = len(train_data)
    len_test = len(test_data)
    print("finish read data, len_train: {}, len_test: {}".format(len_train, len_test))

    # build model
    print("start build model!")

    binary_clf = OneVsRestClassifier(SGDClassifier(
        shuffle=True,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        penalty='elasticnet',
        loss='modified_huber'))
    base_estimator = make_pipeline(CountVectorizer(
        max_df=1.0,
        min_df=0.0,
        ngram_range=((1, 3))
    ), TfidfTransformer(
        use_idf=True,
        smooth_idf=True,
        sublinear_tf=True
    ), binary_clf)

    mlb = MultiLabelBinarizer()
    clf = HierarchicalClassifier(
        base_estimator=base_estimator,
        class_hierarchy=class_hierarchy,
        mlb=mlb,
        feature_extraction="raw",
        use_decision_function=True
    )

    train_X = train_samples
    test_X = test_samples
    y = mlb.fit_transform(train_labels + test_labels)
    train_y = y[0:len_train]
    test_y = y[len_train + 1:]
    mlb_classes = list(mlb.classes_)

    print("train size", len(train_X))
    print("test size", len(test_X))

    print("start training")
    print("try parallel")
    with parallel_backend('multiprocessing'):
        clf.fit(train_X, train_y)

    # test save and load model
    # save the model to disk
    print("start saving model")
    model_path = SCRATCH + "metrics_model_parallel_RM.sav"
    pickle.dump(clf, open(model_path, 'wb'))

    print("start loading model")
    loaded_clf = pickle.load(open(model_path, 'rb'))

    print("start predicting")
    y_pred = loaded_clf.predict_proba(test_X)
    # Calculate accuracy
    pickle.dump(y_pred, open(SCRATCH + "test_dump_y_pred_parallel_RM", 'wb'))

    y_pred[where(y_pred == 0)] = -1
    result = eval_hard_thr(y_pred=y_pred, y_test=test_y,
                           mlb_classes=mlb_classes, labels=all_labels, thr=0.1)

    pickle.dump(result, open(SCRATCH + "test_dump_output_parallel_RM", 'wb'))
    save_to_file_format(result=result, file_path=SCRATCH +
                        "test_output_parallel_RM")


def inference(dataFilePath):
    print("start inference")
    print("start read data")
    train_data_path = dataFilePath[0:13]
    test_data_path = dataFilePath[13:16]
    train_data = read_data(train_data_path)
    test_data = read_data(test_data_path)

    class_hierarchy, _, _, all_labels = build_tree_and_labels_from_data_multiple_label(
        train_data + test_data)
    _, train_samples, train_labels, _ = build_tree_and_labels_from_data_multiple_label(
        train_data)
    _, test_samples, test_labels, _ = build_tree_and_labels_from_data_multiple_label(
        test_data)
    len_train = len(train_data)
    len_test = len(test_data)
    print("finish read data, len_train: {}, len_test: {}".format(len_train, len_test))

    mlb = MultiLabelBinarizer()
    test_X = test_samples
    y = mlb.fit_transform(train_labels + test_labels)
    train_y = y[0:len_train]
    test_y = y[len_train + 1:]
    mlb_classes = list(mlb.classes_)

    model_path = SCRATCH + "metrics_model_2.sav"

    print("start loading model")
    loaded_clf = pickle.load(open(model_path, 'rb'))

    print("start predicting, try to use parallel")
    y_pred = []
    with parallel_backend('multiprocessing'):
        y_pred = loaded_clf.predict_proba(test_X)

    print("start saving")
    pickle.dump(y_pred, open(SCRATCH + "test_y_pred_2", 'wb'))

    y_pred[where(y_pred == 0)] = -1
    result = eval_hard_thr(y_pred=y_pred, y_test=test_y,
                           mlb_classes=mlb_classes, labels=all_labels, thr=0.1)

    pickle.dump(result, open(SCRATCH + "test_dump_output_2", 'wb'))
    save_to_file_format(result=result, file_path=SCRATCH + "test_output_2")


def save_mlb_class(dataFilePath):
    print("start inference")
    print("start read data")
    train_data_path = dataFilePath[0:13]
    test_data_path = dataFilePath[13:16]
    train_data = read_data(train_data_path)
    test_data = read_data(test_data_path)

    class_hierarchy, _, _, all_labels = build_tree_and_labels_from_data_multiple_label(
        train_data + test_data)
    _, train_samples, train_labels, _ = build_tree_and_labels_from_data_multiple_label(
        train_data)
    _, test_samples, test_labels, _ = build_tree_and_labels_from_data_multiple_label(
        test_data)
    len_train = len(train_data)
    len_test = len(test_data)
    print("finish read data, len_train: {}, len_test: {}".format(len_train, len_test))

    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(train_labels + test_labels)
    mlb_classes = list(mlb.classes_)

    pickle.dump(mlb_classes, open(SCRATCH + "mlb_classes", 'wb'))


if __name__ == "__main__":
    tree_file_path = "/pylon5/sez3a3p/yyn1228/Dorothy-Ymir/model/NeuralClassifier/NeuralNLP-NeuralClassifier-master/data/cpc_label_tree.pkl"
    #  dataFilePaths = ["/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_0.p"]
    dataFilePaths = ["/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_0.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_1.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_2.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_3.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_5.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_6.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_4.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_7.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_8.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_9.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_10.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_11.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_12.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_13.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_14.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_15.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_16.p",
                     "/pylon5/sez3a3p/yyn1228/data/patent_2M_reparse_17.p",
                     ]

    #  main(dataFilePaths)
    #  go(dataFilePaths)  # gogo futou
    #  load_full_tree(tree_file_path=tree_file_path)
    #  run_metrics(dataFilePath=dataFilePaths)
    #  inference(dataFilePath=dataFilePaths)
    save_mlb_class(dataFilePaths)
