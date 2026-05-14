import numpy as np
import pandas as pd
import argparse
import os
import json
from scipy.stats import permutation_test, false_discovery_control

parser = argparse.ArgumentParser(description="Perform pairwise statistical comparison of FC values")
parser.add_argument("--fc_dir", type=str, help="The path to the raw FC directory")
parser.add_argument("--subids", type=str, nargs="+", help="All the subids to be included")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
args = parser.parse_args()

demo_data = pd.read_csv(args.demo_data_path)

# Separate the FCs into groups
nmdare_fcs_regr = []
hc_fcs_regr = []
for subid in args.subids:
    fc = np.loadtxt(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-regressedFC_relmat.tsv"), delimiter='\t')
    if demo_data[demo_data["ID"] == subid]["nmdare"].item() == 1:
        nmdare_fcs_regr.append(fc)
    else:
        hc_fcs_regr.append(fc)

# Create average FC for each group and save them
avg_nmdare_fc = np.mean(nmdare_fcs_regr, axis=0)
avg_hc_fc = np.mean(hc_fcs_regr, axis=0)
np.savetxt(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgNmdareFc_relmat.tsv"), avg_nmdare_fc, delimiter='\t')
np.savetxt(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgHcFc_relmat.tsv"), avg_hc_fc, delimiter='\t')

# Fisher transform the FC values before statistical testing
nmdare_fcs_fisher = np.arctanh(nmdare_fcs_regr)
hc_fcs_fisher = np.arctanh(hc_fcs_regr)

# Perform statistical comparison for each FC value
def statistic(x, y, axis):
    return np.mean(x, axis=axis) - np.mean(y, axis=axis)

p_vals = np.ones(nmdare_fcs_fisher.shape[1:])
stats = np.ones(nmdare_fcs_fisher.shape[1:])
for i in range(nmdare_fcs_fisher.shape[1]):
    for j in range(nmdare_fcs_fisher.shape[2]):
        res = permutation_test([nmdare_fcs_fisher[:, i, j], hc_fcs_fisher[:, i, j]], statistic, permutation_type="independent", n_resamples=100000, rng=13)
        p_vals[i, j] = res.pvalue
        stats[i, j] = res.statistic
np.fill_diagonal(p_vals, 1)

# Perform False Discovery Correction
p_vals_fdr = np.zeros(p_vals.shape)
p_vals_fdr[np.triu_indices_from(p_vals_fdr)] = false_discovery_control(p_vals[np.triu_indices_from(p_vals)])
p_vals_fdr = p_vals_fdr + p_vals_fdr.T - np.diag(np.diag(p_vals_fdr))
np.fill_diagonal(p_vals_fdr, 1)

# Save results
np.savetxt(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvals_relmat.tsv"), p_vals, delimiter='\t')
np.savetxt(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvalsFdr_relmat.tsv"), p_vals_fdr, delimiter='\t')
np.savetxt(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonTestStats_relmat.tsv"), stats, delimiter='\t')

# Create json sidecar
with open("resources/static_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = []
for subid in args.subids:
    sources.append(f"bids:static:sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-regressedFC_relmat.tsv")

sidecar["Sources"] = sources

with open(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgNmdareFc_relmat.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgHcFc_relmat.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvals_relmat.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonPvalsFdr_relmat.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fc_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-pairwiseComparisonTestStats_relmat.json"), "w") as f:
    json.dump(sidecar, f)