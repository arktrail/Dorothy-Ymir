from bs4 import BeautifulSoup as bs
import re

def get_brief_summary(dct):
    r = ''
    for f in ['BRIEF_SUMMARY']:
        if f in dct['description']:
            if 'normalized' in dct['description'][f]:
                r = dct['description'][f]['normalized']
    return r

def get_detailed_description(dct):
    r = ''
    for f in ['DETAILED_DESC']:
        if f in dct['description']:
            if 'normalized' in dct['description'][f]:
                r = dct['description'][f]['normalized']
    return r

def get_description(dct):
    r = []
    for f in ['BRIEF_SUMMARY','DETAILED_DESC']:
        if f in dct['description']:
            if 'normalized' in dct['description'][f]:
                r.append(dct['description'][f]['normalized'])
    return '\n'.join(r)

def get_abstract(dct):
    return dct['abstract']['normalized']

def get_title(dct):
    return dct['title']

def get_claims(dct):
    return '\n'.join([c['normalized'] for c in dct['claims']])

initial_nums_rgx = re.compile('^[\W|\d|\.]?')

def expand_claims(clm_id, clm_bs, claims):
    b = clm_bs.find('b')
    if b is not None:
        b.decompose()
    for a in clm_bs.find_all_next('a', {'class':'claim'}):
        s = clm_bs.new_tag('sup')
        if a['idref'] == clm_id:
            s.string = 'THIS CLAIM'
        else:
            s.string = claims[a['idref']][:-1]
        a.insert_after(s)
        a.decompose()
    claims[clm_id] = re.sub(initial_nums_rgx, '', clm_bs.get_text())
    return claims

def get_expanded_claims_dict(dct):
    claims = {}
    for clm in dct['claims']:
        clm_bs = bs(clm['normalized'], features='lxml')
        claims = expand_claims(clm['id'], clm_bs, claims)
    return claims

def get_expanded_and_flattened_claims(dct):
    claims = get_expanded_claims_dict(dct)
    return '\n'.join([v for k,v in sorted(claims.items(), key=lambda tpl: tpl[0])])


def get_normalized_text(field, expanded_claims_dict=False, flatten_claims=True):
    if field == 'description':
        return get_description
    elif field == 'brief_summary':
        return get_brief_summary
    elif field == 'detailed_description':
        return get_detailed_description
    elif field == 'abstract':
        return get_abstract
    elif field == 'title':
        return get_title
    elif field == 'claims':
        if expanded_claims_dict:
            if flatten_claims:
                return get_expanded_and_flattened_claims
            else:
                get_expanded_claims_dict
        else:
            return get_claims
    else:
        msg = 'Unknown field: %s!' % field
        raise KeyError(msg)