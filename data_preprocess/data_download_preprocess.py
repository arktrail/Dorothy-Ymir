import pickle
import slumber
from preprocess import *
from pipline_filters.bs_filters import *
from pipline_filters.string_filters import *

from datafile_loader import *


def get_objects_document(document_id):
    '''
    Download document from API
    :param document_id:  id for document
    :return:
    '''
    a = slumber.API('http://localhost:8000/api/v0')
    par = {'username': 'capstone2020', 'api_key': '48f0580836eaf85e7af82c57a0e7391a7e06530f'}
    patent = a.patent.get(document_id=document_id, **par, full_document=True)
    # patent = a.patent.get(document_id='US20140127591A1', **par, full_document=True)
    if len(patent['objects']) == 0:
        return {}
    return patent['objects'][0]['document']


def build_instance(s, cpc_codes):
    '''
    parse patent from what retrieved from api
    :param s: MCF code
    :param cpc_codes: all relative MCF codes that belongs to the same document with different cpc classifications
    :return:
    '''
    dct = get_objects_document(get_document_id(s))

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
                                    soupify(get_expanded_and_flattened_claims(dct))
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


def worder(document_mcf, cpc_codes):
    '''
    intend to work for multiprocessing
    :param document_mcf:
    :param cpc_codes:
    :return:
    '''
    data = build_instance(document_mcf, cpc_codes)
    return data


def get_document_id(s):
    '''
    get document id from MCF
    :param s: MCF
    :return:
    '''
    return 'US%s%s' % (s[10:18].lstrip(), s[0:2].lstrip())


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def main():
    chunk_size = 20_000

    print("read shuffled MCF code")
    file_name = "/Users/yining/Work/Capstone/TestAPI/shuffle_200000_with_cpc_all"
    ds = read_from_file(file_name)
    document_mcfs = ds['cpc_all'].to_list()

    print("read groupby dict")
    groupby_dict = pickle.load(open("./groupby_dict_all", "rb"))

    # retrieve the db
    print("start retrieve")

    c = 0
    idx = 0
    for document_mcfs_chunk in chunks(document_mcfs, chunk_size):
        idx += 1

        rl = []
        for document_mcf in document_mcfs_chunk:
            document_id = get_document_id(document_mcf)
            cpc_codes = groupby_dict[document_id]
            rl.append(worder(document_id, cpc_codes))
            c += 1
            if c % 100 == 0:
                print(c)

        # save to file
        save_chunk_file_name = "patent_200k_reparse_{}.p".format(idx)
        pickle.dump(rl, open(save_chunk_file_name, "wb"))


if __name__ == '__main__':
    main()
