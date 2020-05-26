import pickle
import sys
from preprocess import *
from pipline_filters.bs_filters import *
from pipline_filters.string_filters import *

from datafile_loader import *

import gzip
import lmdb
from os import listdir
from os.path import isfile, join
import json
import multiprocessing as mp
from itertools import repeat

JSON_ROOT_PATH = "/pylon5/sez3a3p/javide/uspto/grants"
JSON_TAG = "JSON:"
TYPE_UTILITY = 'UTILITY'
PATENT_TYPE = 'patentType'
DOCUMENT_ID = "documentId"
TITLE = "title"
ABSTRACT = "abstract"
CLAIMS = "claims"
DESCRIPTION = "description"
SINGLE_FILE_CNT = 50000
SAVE_FILE_PATH_MUL = "/pylon5/sez3a3p/yyn1228/data/json_reparse_mul/"
SAVE_FILE_PATH_SIN = "/pylon5/sez3a3p/yyn1228/data/json_reparse/"
N_WORKER = 8

PREFIX_DICT = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7
}

LMDB_ENTRIES = "entries"


def _build_instance_json_obj(patent, cpc_codes):
    '''
    build the new patent_obj from json files
    '''
    patent_obj = {
        DOCUMENT_ID: patent[DOCUMENT_ID],
        'title': get_text(soupify(get_title(patent))),
        'abstraction':
            replace_newlines_with_spaces(get_text(
                strip_pre_freetext_table(
                    strip_headers(
                        strip_all_tables(
                            strip_figrefs(
                                strip_math(
                                    soupify(get_abstract(patent))
                                )
                            )
                        )
                    )
                )
            )),
        'claims':
            replace_newlines_with_spaces(get_text(
                strip_pre_freetext_table(
                    strip_headers(
                        strip_all_tables(
                            strip_figrefs(
                                strip_math(
                                    soupify(
                                        get_expanded_and_flattened_claims(patent))
                                )
                            )
                        )
                    )
                )
            )),
        'description':
            replace_newlines_with_spaces(get_text(
                strip_pre_freetext_table(
                    strip_headers(
                        strip_all_tables(
                            strip_figrefs(
                                strip_math(
                                    soupify(get_description(patent))
                                )
                            )
                        )
                    )
                )
            )),
        'cpc_codes': cpc_codes
    }

    if PATENT_TYPE in patent:
        if TYPE_UTILITY in patent[PATENT_TYPE]:
            # could find brief_summary
            patent_obj['brief_summary'] = replace_newlines_with_spaces(get_text(strip_pre_freetext_table(
                strip_headers(strip_all_tables(strip_figrefs(strip_math(soupify(get_brief_summary(patent)))))))))

    return patent_obj


def _retrieve_json_file(json_path, groupby_dict):
    '''
    read file from json_path, parse json, and yield a iterator of built document object
    '''
    json_file_path = JSON_ROOT_PATH + "/" + json_path
    try:
        with gzip.GzipFile(json_file_path, "r") as jf:
            json_bytes = jf.read().decode("utf-8")
            json_bytes_split = json_bytes.split(JSON_TAG)
            for json_binary_object in json_bytes_split:
                if len(json_binary_object) <= 1:
                    continue
                try:
                    patent = json.loads(json_binary_object)
                    if patent[DOCUMENT_ID] not in groupby_dict:
                        #  print("{} is not in groupby dict".format(patent[DOCUMENT_ID]))
                        continue
                    else:
                        yield _build_instance_json_obj(patent, groupby_dict[patent[DOCUMENT_ID]])
                except json.decoder.JSONDecodeError:
                    print("json decoder error for {}".format(json_path))
    except OSError:
        print("can not open {}".format(json_path))


def _worker(json_paths, save_file_prefix):
    '''
    worker for multiprocessing, 
    '''

    groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_strip_all"
    groupby_dict = pickle.load(open(groupby_dict_path, "rb"))
    print("load groupby_dict")
    print("the length of groupby_dict is {}".format(len(group_by_dict)))
    j_cnt = 0
    f_cnt = 0

    result = []

    for json_path in json_paths:
        for res in _retrieve_json_file(json_path, groupby_dict):
            result.append(res)
            j_cnt += 1
            if j_cnt == SINGLE_FILE_CNT:
                f_cnt += 1
                save_file_path = "{}{}_{}".format(
                    SAVE_FILE_PATH_MUL, save_file_prefix, f_cnt)
                print("{} saved".format(save_file_path))
                pickle.dump(result, open(save_file_path, "wb"))
                result = []
                j_cnt = 0

    f_cnt += 1
    save_file_path = "{}{}_{}".format(
        SAVE_FILE_PATH_MUL, save_file_prefix, f_cnt)
    pickle.dump(result, open(save_file_path, "wb"))

    print("process {} complete".format(save_file_prefix))


