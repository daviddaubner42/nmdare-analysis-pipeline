import numpy as np
import pandas as pd
import argparse
import pickle
import os

parser = argparse.ArgumentParser(description="Aggregate all the local metrics into one metric per ROI per subject")
parser.add_argument("--results_dir", type=str, help="The path to the local metrics results directory")
parser.add_argument("--subids", type=str, nargs="+", help="All the subjects to be included in analysis")
parser.add_argument("--metric", type=str)
args = parser.parse_args()

# Get ROIs
with open(f"out/results/graph_theory/local/sub-{args.subids[0]}/sub-{args.subids[0]}_{args.metric}.pkl", "rb") as file:
    temp = pickle.load(file)
rois = list(temp[list(temp.keys())[0]].keys())

# For each subject, load the metrics and average them
metric = args.metric
metric_vals = {}
for roi in rois:
    metric_vals[roi] = {}
for subid in args.subids:
    with open(f"out/results/graph_theory/local/sub-{subid}/sub-{subid}_{metric}.pkl", "rb") as file:
        sub_metrics = pickle.load(file)
    for roi in rois:
        roi_metrics = []
        for gd, m in sub_metrics.items():
            roi_metrics.append(m[roi])
        metric_vals[roi][subid] = np.mean(roi_metrics)
df = pd.DataFrame(metric_vals).T
df.to_csv(f"out/results/graph_theory/local/{metric}_aggregated.csv")
