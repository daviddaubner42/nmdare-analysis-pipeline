import numpy as np
import pandas as pd
import argparse
import pickle
import os

parser = argparse.ArgumentParser(description="Calculate the robustness against random attacks for each subject's FC matrix")
parser.add_argument("--input_path", type=str, help="The path to the regressed FC matrix for this subject")
parser.add_argument("--out_path", type=str, help="The path to the output file")
args = parser.parse_args()

# Load the regressed FC matrix
fc = np.loadtxt(args.input_path, delimiter=',')

# Calculate the absolute mean connectivity
amc = np.nanmean(np.absolute(fc))

# Save the absolute mean connectivity in a pickle file
with open(args.out_path, "wb") as f:
    pickle.dump(amc, f)