def _get_document_id(s):
    '''
    get document id from MCF
    :param s: MCF
    :return:
    '''
    return 'US%s%s' % (s[10:18].lstrip(), s[0:2].lstrip())


def _preprocess_dict():
    '''
    create a new groupby_dict, and use document id as key, and remote whitespaces
    '''
    groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_all"
    group_by_dict = pickle.load(open(groupby_dict_path, "rb"))
    print("load groupby_dict")
    idx = 0
    for k, v in group_by_dict.items():
        print("idx: {} key is {}*".format(idx, k))
        print("idx: {} value is {}".format(idx, v))
        idx += 1
        if idx == 5:
            break


def _reparse_mul():
    #  groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_strip_all"
    #  group_by_dict = pickle.load(open(groupby_dict_path, "rb"))
    #  print("load groupby_dict")
    #  print("the length of groupby_dict is {}".format(len(group_by_dict)))

    document_files = [f for f in listdir(
        JSON_ROOT_PATH) if isfile(join(JSON_ROOT_PATH, f))]

    print("document numbers: {}".format(len(document_files)))

    save_file_prefixes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    print(save_file_prefixes)

    json_file_paths_splits = [
        document_files[i:i + int(len(document_files) / N_WORKER)] for i in range(N_WORKER)]

    print("total length of document_files is {}".format(len(document_files)))
    print("print length for each split")
    for i in json_file_paths_splits:
        print(len(i))

    print("start multi-processing")
    with mp.Pool(processes=N_WORKER) as pool:
        pool.starmap(
            _worker, zip(save_file_prefixes, json_file_paths_splits))

    #  print("test parse the 1 file")
    #  idx = 0
    #  #  for patent_obj in _retrieve_json_file(document_files[1], group_by_dict):
    #  for patent_obj in _retrieve_json_file('ipg070515.json.gz', group_by_dict):
        #  idx += 1
        #  print("FOUND ONE")
        #  print(patent_obj[DOCUMENT_ID])
        #  if idx == 2:
        #  break


def _reparse_single():
    groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_strip_all"
    group_by_dict = pickle.load(open(groupby_dict_path, "rb"))
    print("load groupby_dict")
    print("the length of groupby_dict is {}".format(len(group_by_dict)))

    document_files = [f for f in listdir(
        JSON_ROOT_PATH) if isfile(join(JSON_ROOT_PATH, f))]

    print("document numbers: {}".format(len(document_files)))

    #  print("test parse the 1 file")
    print("parse all the file")

    f_cnt = 0
    d_cnt = 0
    cnt = 0
    rst = []
    for document_file in document_files:
        cnt += 1
        for patent_obj in _retrieve_json_file(document_file, group_by_dict):
            d_cnt += 1
            rst.append(patent_obj)
            #  print("FOUND ONE")
            #  print(patent_obj[DOCUMENT_ID])

            if d_cnt == SINGLE_FILE_CNT:
                save_path = "{}_{}_{}".format(SAVE_FILE_PATH_SIN, f_cnt, d_cnt)

                pickle.dump(rst, open(save_path, "wb"))
                d_cnt = 0
                f_cnt += 1
                rst = []

                print("current {} document_file is, ".format(cnt))
                print(document_file)

    # save the last chunk
    f_cnt += 1
    save_path = "{}_{}_{}".format(SAVE_FILE_PATH_SIN, f_cnt, d_cnt)
    pickle.dump(rst, open(save_path, "wb"))


def _reparse_single_split(prefix):
    print("prefix is {}".format(prefix))

    groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_strip_all"
    group_by_dict = pickle.load(open(groupby_dict_path, "rb"))
    print("load groupby_dict")
    print("the length of groupby_dict is {}".format(len(group_by_dict)))

    save_file_prefixes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    print(save_file_prefixes)

    save_path = "{}_file_path_split".format(SAVE_FILE_PATH_SIN)
    json_file_paths_splits = pickle.load(open(save_path, "rb"))
    print("load all the paths")

    document_files = json_file_paths_splits[PREFIX_DICT[prefix]]

    print("parse the file for {}".format(PREFIX_DICT[prefix]))

    f_cnt = 0
    d_cnt = 0
    cnt = 0
    rst = []
    for document_file in document_files:
        cnt += 1
        for patent_obj in _retrieve_json_file(document_file, group_by_dict):
            d_cnt += 1
            rst.append(patent_obj)
            #  print("FOUND ONE")
            #  print(patent_obj[DOCUMENT_ID])

            if d_cnt == SINGLE_FILE_CNT:
                save_path = "{}_{}_{}_{}".format(
                    SAVE_FILE_PATH_SIN, prefix, f_cnt, d_cnt)

                pickle.dump(rst, open(save_path, "wb"))
                d_cnt = 0
                f_cnt += 1
                rst = []

                print("current {} document_file is, ".format(cnt))
                print(document_file)

    # save the last chunk
    f_cnt += 1
    save_path = "{}_{}_{}_{}".format(SAVE_FILE_PATH_SIN, prefix, f_cnt, d_cnt)
    pickle.dump(rst, open(save_path, "wb"))


