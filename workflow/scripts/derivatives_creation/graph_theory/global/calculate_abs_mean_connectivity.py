import numpy as np
import pandas as pd
import argparse
import pickle
import os
import json

parser = argparse.ArgumentParser(description="Calculate the robustness against random attacks for each subject's FC matrix")
parser.add_argument("--input_path", type=str, help="The path to the regressed FC matrix for this subject")
parser.add_argument("--out_path", type=str, help="The path to the output file")
parser.add_argument("--subid", type=str, help="The subject ID for the json sidecar file")
parser.add_argument("--sidecar_path", type=str, help="The path to the output json sidecar file")
args = parser.parse_args()

# Load the regressed FC matrix
fc = np.loadtxt(args.input_path, delimiter='\t')

# Calculate the absolute mean connectivity
amc = np.nanmean(np.absolute(fc))

# Save the absolute mean connectivity in a pickle file
with open(args.out_path, "wb") as f:
    pickle.dump(amc, f)

# Create json sidecar
with open("resources/graph_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [f"bids:static:/sub-{args.subid}/sub-{args.subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"]

with open(args.sidecar_path, "w") as f:
    json.dump(sidecar, f)