import numpy as np
import pandas as pd
import argparse
import os
import json
from sklearn.linear_model import LinearRegression

parser = argparse.ArgumentParser(description="Regress demographic confounds out of the raw FCs")
parser.add_argument("--fc_dir", type=str, help="The path to the raw FC directory")
parser.add_argument("--subids", type=str, nargs="+", help="All the subids to be included")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
args = parser.parse_args()

demo_data = pd.read_csv(args.demo_data_path)

confounds = []
fcs = []

# Create the confounds matrix and aggregate the individual FCs
for subid in args.subids:
    cur_sub = demo_data.loc[demo_data["ID"] == subid]
    confounds.append([cur_sub.nmdare.item(), cur_sub.age.item(), cur_sub.sex.item() == 'f'])
    
    fc = np.loadtxt(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"), delimiter='\t')
    fcs.append(fc)

# Apply Fisher transformation to the FC values before fitting the regression model
fcs = np.arctanh(fcs)
confounds = np.array(confounds)

for fc in fcs:
    np.fill_diagonal(fc, 1)

# For each FC value, train a regression model, and then use it to regress out the effect of confounds
for i in range(fcs.shape[1]):
    for j in range(fcs.shape[2]):
        target = fcs[:, i, j]
        reg = LinearRegression().fit(confounds, target)
        
        for sub in range(len(confounds)):
            fcs[sub, i, j] -= confounds[sub, 1]*reg.coef_[1] + confounds[sub, 2]*reg.coef_[2]

fcs = np.tanh(fcs)

for i, subid in enumerate(args.subids):
    np.savetxt(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-regressedFC_relmat.tsv"), fcs[i], delimiter='\t')

# Create json sidecar
with open("resources/static_sidecar.json", "rb") as f:
    sidecar = json.load(f)

for subid in args.subids:
    sidecar["Sources"] = [f"bids:static:sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"]
    with open(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-regressedFC_relmat.json"), "w") as f:
        json.dump(sidecar, f)