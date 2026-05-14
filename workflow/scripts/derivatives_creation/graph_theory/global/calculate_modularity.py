import numpy as np
import pandas as pd
import argparse
import pickle
import os
import json
import networkx as nx
from bin_graph_from_fc import bin_graph_from_fc

parser = argparse.ArgumentParser(description="Calculate the modularity for each subject's FC matrix")
parser.add_argument("--input_path", type=str, help="The path to the regressed FC matrix for this subject")
parser.add_argument("--out_path", type=str, help="The path to the output file")
parser.add_argument("--min_density", type=float, help="The minimum density for the graph theory analysis")
parser.add_argument("--max_density", type=float, help="The maximum density for the graph theory analysis")
parser.add_argument("--density_step", type=float, help="The step size for the density range")
parser.add_argument("--network_dir", type=str, help="The path to the directory with network information")
parser.add_argument("--sidecar_path", type=str, help="The path to the output json sidecar file")
parser.add_argument("--subid", type=str, help="The subject ID for the json sidecar file")
args = parser.parse_args()

# Load the regressed FC matrix and the partition
fc = np.loadtxt(args.input_path, delimiter='\t')
with open(os.path.join(args.network_dir, "partition.pkl"), "rb") as f:
    partition = pickle.load(f)
with open(os.path.join(args.network_dir, "to_delete_partition.pkl"), "rb") as f:
    to_delete_partition = pickle.load(f)
with open(os.path.join(args.network_dir, "partition_labels.pkl"), "rb") as f:
    labels = pickle.load(f)

metric_per_density = {}
for gd in np.arange(args.min_density, args.max_density + args.density_step, args.density_step):
    fc_mod = np.delete(fc, to_delete_partition, axis=0)
    fc_mod = np.delete(fc_mod, to_delete_partition, axis=1)
    G_mod = bin_graph_from_fc(fc_mod, labels, gd)
    metric_per_density[gd] = nx.algorithms.community.modularity(G_mod, partition)


# Save the modularity for each density in a pickle file
with open(args.out_path, "wb") as f:
    pickle.dump(metric_per_density, f)

# Create json sidecar
with open("resources/graph_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [f"bids:static:/sub-{args.subid}/sub-{args.subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"]

with open(args.sidecar_path, "w") as f:
    json.dump(sidecar, f)