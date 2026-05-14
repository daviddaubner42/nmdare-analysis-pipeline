import numpy as np
import pandas as pd
import argparse
import pickle
import os
import json
from scipy.stats import permutation_test, false_discovery_control

parser = argparse.ArgumentParser(description="Perform group comparison for this metric")
parser.add_argument("--res_dir", type=str, help="The path to the local metric results directory")
parser.add_argument("--metric", type=str, help="The metric to be analysed")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographical data")
args = parser.parse_args()

# Load demo data
demo_data = pd.read_csv(args.demo_data_path)

# Load aggr metrics
metrics = pd.read_table(os.path.join(args.res_dir, f"task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{args.metric}Aggregated_relmat.tsv"))
metrics.rename(columns={"Unnamed: 0": "ROI"}, inplace=True)
subids = metrics.columns.drop("ROI")
rois = list(metrics["ROI"])

def statistic(x, y, axis):
    return np.mean(x, axis=axis) - np.mean(y, axis=axis)

ps = {}
stats = {}
# Perform group comparison for each ROI
for roi in rois:
    hcs = []
    nmdares = []
    for subid in subids:
        if demo_data.loc[demo_data["ID"] == subid]["nmdare"].item():
            nmdares.append(metrics[metrics["ROI"] == roi][subid])
        else:
            hcs.append(metrics[metrics["ROI"] == roi][subid])
    
    res = permutation_test([hcs, nmdares], statistic, n_resamples=10000)
    ps[roi] = res.pvalue
    stats[roi] = res.statistic

# Perform FDR correction
ps_fdr = false_discovery_control(list(ps.values())).T[0]

# Save the results
df = pd.DataFrame(np.array([np.array(list(ps.keys())).flatten(), np.array(list(ps.values())).flatten(), np.array(ps_fdr), np.array(list(stats.values())).flatten()]).T, columns=["ROI", "p", "p_FDR", "stat"])
df.to_csv(os.path.join(args.res_dir, f"task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{args.metric}PvaluesStats_relmat.tsv"), sep="\t")

# Create json sidecar
with open("resources/graph_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = ["bids:graph_theory/local:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{args.metric}Aggregated_relmat.tsv"]

with open(os.path.join(args.res_dir, f"task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-{args.metric}PvaluesStats_relmat.json"), "w") as f:
    json.dump(sidecar, f)