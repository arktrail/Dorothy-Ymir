import pickle
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
from sklearn.decomposition import TruncatedSVD
from sklearn_hierarchical_classification.classifier import HierarchicalClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from numpy import where
from sklearn.metrics import accuracy_score

from model_data_preprocess import build_tree_and_labels_from_data_multiple_label
from model_data_preprocess import SUB_CLASS

from model_evaluation import eval_top1_exist

RANDOM_STATE = 42


def read_data(path):
    data = []
    if isinstance(path, list):
        print("read data from list {}".format(len(path)))
        for p in path:
            data += pickle.load(open(p, "rb"))
        return data
    return pickle.load(open(path, "rb"))

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
    binary_clf = OneVsRestClassifier(LinearSVC())
    base_estimator = make_pipeline(vectorizer, binary_clf)

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

    print("start predicting")
    y_pred = clf.predict_proba(X_test)
    # print("y_pred", y_pred[0])
    # print("y_test", y_test[0])

    # Calculate accuracy

    y_pred[where(y_pred == 0)] = -1
    top1_acc = eval_top1_exist(y_pred, y_test, mlb_classes, all_labels[SUB_CLASS])
    print("top1 accuracy", top1_acc)

    # accuracy = accuracy_score(y_test, y_pred > -0.2)
    # print(accuracy)

def go():
    # read data
    print("start read data")
    path = "/home/ubuntu/capstone/data/patent_200k_reparse_1.p"
    data = read_data(path)[:10]
    class_hierarchy, samples, labels, all_labels = build_tree_and_labels_from_data_multiple_label(
        data)
    print("finish read data")
    print("subclass_labels", all_labels[SUB_CLASS])


if __name__ == "__main__":
    #  dataFilePath = "/home/ubuntu/capstone/data/patent_2M_reparse_0.p"
    dataFilePaths = [ "/home/ubuntu/capstone/data/patent_2M_reparse_0.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_1.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_2.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_3.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_4.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_5.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_6.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_7.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_8.p",
            "/home/ubuntu/capstone/data/patent_2M_reparse_9.p",
            ]
   
    main(dataFilePaths)
    # go() # gogo futou