def _reparse_single_split_ckp_recover(prefix, ckpnum):
    print("prefix is {},  ckenum is {}".format(prefix, ckpnum))

    groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_strip_all"
    group_by_dict = pickle.load(open(groupby_dict_path, "rb"))
    print("load groupby_dict")
    print("the length of groupby_dict is {}".format(len(group_by_dict)))

    save_file_prefixes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    print(save_file_prefixes)

    save_path = "{}_file_path_split".format(SAVE_FILE_PATH_SIN)
    json_file_paths_splits = pickle.load(open(save_path, "rb"))
    print("load all the paths")

    document_files = json_file_paths_splits[PREFIX_DICT[prefix]]

    print("parse the file for {}".format(PREFIX_DICT[prefix]))

    f_cnt = 0
    d_cnt = 0
    cnt = ckpnum
    rst = []
    for document_file in document_files[ckpnum - 1:]:
        cnt += 1
        for patent_obj in _retrieve_json_file(document_file, group_by_dict):
            d_cnt += 1
            rst.append(patent_obj)
            #  print("FOUND ONE")
            #  print(patent_obj[DOCUMENT_ID])

            if d_cnt == SINGLE_FILE_CNT:
                save_path = "{}_{}_{}_{}_ckp_{}".format(
                    SAVE_FILE_PATH_SIN, prefix, f_cnt, d_cnt, ckpnum)

                pickle.dump(rst, open(save_path, "wb"))
                d_cnt = 0
                f_cnt += 1
                rst = []

                print("current {} document_file is, ".format(cnt))
                print(document_file)

    # save the last chunk
    f_cnt += 1
    save_path = "{}_{}_{}_{}_ckp_{}".format(
        SAVE_FILE_PATH_SIN, prefix, f_cnt, d_cnt, ckpnum)
    pickle.dump(rst, open(save_path, "wb"))


def _save_split_doc():
    document_files = [f for f in listdir(
        JSON_ROOT_PATH) if isfile(join(JSON_ROOT_PATH, f))]

    print("document numbers: {}".format(len(document_files)))
    save_file_prefixes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    print(save_file_prefixes)

    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    json_file_paths_splits = [chunk for chunk in chunks(
        document_files, int(len(document_files) / N_WORKER))]

    print("print the length for each split")
    for i in json_file_paths_splits:
        print(len(i))

    save_path = "{}_file_path_split".format(SAVE_FILE_PATH_SIN)
    pickle.dump(json_file_paths_splits, open(save_path, "wb"))


def _test_reparse():
    groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_strip_all"
    group_by_dict = pickle.load(open(groupby_dict_path, "rb"))
    print("load groupby_dict")
    print("the length of groupby_dict is {}".format(len(group_by_dict)))

    document_files = [f for f in listdir(
        JSON_ROOT_PATH) if isfile(join(JSON_ROOT_PATH, f))]

    print("document numbers: {}".format(len(document_files)))

    print("test parse the 1 file")
    idx = 0
    #  for patent_obj in _retrieve_json_file(document_files[1], group_by_dict):
    for patent_obj in _retrieve_json_file('ipg070515.json.gz', group_by_dict):
        idx += 1
        print("FOUND ONE")
        print(patent_obj[DOCUMENT_ID])
        if idx == 2:
            break


def _possible_strip_groupby_dict():
    groupby_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_all"
    groupby_strip_dict_path = "/pylon5/sez3a3p/yyn1228/data/groupby_dict_strip_all"
    group_by_dict = pickle.load(open(groupby_dict_path, "rb"))
    print("load groupby_dict")
    groupby_strip_dict = dict()

    for k, v in group_by_dict.items():
        groupby_strip_dict[k.strip()] = v

    print("save to file")
    pickle.dump(groupby_strip_dict, open(groupby_strip_dict_path, "wb"))


if __name__ == '__main__':
    #  index_file_name = "/Users/yining/Work/Capstone/TestAPI/shuffle_200000_with_cpc_all"
    #  download_and_save_all(index_file_name)
    #  _test()
    #  _preprocess_dict()
    #  _test_reparse()
    #  _reparse_mul()
    #  _reparse_single()
    #  _possible_strip_groupby_dict()
    #  _save_split_doc()

    if len(sys.argv) == 2:
        prefix = sys.argv[1]

        _reparse_single_split(prefix)
    elif len(sys.argv) == 3:
        prefix = sys.argv[1]
        ckpnum = int(sys.argv[2])
        _reparse_single_split_ckp_recover(prefix, ckpnum)
    else:
        print("wrong input args number {}".format(len(sys.argv)))
