'''
load data from US_Grang_CPC_MCF files, and compute the corresponding numbers for each level
'''

import pandas as pd
import os

def process_cpc_classification_folder(directory, document_type):
    master_df = []
    counter = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        d = process_cpc_classification_file(file_path, document_type)
        master_df.append(d)
        counter += 1
        print(counter)
    return pd.concat(master_df, ignore_index=True)


def build_cpc_field_slice_dicts():
    g = [
        ('kind',                (0 ,2 )),
        ('application_number',  (2 ,10)),
        ('document_number',     (10,18)),
        ('cpc_section',         (18,19)),
        ('cpc_class',           (19,21)),
        ('cpc_subclass',        (21,22)),
        ('cpc_main_group',      (22,26)),
        ('cpc_subgroup',        (27,33)),
        ('cpc_version_date',    (33,41)),
        ('cpc_symbol_position', (41,42)),
        ('cpc_value_code',      (42,43)),
        ('cpc_set_group',       (43,46)),
        ('cpc_set_rank',        (46,48))]
    a = g[:2] + [(k,(v[0],v[1]+3)) for k,v in g[2:3]] + \
        [(k,(v[0]+3,v[1]+3)) for k,v in g[3:]]
    return {'grant': g, 'application': a}


def process_cpc_classification_file(textfile, document_type):
    cpc_field_slice_dict = build_cpc_field_slice_dicts()

    d = pd.read_fwf(
        textfile,
        colspecs=[i[1] for i in cpc_field_slice_dict[document_type]],
        names=[i[0] for i in cpc_field_slice_dict[document_type]],
        dtype=str)
    d['cpc_version_date'] = pd.to_datetime(
        d['cpc_version_date'], yearfirst=True)
    return d


def process_cpc_classification_folder(directory, document_type):
    master_df = []
    counter = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        d = process_cpc_classification_file(file_path, document_type)
        master_df.append(d)
        counter += 1
        print("file: %s, counter: %d".format(file_path, counter))
    return pd.concat(master_df, ignore_index=True)


def read_from_file(file_name):
    return pd.read_pickle(file_name)

# if __name__ == '__main__':
    # N = 10000   # load 10000 data sample as training + test sets
    # df_grant = process_cpc_classification_folder("/Users/yining/Downloads/US_Grant_CPC_MCF_Text_2020-01-01", "grant")
    # doc_date_dedup = df_grant[["document_number", "cpc_version_date"]].drop_duplicates()



