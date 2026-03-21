import numpy as np
import pandas as pd
import argparse
import os
from sklearn.linear_model import LinearRegression
import pickle

parser = argparse.ArgumentParser(description="Regress demographic confounds out of the raw FCs")
parser.add_argument("--fc_dir", type=str, help="The path to the raw FC directory")
parser.add_argument("--subids", type=str, nargs="+", help="All the subids to be included")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
args = parser.parse_args()

demo_data = pd.read_csv(args.demo_data_path)

confounds = []
all_fcs = []

# Create the confounds matrix and aggregate the individual FCs
for subid in args.subids:
    cur_sub = demo_data.loc[demo_data["ID"] == subid]
    confounds.append([cur_sub.nmdare.item(), cur_sub.age.item(), cur_sub.sex.item() == 'f'])
    
    with open(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_windowed_FCs.pkl"), "rb") as f:
        sub_fcs = pickle.load(f)
    all_fcs.append(sub_fcs)

# Apply Fisher transformation to the FC values before fitting the regression model
all_fcs = np.arctanh(np.array(all_fcs))
confounds = np.array(confounds)

for sub_fcs in all_fcs:
    for fc in sub_fcs:
        np.fill_diagonal(fc, 1)

# For each FC value, train a regression model, and then use it to regress out the effect of confounds
for win in range(all_fcs.shape[1]):
    for i in range(all_fcs.shape[2]):
        for j in range(all_fcs.shape[3]):
            target = all_fcs[:, win, i, j]
            reg = LinearRegression().fit(confounds, target)
            
            for sub in range(len(confounds)):
                all_fcs[sub, win, i, j] -= confounds[sub, 1]*reg.coef_[1] + confounds[sub, 2]*reg.coef_[2]

all_fcs = np.tanh(all_fcs)

for i, subid in enumerate(args.subids):
    with open(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_windowed_FCs_regr.pkl"), "wb") as f:
        pickle.dump(all_fcs[i], f)