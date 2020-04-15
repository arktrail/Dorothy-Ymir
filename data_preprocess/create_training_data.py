import json
import os
import sys

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))


level_name_to_number_dict = {'section':      1,
                             'class':        2,
                             'subclass':     3,
                             'main_group':   4,
                             'subgroup':     5}


def extract_labels(subgroup_labels, level_number):
    labels = set()
    for subgroup_label in subgroup_labels:
        subgroup_label_splits = subgroup_label.split("--")
        labels.add("--".join(subgroup_label_splits[:level_number]))
    return list(labels)


def create_training_data(input_path, output_path, text_field, level_name, remove_stop_words=True):
    with open(input_path, 'r') as input_file:
        with open(output_path, 'w') as output_file:
            for line in input_file:
                new_data = dict()
                data = json.loads(line)
                if remove_stop_words:
                    new_data['doc_token'] = [
                        token for token in data[text_field] if token not in stop_words]
                else:
                    new_data['doc_token'] = data[text_field]
                new_data['doc_label'] = extract_labels(
                    data['all_labels'], level_name_to_number_dict[level_name])
                new_data['doc_keyword'] = []
                new_data['doc_topic'] = []
                output_file.write(json.dumps(new_data))
                output_file.write('\n')


if __name__ == '__main__':

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    print("input directory: {}".format(input_directory))
    print("output directory: {}".format(output_directory))

    text_field = sys.argv[3]
    level_name = sys.argv[4]

    print("text field: {}".format(text_field))
    print("level: {}".format(level_name))

    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)
            create_training_data(input_path, output_path,
                                 text_field, level_name, remove_stop_words)

