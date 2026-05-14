import numpy as np
import pandas as pd
import argparse
import pickle
import os
import json
import networkx as nx
from networkx_robustness import networkx_robustness
from bin_graph_from_fc import bin_graph_from_fc

parser = argparse.ArgumentParser(description="Calculate the robustness against random attacks for each subject's FC matrix")
parser.add_argument("--input_path", type=str, help="The path to the regressed FC matrix for this subject")
parser.add_argument("--out_path", type=str, help="The path to the output file")
parser.add_argument("--min_density", type=float, help="The minimum density for the graph theory analysis")
parser.add_argument("--max_density", type=float, help="The maximum density for the graph theory analysis")
parser.add_argument("--density_step", type=float, help="The step size for the density range")
parser.add_argument("--labels_path", type=str, help="The path to the network labels")
parser.add_argument("--sidecar_path", type=str, help="The path to the output json sidecar file")
parser.add_argument("--subid", type=str, help="The subject ID for the json sidecar file")
args = parser.parse_args()

# Load the network labels
with open(args.labels_path, "rb") as f:
    labels = pickle.load(f)

# Load the regressed FC matrix
fc = np.loadtxt(args.input_path, delimiter='\t')

metric_per_density = {}
for gd in np.arange(args.min_density, args.max_density + args.density_step, args.density_step):
    G = bin_graph_from_fc(fc, labels, gd)
    initial, frac, apl = networkx_robustness.simulate_random_attack(G, attack_fraction=0.99999999)
    metric_per_density[gd] = np.sum(frac)

# Save the robustness metric for each density in a pickle file
with open(args.out_path, "wb") as f:
    pickle.dump(metric_per_density, f)

# Create json sidecar
with open("resources/graph_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [f"bids:static:/sub-{args.subid}/sub-{args.subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"]

with open(args.sidecar_path, "w") as f:
    json.dump(sidecar, f)