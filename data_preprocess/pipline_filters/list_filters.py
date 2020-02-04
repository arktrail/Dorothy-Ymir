import re

def depunctuate(lst):
    for itm in lst:
        itm = re.sub('[\p{P} i\n\r]*(.*?)[\p{P} \n\r]', '\1', itm)
        if len(itm) > 1:
            yield itm

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    # MSBIC: Dorothy-v.1-/search_engine_app/ps_proj/patent_search/clean_tokenize.py [4b61b53]
    # https://github.com/dorothy-ai/Dorothy-v.1-/commit/4b61b5355db46c9a4e81bb9c8622f29615aa9694
    # TODO: merge this with `depunctuate` function above
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            yield new_word

def omit_single_character_tokens(words):
    for word in words:
        if len(word) > 1:
            yield word

def space_delimited_join_list_to_string(words):
    return ' '.join(words)



numeric_rgx = re.compile(r'^([(){}1234567890., =-><+]+)$')
def denumerate(lst):
    for itm in lst:
        if not numeric_rgx.match(itm):
            yield itm

import inflect
def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    # MSBIC: Dorothy-v.1-/search_engine_app/ps_proj/patent_search/clean_tokenize.py [4b61b53]
    # https://github.com/dorothy-ai/Dorothy-v.1-/commit/4b61b5355db46c9a4e81bb9c8622f29615aa9694
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            yield new_word
        else:
            yield word



def words_to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    # MSBIC: Dorothy-v.1-/search_engine_app/ps_proj/patent_search/clean_tokenize.py [4b61b53]
    # https://github.com/dorothy-ai/Dorothy-v.1-/commit/4b61b5355db46c9a4e81bb9c8622f29615aa9694
    new_words = []
    for word in words:
        new_word = word.lower()
        yield new_word

import unicodedata
def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    # MSBIC: Dorothy-v.1-/search_engine_app/ps_proj/patent_search/clean_tokenize.py [4b61b53]
    # https://github.com/dorothy-ai/Dorothy-v.1-/commit/4b61b5355db46c9a4e81bb9c8622f29615aa9694
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        yield new_word




from nltk.stem import SnowballStemmer
nltk_snowball_stemmer_en = SnowballStemmer('english')
def stem_using_nltk_snowball_en(words):
    # MSBIC: Dorothy-v.1-/search_engine_app/ps_proj/patent_search/index_clean.py
    # https://github.com/dorothy-ai/Dorothy-v.1-/commit/4b61b5355db46c9a4e81bb9c8622f29615aa9694
    for word in words:
        stemmed_word = nltk_snowball_stemmer_en.stem(word)
        if stemmed_word:
            yield stemmed_word


from nltk.stem import LancasterStemmer
nltk_lancaster_stemmer = LancasterStemmer()
def stem_using_nltk_lancaster(words):
    """Stem words in list of tokenized words"""
    # MSBIC: Dorothy-v.1-/search_engine_app/ps_proj/patent_search/clean_tokenize.py [4b61b53]
    # https://github.com/dorothy-ai/Dorothy-v.1-/commit/4b61b5355db46c9a4e81bb9c8622f29615aa9694
    for word in words:
        stem = nltk_lancaster_stemmer.stem(word)
        yield stem


from nltk.stem import WordNetLemmatizer
nltk_wordnet_lemmatizer = WordNetLemmatizer()
def lemmatize_using_nltk_wordnet(words):
    """Lemmatize verbs in list of tokenized words"""
    # MSBIC: Dorothy-v.1-/search_engine_app/ps_proj/patent_search/clean_tokenize.py [4b61b53]
    # https://github.com/dorothy-ai/Dorothy-v.1-/commit/4b61b5355db46c9a4e81bb9c8622f29615aa9694
    for word in words:
        lemma = nltk_wordnet_lemmatizer.lemmatize(word, pos='v')
        yield lemma