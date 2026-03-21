import numpy as np
import pandas as pd
import argparse
import pickle
import os
from scipy.stats import permutation_test
from sklearn.linear_model import LinearRegression

parser = argparse.ArgumentParser(description="Compare the global metrics between the two groups")
parser.add_argument("--metric_path", type=str, help="The path to the csv file with global metrics")
parser.add_argument("--out_dir", type=str, help="The directory where the output files will be saved")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
parser.add_argument("--subids", type=str, nargs="+", help="All the subids to be included")
args = parser.parse_args()

demo_data = pd.read_csv(args.demo_data_path)

confounds = []

# Create the confounds matrix
for subid in args.subids:
    cur_sub = demo_data.loc[demo_data["ID"] == subid]
    confounds.append([cur_sub.nmdare.item(), cur_sub.age.item(), cur_sub.sex.item() == 'f'])
confounds = np.array(confounds)

# Load the global metrics data
props = pd.read_csv(args.metric_path)

ps = {}
stats = {}

metric_names = ["abs_mean_connectivity", "avg_clustering", "global_efficiency", "modularity", "assortativity", "robustness_random", "robustness_targeted"]

def statistic(x, y, axis):
    return np.mean(x, axis=axis) - np.mean(y, axis=axis)

for metric in metric_names:
    # Regress confounds out
    target = []
    for subid in args.subids:
        target.append(props[props["subid"] == subid][metric].values)
    reg = LinearRegression().fit(confounds, target)

    for i, subid in enumerate(args.subids):
        props[props["subid"] == subid][metric] -= confounds[i, 1]*reg.coef_[0][1] + confounds[i, 2]*reg.coef_[0][2]

    # Compare groups
    nmdare_values = props[props["NMDARE"] == 1][metric].values
    hc_values = props[props["NMDARE"] == 0][metric].values
    res = permutation_test([nmdare_values, hc_values], statistic, permutation_type="independent", n_resamples=100000, rng=13)
    ps[metric] = res.pvalue
    stats[metric] = res.statistic

# Save results
with open(os.path.join(args.out_dir, "global_metric_ps.pkl"), "wb") as f:
    pickle.dump(ps, f)
with open(os.path.join(args.out_dir, "global_metric_stats.pkl"), "wb") as f:
    pickle.dump(stats, f)