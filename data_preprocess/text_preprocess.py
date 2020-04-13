import nltk
import pickle
import pandas as pd
from nltk.tokenize import word_tokenize
import string
import json
import os
import sys
from pandarallel import pandarallel

pandarallel.initialize()

cpc_field_slice_dict = {'kind':                (0 ,2 ),   
                        'application_number':  (2 ,10),  
                        'document_number':     (10,18),
                        'cpc_section':         (18,19), 
                        'cpc_class':           (18,21), # include higher levels
                        'cpc_subclass':        (18,22), # include higher levels
                        'cpc_main_group':      (18,26), # include higher levels
                        'cpc_subgroup':        (18,33), # include higher levels
                        'cpc_version_date':    (33,41), 
                        'cpc_symbol_position': (41,42), 
                        'cpc_value_code':      (42,43), 
                        'cpc_set_group':       (43,46), 
                        'cpc_set_rank':        (46,48)}


def extract_labels(cpc_codes, label_columns):
    labels = set()
    for cpc_code in cpc_codes:
        level_label = []
        for label_column in label_columns:
            index = cpc_field_slice_dict[label_column]
            level_label.append(cpc_code[index[0]:index[1]])
        labels.add("--".join(level_label))
    return list(labels)


def tokenize(text):
    tokens = word_tokenize(text)
    return [token.lower() for token in tokens if token not in string.punctuation]


def process_single_API_data(input_path, output_path):

    print("starting to process {}".format(input_path))
    with open(input_path, 'rb') as file:
        df = pd.DataFrame(pickle.load(file))
        
    df_text = pd.DataFrame(df['cpc_codes'].apply(extract_labels, args=(LABEL_COLUMNS,)))
    df_text.rename(columns={'cpc_codes': 'all_labels'}, inplace=True)

    print("label extraction done")
    
    for text_column in TEXT_COLUMNS:
        print("tokenizing {}".format(text_column))
        df_text[text_column] = df[text_column].parallel_apply(tokenize)
    df_text.to_json(output_path, orient='records', lines=True)


def process_API_data_folder(input_directory, output_directory):
    counter = 0
    for filename in os.listdir(input_directory):
        
        if filename.endswith("_split"):
            continue 
            
        if filename.startswith("_"):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, OUTPUT_BASE_NAME.format(counter))
            process_single_API_data(input_path, output_path)
            counter += 1
            print("finished processing file {}; count = {}".format(filename, counter))


def combine_json(json_list, output_file):
    with open(output_file, "w") as outfile:
        for input_path in json_list:
            with open(input_path) as infile:
                print("opened {}".format(input_path))
                outfile.write(infile.read())
                outfile.write('\n')
            os.remove(input_path)

            
def get_json_list(output_directory, start_index, end_index, base_name):
    return [os.path.join(output_directory, base_name.format(i)) for i in range(start_index, end_index+1)]


if __name__ == '__main__':

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    TEXT_COLUMNS = ['title', 'abstraction', 'claims', 'brief_summary', 'description']
    LABEL_COLUMNS = ['cpc_section', 'cpc_class', 'cpc_subclass', 'cpc_main_group', 'cpc_subgroup']
    OUTPUT_BASE_NAME = "post_json_{}.p"


    train_start_index = 1
    train_end_index = 70
    valid_start_index = 71
    valid_end_index = 80
    test_start_index = 81
    test_end_index = 91

    process_API_data_folder(input_directory, output_directory)

    train_json_list = get_json_list(output_directory, train_start_index, train_end_index, OUTPUT_BASE_NAME)
    valid_json_list = get_json_list(output_directory, valid_start_index, valid_end_index, OUTPUT_BASE_NAME)
    test_json_list = get_json_list(output_directory, test_start_index, test_end_index, OUTPUT_BASE_NAME)

    combine_json(train_json_list, os.path.join(output_directory, "train.json"))
    combine_json(valid_json_list, os.path.join(output_directory, "valid.json"))
    combine_json(test_json_list, os.path.join(output_directory, "test.json"))
