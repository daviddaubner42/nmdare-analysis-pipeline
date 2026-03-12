import pandas as pd
import numpy as np
import pickle
import argparse
import nibabel as nib

parser = argparse.ArgumentParser(description="Calculate an FC matrix from a parcellated time series")
parser.add_argument("--ts_path", type=str, help="The path to the parcellated time series")
parser.add_argument("--excluded_rois_path", type=str, help="Path to file with regions not to be included in FC calculation")
parser.add_argument("--out_path", type=str, help="Path to the desired output FC file")
args = parser.parse_args()

with open(args.excluded_rois_path, "rb") as f:
    to_delete = pickle.load(f)

# Load the parcellated time series and delete the excluded regions
ts = np.array(nib.load(args.ts_path).dataobj)
ts = np.delete(ts, to_delete, 1)

# Calculate the FC matrix
cutoff = 5
ts = ts[cutoff:]
fc = np.corrcoef(ts, rowvar=False)

np.savetxt(args.out_path, fc, delimiter=',')