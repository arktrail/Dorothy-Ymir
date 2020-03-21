import os

data_path = "./"
file_list = [i for i in os.listdir(data_path) if i.endswith(".txt")]
print(file_list)