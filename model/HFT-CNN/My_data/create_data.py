import pickle
from random import shuffle

CPC_CODES = "cpc_codes"
TITLE = "title"
ABSTRACTION = "abstraction"
CLAIMS = "claims"
BRIEF_SUMMARY = "brief_summary"
DESCRIPTION = "description"

SECTION = 3
CLASS = 4
SUBCLASS = 5
MAIN_GROUP = 6
SUB_GROUP = 7


def _build_cpc_field_slice_dicts():
    g = [
        ('kind', (0, 2)),
        ('application_number', (2, 10)),
        ('document_number', (10, 18)),
        ('cpc_section', (18, 19)),
        ('cpc_class', (19, 21)),
        ('cpc_subclass', (21, 22)),
        ('cpc_main_group', (22, 26)),
        ('cpc_subgroup', (27, 33)),
        ('cpc_version_date', (33, 41)),
        ('cpc_symbol_position', (41, 42)),
        ('cpc_value_code', (42, 43)),
        ('cpc_set_group', (43, 46)),
        ('cpc_set_rank', (46, 48))]
    a = g[:2] + [(k, (v[0], v[1] + 3)) for k, v in g[2:3]] + \
        [(k, (v[0] + 3, v[1] + 3)) for k, v in g[3:]]
    return {'grant': g, 'application': a}

def build_tree_and_labels_from_data(data):
    '''
    build tree for usage of sklearn hierarchical classification
    :param data:  a list of dict, read from pre-processed dataset
    :return: tree
        r"""Test that a nontrivial hierarchy leaf classification behaves as expected.
    1
    2     We build the following class hierarchy along with data from the handwritten digits dataset:
    3
    4             <ROOT>
    5            /      \
    6           A        B
    7          / \       |  \
    8         1   7      C   9
    9                  /   \
    10                 3     8
    11
    12     """
    '''
    cpc_field_slice_dict = _build_cpc_field_slice_dicts()

    class_hierarchy = {"ROOT": set()}
    data_labels = []
    data_samples = []
    hierachy_text_list = []

    for cur_d in data:
        # concat the texts into one single one
        # data_samples.append(".".join([cur_d[TITLE], cur_d[ABSTRACTION]]))
        data_samples.append(cur_d[TITLE])
        
        # extract labels from cpc codes
        cpc_classifications_labels_set = set()
        for cpc_code in cur_d[CPC_CODES]:
            cpc_classification_labels = [
                cpc_code[cpc_field_slice_dict['grant'][SECTION][1][0] : cpc_field_slice_dict['grant'][SECTION][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][CLASS][1][0] : cpc_field_slice_dict['grant'][CLASS][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][SUBCLASS][1][0] : cpc_field_slice_dict['grant'][SUBCLASS][1][1]],
                # cpc_code[cpc_field_slice_dict['grant'][6][1][0] : cpc_field_slice_dict['grant'][6][1][1]].strip(),
                # cpc_code[cpc_field_slice_dict['grant'][7][1][0] : cpc_field_slice_dict['grant'][7][1][1]].strip(),
            ]

            cur_hierachy_list = []
            for i in range(len(cpc_classification_labels)):
                if i == 0:
                    cur_hierachy_list.append(cpc_classification_labels[i])
                else:
                    cur_level_label = cur_hierachy_list[i-1].split("<")[-1] + "@" + cpc_classification_labels[i]
                    cur_hierachy_list.append(cur_hierachy_list[i-1] + "<" + cur_level_label)
            
            cur_label_list = [label.split("<")[-1] for label in cur_hierachy_list]
            cpc_classifications_labels_set.add(','.join(cur_label_list))
            hierachy_text_list.extend(cur_hierachy_list)

        cpc_classifications_labels = []
        for label_string in cpc_classifications_labels_set:
            cpc_classifications_labels.extend(label_string.split(','))
        data_labels.append(cpc_classifications_labels)

    return hierachy_text_list, data_samples, data_labels

def read_data(path):
    return pickle.load(open(path, "rb"))

def shuffle_list(*ls):
    l =list(zip(*ls))

    shuffle(l)
    return zip(*l)

def write_data_file(file_path, data, labels):
    f = open(file_path, "w")
    for d, label_set in zip(data, labels):
        label = ','.join(label_set)
        f.write(label + "\t" + d + "\n")
    f.close()

def main():
    data = read_data("./patent_200k_reparse_1.p")
    tree_path = "../Tree/CPC.tree"
    hierachy_text_list, data_samples, data_labels = build_tree_and_labels_from_data(data)
    no_dup_hierachy_text_list = list(set(hierachy_text_list))
    no_dup_hierachy_text_list.sort(key=hierachy_text_list.index)

    f = open(tree_path, "w")
    for hierachy_text in no_dup_hierachy_text_list:
        f.write(hierachy_text)
        f.write("\n")
    f.close()

    test_size = int(len(data_labels) * 0.2)
    valid_size = int(len(data_labels) * 0.1)

    shuffled_data, shuffled_labels = shuffle_list(data_samples, data_labels)
    test_data = shuffled_data[:test_size]
    test_labels = shuffled_labels[:test_size]

    valid_data = shuffled_data[test_size: test_size+valid_size]
    valid_labels = shuffled_labels[test_size: test_size+valid_size]

    train_data = shuffled_data[test_size+valid_size:]
    train_labels = shuffled_labels[test_size+valid_size:]

    test_data_file_path = "./test_data.txt" 
    valid_data_file_path = "./valid_data.txt"
    train_data_file_path = "./train_data.txt"

    #average sentence length for test, valid, train is 120, 119, 121
    write_data_file(test_data_file_path, test_data, test_labels)
    write_data_file(valid_data_file_path, valid_data, valid_labels)
    write_data_file(train_data_file_path, train_data, train_labels)

if __name__ == "__main__":
    main()