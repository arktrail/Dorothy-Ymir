import copy
from collections import defaultdict

# Create a hierarchical structure
# =========================================================
def make(): return defaultdict(make)


def dicts(t): return {k: dicts(t[k]) for k in t}

# Add labels to a hierarchical structure
# ========================================================= 
def add(t, path):
    for node in path:
        t = t[node]

# Search parent labels
# =========================================================
def search_parent(tree,child,layer=1,prev_parent='root'):
    for k,v in list(tree.items()):
        if(k == child):
                return prev_parent
        else:
                if len(v) >= 1:
                        layer += 1
                        found = search_parent(v, child, layer,k)
                        if found:
                                return found
                        layer -=1
                else:
                        continue

# Search child labels
# =========================================================
def search_child(tree,node,layer=1):
    if (node == "root" or node =="ROOT" or node == "Root"):
        return list(tree.keys())
    for k,v in list(tree.items()):
        if(k == node):
            return list(v.keys())
        else:
            if len(v) >= 1:
                layer += 1
                found = search_child(v, node, layer)
                if found:
                    return found
                layer -=1
            else:
                continue

# Search path from the root of the specified label
# =========================================================
def search_path(tree, node):
        start_node = copy.deepcopy(node)
        path = [start_node]
        while (node != "root"):
                node = search_parent(tree, node)
                path.append(node)

        return path
