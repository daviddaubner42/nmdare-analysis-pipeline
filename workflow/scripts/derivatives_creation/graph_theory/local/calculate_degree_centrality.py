import numpy as np
import pandas as pd
import argparse
import pickle
import os
import json
import networkx as nx
from bin_graph_from_fc import bin_graph_from_fc

parser = argparse.ArgumentParser(description="Calculate the degree centrality for each ROI for each density")
parser.add_argument("--fc_path", type=str, help="The path to the regressed FC matrix for this subject")
parser.add_argument("--out_path", type=str, help="The path to the output file")
parser.add_argument("--min_density", type=float, help="The minimum density for the graph theory analysis")
parser.add_argument("--max_density", type=float, help="The maximum density for the graph theory analysis")
parser.add_argument("--density_step", type=float, help="The step size for the density range")
parser.add_argument("--labels_path", type=str, help="The path to the labels")
parser.add_argument("--subid", type=str, help="The subid for this subject")
parser.add_argument("--sidecar_path", type=str, help="The path to the sidecar json file for this metric")
args = parser.parse_args()

# Load the network labels
with open(args.labels_path, "rb") as f:
    labels = pickle.load(f)

# Load the regressed FC matrix
fc = np.loadtxt(args.fc_path, delimiter='\t')

# Calculate the betweenness centrality of each ROI for each density
metric_per_density = {}
for gd in np.arange(args.min_density, args.max_density + args.density_step, args.density_step):
    metric_per_density[gd] = {}
    G = bin_graph_from_fc(fc, labels, gd)
    metrics = dict(G.degree())
    for area, metric in metrics.items():
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