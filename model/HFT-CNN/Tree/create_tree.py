import pickle
import copy 

def dfs(tree, path, cur_key, all_path):
	path.append(cur_key)
	if len(path) > 6 or type(tree).__name__ != 'dict':
		all_path.append(copy.deepcopy(path))
		path.pop()
	else:
		for child in tree[cur_key]:
			dfs(tree[cur_key], path, child, all_path)
		path.pop()

if __name__ == '__main__':
	tree = pickle.load(open("cpc_label_tree.pkl", "rb"))
	all_path = []
	for section in tree["Root"].keys():
		dfs(tree["Root"], [], section, all_path)
	print(len(all_path))
	

	cpc_classifications_labels_set = set()
	for path in all_path:
		cur_hierachy_list = []
		for i in range(len(path)):
			if i == 0:
				cur_hierachy_list.append(path[i])
			else:
				prev_len = len(path[i-1])
				cur_level_label = cur_hierachy_list[i-1].split("<")[-1] + "@" + path[i][prev_len:].strip()
				cur_hierachy_list.append(cur_hierachy_list[i-1] + "<" + cur_level_label)
		# print(cur_hierachy_list)
		cpc_classifications_labels_set.update(cur_hierachy_list)

	print(len(cpc_classifications_labels_set))
	
	tree_path = "./CPC_subgroup.tree"
	f = open(tree_path, "w")
	for label in cpc_classifications_labels_set:
		f.write(label)
		f.write("\n")
	f.close()	
