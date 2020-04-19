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

    # print(section_label, class_label, subclass_label)

    return section_label, class_label, subclass_label


def change_format(prediction):
    '''
    prediction: tuple(tuple(), np.array())
    return: three dict(label_name: str, prob: float)
    '''
    labels, probs = prediction[0], prediction[1]
    # normalized_probs = (probs - np.min(probs)) / \
    #     (np.max(probs) - np.min(probs))
    normalized_probs = probs
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

    # normalize section and class level
    section_prob_max = section_prob_dict[max(
        section_prob_dict, key=section_prob_dict.get)]
    section_prob_min = section_prob_dict[min(
        section_prob_dict, key=section_prob_dict.get)]
    class_prob_max = class_prob_dict[max(
        class_prob_dict, key=class_prob_dict.get)]
    class_prob_min = class_prob_dict[min(
        class_prob_dict, key=class_prob_dict.get)]
    section_prob_sum = sum(section_prob_dict.values())
    class_prob_sum = sum(class_prob_dict.values())
    subclass_prob_sum = sum(subclass_prob_dict.values())

    def normalized(v, _max, _min):
        return (v - _min) / (_max - _min + 1)

    def standardized(v, _sum):
        return (v + 0.1) / _sum
    # section_prob_dict = {k: normalized(v, section_prob_max, section_prob_min)
    #                      for k, v in section_prob_dict.items()}
    # class_prob_dict = {k: normalized(
    #     v, class_prob_max, class_prob_min) for k, v in class_prob_dict.items()}
    section_prob_dict = {k: standardized(v, section_prob_sum)
                         for k, v in section_prob_dict.items()}
    class_prob_dict = {k: standardized(
        v, class_prob_sum) for k, v in class_prob_dict.items()}
    subclass_prob_dict = {k: standardized(
        v, subclass_prob_sum) for k, v in subclass_prob_dict.items()}

    # # calculate dependent probability
    # for k, v in subclass_prob_dict.items():
    #     class_label = k[0:4]  # had seperater
    #     subclass_prob_dict[k] /= class_prob_dict[class_label]
    # for k, v in class_prob_dict.items():
    #     section_label = k[0:1]
    #     class_prob_dict[k] /= section_prob_dict[section_label]

    return section_prob_dict, class_prob_dict, subclass_prob_dict
