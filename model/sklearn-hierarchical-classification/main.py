import pickle

from sklearn import svm
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
from sklearn.decomposition import TruncatedSVD
from sklearn_hierarchical_classification.classifier import HierarchicalClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split

from model_data_preprocess import build_tree_and_labels_from_data

RANDOM_STATE = 42


def read_data(path):
    return pickle.load(open(path, "rb"))


def main():
    # read data
    print("start read data")
    path = "/Users/yining/Work/Capstone/TestAPI/patent_200k_reparse_1.p"
    data = read_data(path)
    class_hierarchy, samples, labels = build_tree_and_labels_from_data(data)
    print("finish read data")

    # build model
    print("start build model")
    base_estimator = make_pipeline(
        TruncatedSVD(n_components=24),
        svm.SVC(
            gamma=0.001,
            kernel="rbf",
            probability=True
        )
    )

    bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), token_pattern=r'\b\w+\b', min_df=1)
    mlb = MultiLabelBinarizer()
    clf = HierarchicalClassifier(
        base_estimator=base_estimator,
        class_hierarchy=class_hierarchy,
        mlb=mlb
    )


    X = bigram_vectorizer.fit_transform(samples)
    y = mlb.fit_transform(labels)
    # y = labels
    print("shape of X", X.shape)
    print("shape of y", y.shape)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE
    )

    print("shape of X_train", X_train.shape)
    print("shape of X_test", X_test.shape)
    print("shape of y_train", y_train.shape)
    print("shape of y_test", y_test.shape)
    print("start training")
    clf.fit(X_train, y_train)

    print("start predicting")
    y_pred = clf.predict(X_test)

    print("Classification Report:\n", classification_report(y_test, y_pred))


def test():
    path = "/Users/yining/Work/Capstone/TestAPI/patent_200k_reparse_1.p"
    data = read_data(path)
    class_hierarchy, samples, labels = build_tree_and_labels_from_data(data)

    bigram_vectorizer = CountVectorizer(ngram_range=(1, 2), token_pattern=r'\b\w+\b', min_df=1)

    X = bigram_vectorizer.fit_transform(samples)


if __name__ == "__main__":
    main()
    # test()
