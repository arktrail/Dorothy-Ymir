import numpy as np
import pandas as pd
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)  

EVALUATION_LAYER = "3rd"
GT_PATH = "./CNN/RESULT/grand_truth_{}.csv".format(EVALUATION_LAYER)
PRED_PATH = "./CNN/RESULT/probability_{}.csv".format(EVALUATION_LAYER)

pred_results = open(PRED_PATH, "r")
gt_results = open(GT_PATH, "r")


true_pred = 0
total_pred = 0
for (line_num, gt), (line_num, pred) in zip(enumerate(gt_results), enumerate(pred_results)):
	if line_num is 0:
		label_list = gt.rstrip('\n').split(",")
		continue

	gt_list = gt.rstrip('\n').split(",")
	pred_list = pred.rstrip('\n').split(",")
	pred_list = [float(i) for i in pred_list]

	top1_pred_idx = pred_list.index(max(pred_list))
	top1_pred = label_list[top1_pred_idx]

	if top1_pred in gt_list:
		true_pred += 1
	total_pred += 1

print(true_pred, total_pred, true_pred/total_pred)

