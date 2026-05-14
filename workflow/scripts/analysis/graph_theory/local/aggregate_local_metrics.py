import numpy as np
import pandas as pd
import argparse
import pickle
import os
import json

parser = argparse.ArgumentParser(description="Aggregate all the local metrics into one metric per ROI per subject")
parser.add_argument("--results_dir", type=str, help="The path to the local metrics results directory")
parser.add_argument("--subids", type=str, nargs="+", help="All the subjects to be included in analysis")
parser.add_argument("--metric", type=str)
args = parser.parse_args()

# Get ROIs
with open(f"{args.results_dir}/sub-{args.subids[0]}/sub-{args.subids[0]}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{args.metric}_relmat.pkl", "rb") as file:
    temp = pickle.load(file)
rois = list(temp[list(temp.keys())[0]].keys())

# For each subject, load the metrics and average them
metric = args.metric
metric_vals = {}
for roi in rois:
    metric_vals[roi] = {}
for subid in args.subids:
    with open(f"{args.results_dir}/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{metric}_relmat.pkl", "rb") as file:
        sub_metrics = pickle.load(file)
    for roi in rois:
        roi_metrics = []
        for gd, m in sub_metrics.items():
            roi_metrics.append(m[roi])
        metric_vals[roi][subid] = np.mean(roi_metrics)
df = pd.DataFrame(metric_vals).T
df.to_csv(f"{args.results_dir}/task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{metric}Aggregated_relmat.tsv", sep="\t")

# Create json sidecar
with open("resources/graph_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = []
for subid in args.subids:
    sources.append(f"bids:static:/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{metric}_relmat.pkl")
sidecar["Sources"] = sources

with open(os.path.join(args.results_dir, f"task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{metric}Aggregated_relmat.json"), "w") as f:
    json.dump(sidecar, f)