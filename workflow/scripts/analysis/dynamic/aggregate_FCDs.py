import pickle
import os
import numpy as np
import pandas as pd
import argparse
import json
from sklearn.linear_model import LinearRegression

parser = argparse.ArgumentParser(description="Plot the results of the pairwise FC comparison")
parser.add_argument("--fcds_path", type=str, help="The path to the FCD results directory")
parser.add_argument("--subids", type=str, nargs="+", help="All the subids to be included")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
args = parser.parse_args()

# Load demographic data
demo_data = pd.read_csv(args.demo_data_path)

confounds = []
fcds = {}
hists = {}

# Create the confounds matrix and load the FCD results
for subid in args.subids:
    cur_sub = demo_data.loc[demo_data["ID"] == subid]
    confounds.append([cur_sub.nmdare.item(), cur_sub.age.item(), cur_sub.sex.item() == 'f'])
    
    fcds[subid] = np.loadtxt(os.path.join(args.fcds_path, f"sub-{subid}", f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCD_relmat.tsv"), delimiter='\t')
    hists[subid] = np.loadtxt(os.path.join(args.fcds_path, f"sub-{subid}", f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistogram_histogram.tsv"), delimiter='\t')
confounds = np.array(confounds)

# Save raw results
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDs_relmat.pkl"), "wb") as f:
    pickle.dump(fcds, f)
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistograms_histogram.pkl"), "wb") as f:
    pickle.dump(hists, f)

# Regress the confounds out of the histograms
all_hists = np.array(list(hists.values()))
for bin in range(all_hists.shape[1]):
    target = all_hists[:, bin]
    reg = LinearRegression().fit(confounds, target)

    for i, subid in enumerate(args.subids):
        hists[subid][bin] -= confounds[i, 1]*reg.coef_[1] + confounds[i, 2]*reg.coef_[2]

# Save regressed histograms
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistogramsRegressed_histogram.pkl"), "wb") as f:
    pickle.dump(hists, f)

# Create json sidecar
with open("resources/dynamic_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = []
for subid in args.subids:
    sources.append(f"bids:dynamic:/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCD_relmat.tsv")
    sources.append(f"bids:dynamic:/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistogram_histogram.tsv")
sidecar["Sources"] = sources

with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDs_relmat.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistograms_histogram.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistogramsRegressed_histogram.json"), "w") as f:
    json.dump(sidecar, f)