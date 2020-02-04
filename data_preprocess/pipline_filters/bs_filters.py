from bs4 import BeautifulSoup as bs
import re

def soupify(s):
    return bs(s, 'lxml')

def desoupify(s):
    return str(s)

def get_text(s):
    assert(isinstance(s, bs))
    return s.get_text()

def strip_headers(s):
    assert(isinstance(s, bs))
    for h in ['h2']:
        for tag in s.find_all(h):
            tag.decompose()
    return s

def strip_figrefs(s):
    assert(isinstance(s, bs))
    for tag in s.find_all('a', {'class': 'figref'}):
        tag.decompose()
    for tag in s.find_all('b'):
        try:
            if tag is not None and tag.contents is not None:
                if all([(isinstance(x, str) and x.isdigit()) for x in tag.contents if x is not None]):
                    tag.decompose()
        except:
            print(tag)
            raise
    return s

def strip_all_tables(s):
    assert(isinstance(s, bs))
    for tag in s.find_all(['pre', {'class': 'freetext-table'},'table']):
        tag.decompose()
    return s

def strip_pre_freetext_table(s):
    assert(isinstance(s, bs))
    for tag in s.find_all('pre', {'class': 'freetext-table'}):
        tag.decompose()
    return s

def strip_math(s):
    assert(isinstance(s, bs))
    for tag in s.find_all('span', {'class': ['formula','math']}):
        tag.decompose()
    return s

def flatten_tables(s):
    assert(isinstance(s, bs))
    for tag in s.find_all('table'):
        new_tag = bs(re.sub(r'\n','.\n',tag.get_text()))
        tag.replace_with(new_tag)
    return s