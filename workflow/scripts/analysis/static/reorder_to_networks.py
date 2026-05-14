import numpy as np
import pandas as pd
import argparse
import os
import json
import pickle

parser = argparse.ArgumentParser(description="Reorder the average FCs, p-values and statistics to be organized by network")
parser.add_argument("--results_dir", type=str, help="The path to the results directory for the pairwise FC comparison")
parser.add_argument("--network_dir", type=str, help="The path to the directory with network information")
args = parser.parse_args()

# Load the average FC matrices, p-values, statistics, and network information
avg_nmdare_fc = np.loadtxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgNmdareFc_relmat.tsv"), delimiter='\t')
avg_hc_fc = np.loadtxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgHcFc_relmat.tsv"), delimiter='\t')
p_vals = np.loadtxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvals_relmat.tsv"), delimiter='\t')
p_vals_fdr = np.loadtxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvalsFdr_relmat.tsv"), delimiter='\t')
stats = np.loadtxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonTestStats_relmat.tsv"), delimiter='\t')
with open(os.path.join(args.network_dir, "networks.pkl"), "rb") as f:
    networks = pickle.load(f)
with open(os.path.join(args.network_dir, "network_labels.pkl"), "rb") as f:
    network_labels = pickle.load(f)

# Get the indices corresponding to each label in the original ordering
og_idxs = {}
for i, label in enumerate(network_labels):
    og_idxs[label] = i

# Create the dictionary describing the new ordering
idx_transform = {}
i = 0
for net in networks:
    for label in net:
        idx_transform[og_idxs[label]] = i
        i += 1

# Reorder the p-values and statistics according to the new ordering
n = len(p_vals)
new_p_vals = np.zeros((n, n))
new_p_vals_fdr = np.zeros((n, n))
new_stats = np.zeros((n, n))
new_avg_nmdare_fc = np.zeros((n, n))
new_avg_hc_fc = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        new_i = idx_transform[i]
        new_j = idx_transform[j]
        new_p_vals[new_i, new_j] = p_vals[i, j]
        new_p_vals_fdr[new_i, new_j] = p_vals_fdr[i, j]
        new_stats[new_i, new_j] = stats[i, j]
        new_avg_nmdare_fc[new_i, new_j] = avg_nmdare_fc[i, j]
        new_avg_hc_fc[new_i, new_j] = avg_hc_fc[i, j]

# Save the average FC matrices and reordered p-values and statistics
np.savetxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedAvgNmdareFc_relmat.tsv"), new_p_vals, delimiter='\t')
np.savetxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedAvgHcFc_relmat.tsv"), new_p_vals_fdr, delimiter='\t')
np.savetxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedPairwiseComparisonPvals_relmat.tsv"), new_stats, delimiter='\t')
np.savetxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedPairwiseComparisonPvalsFdr_relmat.tsv"), new_avg_nmdare_fc, delimiter='\t')
np.savetxt(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedPairwiseComparisonTestStats_relmat.tsv"), new_avg_hc_fc, delimiter='\t')

# Create json sidecars

with open("resources/static_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [f"bids:static:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgNmdareFc_relmat.tsv"]
with open(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedAvgNmdareFc_relmat.json"), "w") as f:
    json.dump(sidecar, f)
sidecar["Sources"] = [f"bids:static:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgHcFc_relmat.tsv"]
with open(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedAvgHcFc_relmat.json"), "w") as f:
    json.dump(sidecar, f)
sidecar["Sources"] = [f"bids:static:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvals_relmat.tsv"]
with open(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedPairwiseComparisonPvals_relmat.json"), "w") as f:
    json.dump(sidecar, f)
sidecar["Sources"] = [f"bids:static:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvalsFdr_relmat.tsv"]
with open(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedPairwiseComparisonPvalsFdr_relmat.json"), "w") as f:
    json.dump(sidecar, f)
sidecar["Sources"] = [f"bids:static:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonTestStats_relmat.tsv"]
with open(os.path.join(args.results_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-reorderedPairwiseComparisonTestStats_relmat.json"), "w") as f:
    json.dump(sidecar, f)