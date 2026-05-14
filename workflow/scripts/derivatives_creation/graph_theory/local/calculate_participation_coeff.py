import numpy as np
import pandas as pd
import argparse
import pickle
import os
import json
import networkx as nx
from bin_graph_from_fc import bin_graph_from_fc
import bct

parser = argparse.ArgumentParser(description="Calculate the participation coefficient for each ROI for each density")
parser.add_argument("--fc_path", type=str, help="The path to the regressed FC matrix for this subject")
parser.add_argument("--out_path", type=str, help="The path to the output file")
parser.add_argument("--min_density", type=float, help="The minimum density for the graph theory analysis")
parser.add_argument("--max_density", type=float, help="The maximum density for the graph theory analysis")
parser.add_argument("--density_step", type=float, help="The step size for the density range")
parser.add_argument("--networks_dir", type=str, help="The dir with network info")
parser.add_argument("--subid", type=str, help="The subid for this subject")
parser.add_argument("--sidecar_path", type=str, help="The path to the sidecar json file for this metric")
args = parser.parse_args()

# Load the partition info
with open(os.path.join(args.networks_dir, "partition_labels.pkl"), "rb") as f:
    labels = pickle.load(f)
with open(os.path.join(args.networks_dir, "partition.pkl"), "rb") as f:
    partition = pickle.load(f)
with open(os.path.join(args.networks_dir, "to_delete_partition.pkl"), "rb") as f:
    to_delete = pickle.load(f)

# Load the regressed FC matrix
fc = np.loadtxt(args.fc_path, delimiter='\t')
fc_mod = np.delete(fc, to_delete, 0)
fc_mod = np.delete(fc_mod, to_delete, 1)

# Convert partition to BCT format
partition_dict = {}
for i, network in enumerate(partition):
    partition_dict[i] = network

partition_bct = []
for i, node in enumerate(labels):
    for idx, network in partition_dict.items():
        if node in network:
            partition_bct.append(idx)

# Calculate the participation coeff of each ROI for each density
metric_per_density = {}
for gd in np.arange(args.min_density, args.max_density + args.density_step, args.density_step):
    metric_per_density[gd] = {}
    G_mod = bin_graph_from_fc(fc_mod, labels, gd)
    metrics = bct.participation_coef(nx.to_numpy_array(G_mod), partition_bct)
    for i, metric in enumerate(metrics):
        area = labels[i]
        metric_per_density[gd][area] = metric

# Save the metric for each density
with open(args.out_path, "wb") as f:
    pickle.dump(metric_per_density, f)

# Create json sidecar
with open("resources/graph_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [f"bids:static:/sub-{args.subid}/sub-{args.subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"]

with open(args.sidecar_path, "w") as f:
    json.dump(sidecar, f)