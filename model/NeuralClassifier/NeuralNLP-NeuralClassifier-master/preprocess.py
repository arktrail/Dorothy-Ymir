#!/usr/bin/env python
# coding: utf-8

# In[3]:


import nltk
import os
#  nltk.download()


# In[2]:


import pickle
import pandas as pd
from nltk.tokenize import word_tokenize
import string
import json
import os
from sklearn.model_selection import train_test_split


# In[3]:


def process_API_data(directory):
    
    master_df = []
    counter = 0
    for filename in os.listdir(directory):
        if filename.startswith('patent'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'rb') as file:
                d = pd.DataFrame(pickle.load(file))
            master_df.append(d)
            counter += 1
            print("finished processing file {}; count = {}".format(filename, counter))
    return pd.concat(master_df, ignore_index=True)


# In[4]:


API_data_directory = os.environ.get("SCRATCH") + '/data'
df_raw = process_API_data(API_data_directory)


# ## Data analysis

# In[5]:


# slice dictionary for cpc field
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


# In[6]:


# number of claims
len(df_raw)


# In[7]:


flattened_cpc = [y for x in df_raw["cpc_codes"] for y in x]


# In[8]:


# number of labels
len(flattened_cpc)


# In[9]:


# create analytics dataset without any text data
levels = ["cpc_section", "cpc_class", "cpc_subclass", "cpc_main_group", "cpc_subgroup"]
df_analytics = pd.DataFrame([[cpc[value[0]:value[1]] for key, value in cpc_field_slice_dict.items()] 
                             for cpc in flattened_cpc],
                            columns = list(cpc_field_slice_dict.keys()))  


# In[10]:


df_analytics.head()


# In[12]:


# number of unique values at differente levels
unique_label_dict = {}
for level in levels:
    unique_label_dict[level] = set(df_analytics[level])
    print("number of unique " + level + ": " + str(len(unique_label_dict[level])))


# In[13]:


df_raw["num_label"] = df_raw["cpc_codes"].apply(lambda x: len(x))


# In[14]:


# percent of patents with one label
len(df_raw[df_raw["num_label"] == 1]) / len(df_raw["num_label"])


# In[15]:


pd.concat([df_raw["num_label"].value_counts(),
           df_raw["num_label"].value_counts(normalize=True).mul(100)
           .round(1).astype(str)+"%"], axis=1, keys=['count', '%'])


# ## Data preprocess

# In[16]:


# text_column values: ['title', 'abstraction', 'claims', 'brief_summary', 'description']
text_columns = ['title', 'abstraction', 'claims']

# label_columns values: ['cpc_section', 'cpc_class', 'cpc_subclass', 'cpc_main_group', 'cpc_subgroup']
label_columns = ['cpc_section', 'cpc_class', 'cpc_subclass']


# In[17]:


def extract_labels(cpc_codes, label_columns):
    labels = set()
    for cpc_code in cpc_codes:
        level_label = []
        for label_column in label_columns:
            index = cpc_field_slice_dict[label_column]
            level_label.append(cpc_code[index[0]:index[1]])
        labels.add("--".join(level_label))
    return list(labels)


# In[18]:


def tokenize(text):
    tokens = word_tokenize(text)
    return [token.lower() for token in tokens if token not in string.punctuation]


# In[19]:


def merge_data(text_columns, label_columns, folder):
    df_text = pd.DataFrame(df_raw['cpc_codes'].apply(extract_labels, args=(label_columns,)))
    df_text['doc_token'] = df_raw[text_columns].agg(' '.join, axis=1).apply(tokenize)
    df_text.columns = ['doc_label', 'doc_token']
    
    df_train, df_valid_test = train_test_split(df_text, test_size=0.3, random_state=1)
    df_valid, df_test = train_test_split(df_valid_test, test_size=0.333, random_state=1)
    
    df_train.to_json(folder + "/train.json", orient='records')
    df_valid.to_json(folder + "/valid.json", orient='records')
    df_test.to_json(folder + "/test.json", orient='records')


# In[ ]:


merge_data(text_columns, label_columns, 'data')


# In[ ]:


# check if data is successfully created
with open('data/train.json') as f:
    data = json.load(f)
    print(data[0])


# ## Create taxonomy

# In[122]:


import pickle
cpc_label_tree_path = 'data/cpc_label_tree.pkl'
taxonomy_path = 'data/cpc.taxonomy'

with open(cpc_label_tree_path,"rb") as f:
    cpc_label_tree = pickle.load(f)


# In[154]:


with open(taxonomy_path, "w") as f:
    
    root_dict = cpc_label_tree['Root']
    children = "\t".join(root_dict.keys())
    f.write(f"Root\t{children}\n")
    
    for cpc_section, section_dict in root_dict.items():
        
        children = "\t".join(section_dict.keys())
        f.write(f"{cpc_section}\t{children}\n")
        
        for cpc_class, class_dict in section_dict.items():
            
            children = "\t".join(class_dict.keys())
            f.write(f"{cpc_class}\t{children}\n")
            
            for cpc_subclass, subclass_dict in class_dict.items():
                
                children = "\t".join(subclass_dict.keys())
                f.write(f"{cpc_subclass}\t{children}\n")
                
                for cpc_main_group, main_group_set in subclass_dict.items():
                    
                    children = "\t".join(main_group_set)
                    f.write(f"{cpc_main_group}\t{children}\n")

