import numpy as np

SEPARATOR_1 = '@'
SEPARATOR_2 = ','
SECTION = 'SECTION'
CLASS = 'CLASS'
SUBCLASS = 'SUBCLASS'

FASTTEXT_LABEL_PREFIX = "__label__"
FASTTEXT_LABEL_SEP = "--"


def get_seperated_labels(label: str):
    subclass_label = label.replace(
        FASTTEXT_LABEL_PREFIX, "").split(FASTTEXT_LABEL_SEP)[2]
    section_label = subclass_label[0:1]
    class_label = SEPARATOR_1.join([section_label, subclass_label[1:3]])
    subclass_label = SEPARATOR_1.join([
        section_label, subclass_label[1:3], subclass_label[3:]])

    print(section_label, class_label, subclass_label)

    return section_label, class_label, subclass_label


def change_format(prediction):
    '''
    prediction: tuple(tuple(), np.array())
    return: three dict(label_name: str, prob: float)
    '''
    labels, probs = prediction[0], prediction[1]
    normalized_probs = (probs - np.min(probs)) / \
        (np.max(probs) - np.min(probs))
    section_prob_dict = {}
    class_prob_dict = {}
    subclass_prob_dict = {}

    for idx,  label in enumerate(labels):
        section_label, class_label, subclass_label = get_seperated_labels(
            label)
        if section_label not in section_prob_dict:
            section_prob_dict[section_label] = 0
        if class_label not in class_prob_dict:
            class_prob_dict[class_label] = 0

        section_prob_dict[section_label] += normalized_probs[idx]
        class_prob_dict[class_label] += normalized_probs[idx]
        subclass_prob_dict[subclass_label] = normalized_probs[idx]

    return section_prob_dict, class_prob_dict, subclass_prob_dict
