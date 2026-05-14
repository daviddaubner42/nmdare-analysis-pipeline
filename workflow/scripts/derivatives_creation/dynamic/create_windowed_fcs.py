import pandas as pd
import numpy as np
import pickle
import argparse
import json
import nibabel as nib

parser = argparse.ArgumentParser(description="Calculate an FC matrix from a parcellated time series")
parser.add_argument("--ts_path", type=str, help="The path to the parcellated time series")
parser.add_argument("--excluded_rois_path", type=str, help="Path to file with regions not to be included in FC calculation")
parser.add_argument("--out_path", type=str, help="Path to the desired output FC file")
parser.add_argument("--window_size", type=int, help="The size of the window to be used for calculating windowed FCs")
parser.add_argument("--step_size", type=int, help="The step size to be used for calculating windowed FCs")
parser.add_argument("--subid", type=str, help="The ID of the current subject")
parser.add_argument("--sidecar_path", type=str, help="The path to the output json sidecar file")
args = parser.parse_args()

with open(args.excluded_rois_path, "rb") as f:
    to_delete = pickle.load(f)

# Load the parcellated time series and delete the excluded regions
ts = np.array(nib.load(args.ts_path).dataobj)
ts = np.delete(ts, to_delete, 1)

# Calculate the windowed FC matrices
n_windows = len(range(0, ts.shape[0] - args.window_size, args.step_size))
windowed_fcs = []
for i in range(0, ts.shape[0] - args.window_size, args.step_size):
    window_ts = ts[i:i+args.window_size, :]
    fc = np.corrcoef(window_ts, rowvar=False)
    np.fill_diagonal(fc, np.nan)
    windowed_fcs.append(fc)

# Save the windowed FC matrices
with open(args.out_path, "wb") as f:
    pickle.dump(windowed_fcs, f)

# Create json sidecar
with open("resources/dynamic_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [f"bids:xcp_d:/sub-{args.subid}/func/sub-{args.subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_stat-mean_timeseries.ptseries.nii"]

with open(args.sidecar_path, "w") as f:
    json.dump(sidecar, f)