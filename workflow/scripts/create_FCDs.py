import numpy as np
import pandas as pd
import argparse
import pickle
import matplotlib.pyplot as plt
import os

parser = argparse.ArgumentParser(description="Create the FCD matrices and histograms from the windowed FC matrices")
parser.add_argument("--windowed_fc_path", type=str, help="The path to the windowed FC matrices")
parser.add_argument("--out_dir", type=str, help="The path to the desired output directory for the FCD matrices and histograms")
parser.add_argument("--subid", type=str, help="The subid of the subject for which to create the FCD matrix and histogram")
args = parser.parse_args()

with open(args.windowed_fc_path, "rb") as f:
    windowed_fcs = pickle.load(f)

n_fcs = windowed_fcs[0].shape[0]

# Calculate the FCD matrix
FCD = np.zeros((n_fcs, n_fcs))
for i in range(n_fcs):
    for j in range(n_fcs):
        fc_i = windowed_fcs[i]
        np.fill_diagonal(fc_i, 0)
        fc_j = windowed_fcs[j]
        np.fill_diagonal(fc_j, 0)
        # Calculate the correlation between the upper triangle of the two FC matrices as the FCD value
        u_idx = np.triu_indices_from(fc_i, k=1)
        FCu1 = fc_i.copy()[u_idx]
        FCu2 = fc_j.copy()[u_idx]
        FCu1 = np.arctanh(FCu1)
        FCu2 = np.arctanh(FCu2)
        FCD[i, j] = np.corrcoef(FCu1, FCu2)[0, 1]

# Create the histogram of FCD values
fcd_flattened = FCD[np.triu_indices_from(FCD)]
hist = np.histogram(fcd_flattened, bins=100, range=(0, 1))

# Save the FCD matrix and histogram
np.savetxt(os.path.join(args.out_dir, f"{args.subid}_FCD.csv"), FCD, delimiter=',')
np.savetxt(os.path.join(args.out_dir, f"{args.subid}_FCD_hist.csv"), hist, delimiter=',')