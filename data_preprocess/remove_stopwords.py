import sys
import os
import json

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

def remove_stopwords(input_path, output_path):
    with open(input_path, 'r') as input_file:
        with open(output_path, 'w') as output_file:
            for line in input_file:
                content = json.loads(line)
                tokens = content['doc_token']
                content['doc_token'] = [token for token in tokens if token not in stop_words]
                output_file.write(json.dumps(content))
                output_file.write('\n')
    
if __name__ == '__main__':

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)
            remove_stopwords(input_path, output_path)
    