import numpy as np
import pandas as pd
import argparse
import os
import pickle

parser = argparse.ArgumentParser(description="Aggregate all global metrics across all subids into a single table")
parser.add_argument("--global_metrics_dir", type=str, help="The path to the directory with the global metrics for each subject")
parser.add_argument("--out_path", type=str, help="The path to the desired output csv file")
parser.add_argument("--subids", type=str, nargs="+", help="All the subids to be included")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
args = parser.parse_args()

# Load the demographic data
demo_data = pd.read_csv(args.demo_data_path)

# For each subject, calculate the average of each global metric across all thresholds
mean_metrics = {}
for subid in args.subids:
    with open(os.path.join(args.global_metrics_dir, f"sub-{subid}", f"sub-{subid}_abs_mean_connectivity.pkl"), "rb") as f:
        abs_mean_connectivity = pickle.load(f)
    with open(os.path.join(args.global_metrics_dir, f"sub-{subid}", f"sub-{subid}_avg_clustering.pkl"), "rb") as f:
        avg_clustering = pickle.load(f)
    with open(os.path.join(args.global_metrics_dir, f"sub-{subid}", f"sub-{subid}_global_efficiency.pkl"), "rb") as f:
        global_efficiency = pickle.load(f)
    with open(os.path.join(args.global_metrics_dir, f"sub-{subid}", f"sub-{subid}_modularity.pkl"), "rb") as f:
        modularity = pickle.load(f)
    with open(os.path.join(args.global_metrics_dir, f"sub-{subid}", f"sub-{subid}_assortativity.pkl"), "rb") as f:
        assortativity = pickle.load(f)
    with open(os.path.join(args.global_metrics_dir, f"sub-{subid}", f"sub-{subid}_robustness_random.pkl"), "rb") as f:
        robustness_random = pickle.load(f)
    with open(os.path.join(args.global_metrics_dir, f"sub-{subid}", f"sub-{subid}_robustness_targeted.pkl"), "rb") as f:
        robustness_targeted = pickle.load(f)
    
    mean_metrics[subid] = {
        "subid": subid,
        "NMDARE": demo_data[demo_data["ID"] == subid]["nmdare"].item(),
        "abs_mean_connectivity": abs_mean_connectivity,
        "avg_clustering": np.mean(list(avg_clustering.values())),
        "global_efficiency": np.mean(list(global_efficiency.values())),
        "modularity": np.mean(list(modularity.values())),
        "assortativity": np.mean(list(assortativity.values())),
        "robustness_random": np.mean(list(robustness_random.values())),
        "robustness_targeted": np.mean(list(robustness_targeted.values()))
    }

# Save the aggregated metrics to a csv file
mean_metrics_df = pd.DataFrame.from_dict(mean_metrics, orient='index')
mean_metrics_df.to_csv(args.out_path, index=False)