from treebuilder import load_description_from_file
from collections import OrderedDict 

data = load_description_from_file()

sorted_data = OrderedDict(sorted(data.items())) 
selections = []
for code, description in sorted_data.items():
    if len(code) != 4:
        continue
    selections.append({'code': code, "description": description})

print(selections)