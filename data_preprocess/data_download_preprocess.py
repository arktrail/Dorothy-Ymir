import pickle
import slumber
from preprocess import *
from pipline_filters.bs_filters import *
from pipline_filters.string_filters import *

from datafile_loader import *


def _get_objects_documents_by_ids(document_ids):
    '''
    Download documents from API by document_ids
    :param document_id:  ids for documents
    :return:
    '''
    a = slumber.API('http://localhost:8000/api/v0')
    par = {'username': 'capstone2020',
           'api_key': '48f0580836eaf85e7af82c57a0e7391a7e06530f'}
    patent = a.patent.get(document_id__in=document_ids,
                          **par, full_document=True)
    # patent = a.patent.get(document_id='US20140127591A1', **par, full_document=True)
    if len(patent['objects']) == 0:
        return {}
    return [obj['document'] for obj in patent['objects']]


def _get_objects_document(document_id):
    '''
    Download document from API
    :param document_id:  id for document
    :return:
    '''
    a = slumber.API('http://localhost:8000/api/v0')
    par = {'username': 'capstone2020',
           'api_key': '48f0580836eaf85e7af82c57a0e7391a7e06530f'}
    patent = a.patent.get(document_id=document_id, **par, full_document=True)
    # patent = a.patent.get(document_id='US20140127591A1', **par, full_document=True)
    if len(patent['objects']) == 0:
        return {}
    return patent['objects'][0]['document']


def _build_instance(s, cpc_codes, dct):
    '''
    parse patent from what retrieved from api
    :param s: MCF code
    :param cpc_codes: all relative MCF codes that belongs to the same document with different cpc classifications
    :return:
    '''
    #  dct = _get_objects_document(_get_document_id(s))

    if len(dct) == 0:
        return {}

    data = {
        'mcf': s,
        'title': get_text(soupify(get_title(dct))),
        'abstraction':
            replace_newlines_with_spaces(get_text(
                strip_pre_freetext_table(
                    strip_headers(
                        strip_all_tables(
                            strip_figrefs(
                                strip_math(
                                    soupify(get_abstract(dct))
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
                                        get_expanded_and_flattened_claims(dct))
                                )
                            )
                        )
                    )
                )
            )),
        'brief_summary':
            replace_newlines_with_spaces(get_text(
                strip_pre_freetext_table(
                    strip_headers(
                        strip_all_tables(
                            strip_figrefs(
                                strip_math(
                                    soupify(get_brief_summary(dct))
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
                                    soupify(get_description(dct))
                                )
                            )
                        )
                    )
                )
            )),
        'cpc_codes': cpc_codes
    }

    return data


def _build_instances(ids, mcfs, cpc_codes):
    documens_dcts = _get_objects_documents_by_ids(ids)
    return [_build_instance(mcf, cpc_code, dct) for mcf, cpc_code, dct in zip(mcfs, cpc_codes, documens_dcts)]


def _worker(document_mcf, cpc_codes):
    '''
    intend to work for multiprocessing
    :param document_mcf:
    :param cpc_codes:
    :return:
    '''
    dct = _get_objects_document(_get_document_id(document_mcf))
    data = _build_instance(document_mcf, cpc_codes, dct)
    return data


def _worker_mul(document_ids, document_mcfs, cpc_codes):
    '''
    download multiple documents
    '''
    return _build_instances(document_ids, document_mcfs, cpc_codes)


def _get_document_id(s):
    '''
    get document id from MCF
    :param s: MCF
    :return:
    '''
    return 'US%s%s' % (s[10:18].lstrip(), s[0:2].lstrip())


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def download_and_save_all(index_file_name):
    '''
    download all the document in the index file, the index file here is the MCF files, each row is an MCF row
    '''
    chunk_size = 20_000

    print("read shuffled MCF code")
    ds = read_from_file(index_file_name)
    document_mcfs = ds['cpc_all'].to_list()

    print("read groupby dict")
    groupby_dict = pickle.load(open("./groupby_dict_all", "rb"))

    # retrieve the db
    print("start retrieve")

    c = 0
    idx = 0
    for document_mcfs_chunk in _chunks(document_mcfs, chunk_size):
        idx += 1

        rl = []
        for document_mcf in document_mcfs_chunk:
            document_id = _get_document_id(document_mcf)
            cpc_codes = groupby_dict[document_id]
            rl.append(_worker(document_id, cpc_codes))
            c += 1
            if c % 100 == 0:
                print(c)

        # save to file
        save_chunk_file_name = "patent_200k_reparse_{}.p".format(idx)
        pickle.dump(rl, open(save_chunk_file_name, "wb"))


def download_by_number(index_file_name, groupby_dict_path, num):
    '''
    download documents by number
    '''
    default_index_file_name = "/pylon5/sez3a3p/yyn1228/shuffle_5000000_with_cpc_all"
    default_groupby_dict_path = "/pylon5/sez3a3p/yyn1228/groupby_dict_all"
    default_num = 32
    use_index_file_name = ""
    use_groupby_dict_path = ""
    chunk_size = 32

    if len(index_file_name) == 0:
        print("download by number: no index file name given, use index_file_name {}".format(
            default_index_file_name))
        use_index_file_name = default_index_file_name
    else:
        print("download by number: index_file_name {}".format(index_file_name))
        use_index_file_name = index_file_name

    if len(groupby_dict_path) == 0:

        print("download by number: no groupby_dict_path given , use default groupby_dict_path {}".format(
            default_groupby_dict_path))
        use_groupby_dict_path = default_groupby_dict_path
    else:
        print("download by number: groupby_dict_path {}".format(groupby_dict_path))
        use_groupby_dict_path = groupby_dict_path

    if num == 0:
        print("download by number: no num given: use default  num {}".format(chunk_size))
    else:
        print("download by number: num {}".format(num))
        chunk_size = num

    print("read shuffled MCF code")
    ds = read_from_file(use_index_file_name)
    document_mcfs = ds['cpc_all'].to_list()

    print("read groupby dict")
    groupby_dict = pickle.load(open(use_groupby_dict_path, "rb"))

    # retrieve the db
    print("start retrieve")

    c = 0
    idx = 0
    for document_mcfs_chunk in _chunks(document_mcfs, chunk_size):
        idx += 1

        rl = []
        document_ids = [_get_document_id(mcf) for mcf in document_mcfs_chunk]
        cpc_codes = [groupby_dict[d_id] for d_id in document_ids]
        rl.append(_worker_mul(document_ids, document_mcfs_chunk, cpc_codes))

        yield rl


def document_by_mcfs(mcfs):
    '''
    download documents by given mcsf, the mcfs is one row in MCF files
    '''
    assert(isinstance(mcfs, list))

    document_ids = [_get_document_id(mcf) for mcf in mcfs]
    return download_by_ids(document_ids)


def download_by_ids(document_ids):
    '''
    download documents by given document_ids, the document_ids are given by a list
    '''
    assert(isinstance(document_ids, list))


def _test():
    index_file_name = "/Users/yining/Work/Capstone/TestAPI/shuffle_2000000_with_cpc_all"
    groupby_dict_path = "/Users/yining/Work/Capstone/TestAPI/groupby_dict_all"
    num = 1

    cnt = 0
    for d in download_by_number(index_file_name, groupby_dict_path, num):
        cnt += 1
        if cnt == 5:
            break
        print(d)


if __name__ == '__main__':
    #  index_file_name = "/Users/yining/Work/Capstone/TestAPI/shuffle_200000_with_cpc_all"
    #  download_and_save_all(index_file_name)
    _test()
