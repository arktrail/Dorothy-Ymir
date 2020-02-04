# import regex as re

import re

def replace_non_alpha_characters_by_space(input_string):
    output_string = input_string
    for ch_rep in [["[^a-z]", " "], [" [ ]+", " "], ]:
        output_string = re.sub(ch_rep[0], ch_rep[1], output_string)
    return output_string


def string_to_lowercase(input_string):
    return input_string.lower()


def strip_string(input_string):
    return input_string.strip()


def yield_whitespace_split_tokens(input_string):
    for i in input_string.split():
        yield i


def normalize_whitespace(s):
    assert (isinstance(s, str))
    return re.sub(r' {2,}', ' ', s)


def normalize_newlines(s):
    assert (isinstance(s, str))
    return re.sub(r'\n{2,}', '\n', s)


def replace_newlines_with_spaces(s):
    assert (isinstance(s, str))
    return re.sub(r'\n', ' ', s)


def normalize_nucleotides(s):
    assert (isinstance(s, str))
    return re.sub(r'(5\'[ ACTG]+?3\')', lambda m: re.sub(r' ', '', m.group(1)), s)


def yield_substring_chunks(input_string, max_length):
    if len(input_string) < max_length:
        yield input_string
    else:
        words = input_string.split(' ')
        chunk = []
        chunk_len = 0
        for w in words:
            if (chunk_len + len(w) + 1) < max_length:
                chunk.append(w)
                chunk_len = chunk_len + len(w) + 1
            else:
                yield ' '.join(chunk)
                chunk = []
                chunk_len = 0


# import spacy
#
# _spacy_en_nlp = spacy.load('en')
#
#
# def spacy_lemmatize_and_tokenize(s):
#     assert (isinstance(s, str))
#     for chunk in yield_substring_chunks(s, 999999):
#         for token in _spacy_en_nlp(chunk):
#             yield token.lemma_.lower()


import nltk


def nltk_word_tokenize(input_string):
    for word in nltk.word_tokenize(input_string):
        yield word