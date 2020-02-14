from sklearn_hierarchical_classification.constants import ROOT

CPC_CODES = "cpc_codes"
TITLE = "title"
ABSTRACTION = "abstraction"
CLAIMS = "claims"
BRIEF_SUMMARY = "brief_summary"
DESCRIPTION = "description"
SECTION = "section"
CLASS = "class"
SUB_CLASS = "sub_class"
GROUP = "group"
SUB_GROUP = "sub_group"


__all__ = [
    'build_tree_and_labels_from_data',
    'build_tree_and_labels_from_data_multiple_label'
]


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


def build_tree_from_all_cpc():
    '''
    placeholder for build hierarchy tree from all cpc codes, for future used
    :return:
    '''
    pass


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
    13     class_hierarchy = {
    14         ROOT: ["A", "B"],
    15         "A": ["1", "7"],
    16         "B": ["C", "9"],
    17         "C": ["3", "8"],
    '''
    cpc_field_slice_dict = _build_cpc_field_slice_dicts()

    class_hierarchy = {ROOT: set()}
    data_labels = []
    data_samples = []
    subclass_nodes = set()

    for d in data:
        # concat the texts into one single one
        data_samples.append(".".join([d[TITLE], d[ABSTRACTION]]))

        # extract labels from cpc codes
        cpc_classifications_labels = set()
        for cpc_code in d[CPC_CODES]:
            cpc_classification_labels = [
                cpc_code[cpc_field_slice_dict['grant'][3][1][0]
                    : cpc_field_slice_dict['grant'][3][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][4][1][0]
                    : cpc_field_slice_dict['grant'][4][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][5][1][0]
                    : cpc_field_slice_dict['grant'][5][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][6][1][0]
                    : cpc_field_slice_dict['grant'][6][1][1]].strip(),
                cpc_code[cpc_field_slice_dict['grant'][7][1][0]
                    : cpc_field_slice_dict['grant'][7][1][1]].strip(),
            ]

            # build tree
            class_hierarchy[ROOT].add(cpc_classification_labels[0])

            for idx in range(len(cpc_classification_labels) - 2):
                current_level = ".".join(cpc_classification_labels[0:idx])
                next_level = ".".join(cpc_classification_labels[0:idx + 1])
                if current_level not in class_hierarchy.keys():
                    class_hierarchy[current_level] = set()
                class_hierarchy[current_level].add(
                    next_level)

            cpc_classifications_labels.add(
                ".".join(cpc_classification_labels[0:3]))

        data_labels.append(list(cpc_classifications_labels))

    # change set to list
    if '' in class_hierarchy.keys():
        del class_hierarchy['']

    for k, v in class_hierarchy.items():
        class_hierarchy[k] = list(v)

    return class_hierarchy, data_samples, data_labels, subclass_nodes


def build_tree_and_labels_from_data_multiple_label(data):
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
    13     class_hierarchy = {
    14         ROOT: ["A", "B"],
    15         "A": ["1", "7"],
    16         "B": ["C", "9"],
    17         "C": ["3", "8"],
    '''
    cpc_field_slice_dict = _build_cpc_field_slice_dicts()

    class_hierarchy = {ROOT: set()}
    data_labels = []
    data_samples = []
    all_labels = {SECTION: set(), CLASS: set(), SUB_CLASS: set(), GROUP: set(), SUB_GROUP: set()}

    for d in data:
        # concat the texts into one single one
        data_samples.append(".".join([d[TITLE], d[ABSTRACTION]]))

        # extract labels from cpc codes
        cpc_classifications_labels = set()
        for cpc_code in d[CPC_CODES]:
            cpc_classification_labels = [
                cpc_code[cpc_field_slice_dict['grant'][3][1][0]
                    : cpc_field_slice_dict['grant'][3][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][4][1][0]
                    : cpc_field_slice_dict['grant'][4][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][5][1][0]
                    : cpc_field_slice_dict['grant'][5][1][1]],
                cpc_code[cpc_field_slice_dict['grant'][6][1][0]
                    : cpc_field_slice_dict['grant'][6][1][1]].strip(),
                cpc_code[cpc_field_slice_dict['grant'][7][1][0]
                    : cpc_field_slice_dict['grant'][7][1][1]].strip(),
            ]

            # build tree
            class_hierarchy[ROOT].add(cpc_classification_labels[0])

            for idx in range(len(cpc_classification_labels) - 2):
                current_level = ".".join(cpc_classification_labels[0:idx])
                next_level = ".".join(cpc_classification_labels[0:idx + 1])
                if current_level not in class_hierarchy.keys():
                    class_hierarchy[current_level] = set()
                class_hierarchy[current_level].add(
                    next_level)

                cpc_classifications_labels.add(
                    next_level)

            # get all labels:
            all_labels[SECTION].add(cpc_classification_labels[0])
            all_labels[CLASS].add(".".join(cpc_classification_labels[0:2]))
            all_labels[SUB_CLASS].add(".".join(cpc_classification_labels[0:3]))
            all_labels[GROUP].add(".".join(cpc_classification_labels[0:4]))
            all_labels[SUB_GROUP].add(".".join(cpc_classification_labels[0:5]))

        data_labels.append(list(cpc_classifications_labels))

    # change set to list
    if '' in class_hierarchy.keys():
        del class_hierarchy['']

    for k, v in class_hierarchy.items():
        class_hierarchy[k] = list(v)

    return class_hierarchy, data_samples, data_labels, all_labels
