from sklearn.metrics import accuracy_score
import numpy as np

__all__ = [
    'eval_top1_exist'
]


def eval_top1_exist(y_pred, y_test, mlb_classes, labels):
    # select leaf nodes, here we select sub_class label
    leaf_indexes = []
    leaf_indexes = [i for i in range(len(mlb_classes)) if mlb_classes[i] in labels]
    print(leaf_indexes)
    y_pred_leaves = y_pred[:, leaf_indexes]
    y_test_leaves = y_test[:, leaf_indexes]

    y_pred_one_hot = np.zeros_like(y_pred_leaves)
    y_pred_one_hot[np.arange(len(y_pred_leaves)), y_pred_leaves.argmax(1)] = 1
    #  print("y_pred_one_hot", y_pred_one_hot)
    #  print("y_test_leaves", y_test_leaves)
    correct = np.sum(np.minimum(y_pred_one_hot, y_test_leaves))
    total = y_test.shape[0]
    print("correct", correct, "total", total)

    top1_acc = correct / total
    return top1_acc



