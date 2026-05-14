import matplotlib.pyplot as plt
import matplotlib
import pickle
import scienceplots
import os
import json
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Plot the results of the pairwise FC comparison")
parser.add_argument("--fcds_path", type=str, help="The path to the FCD results directory")
parser.add_argument("--subids", type=str, nargs="+", help="All the subids to be included")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
args = parser.parse_args()

# Plotting settings
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
plt.style.use(['ieee'])
plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif"
})

cm = 1/2.54

# Load demographic data
demo_data = pd.read_csv(args.demo_data_path)

# Load FCD results
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDs_relmat.pkl"), "rb") as f:
    fcds = pickle.load(f)
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistograms_histogram.pkl"), "rb") as f:
    hists = pickle.load(f)
with open(os.path.join(args.fcds_path, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistogramsRegressed_histogram.pkl"), "rb") as f:
    hists_regr = pickle.load(f)

nmdare_fcds = []
hc_fcds = []
nmdare_hists = []
hc_hists = []
nmdare_hists_regr = []
hc_hists_regr = []

for subid in args.subids:
    if demo_data[demo_data["ID"] == subid]["nmdare"].item() == 1:
        nmdare_fcds.append(fcds[subid])
        nmdare_hists.append(hists[subid])
        nmdare_hists_regr.append(hists_regr[subid])
    else:
        hc_fcds.append(fcds[subid])
        hc_hists.append(hists[subid])
        hc_hists_regr.append(hists_regr[subid])

avg_nmdare_fcd = np.mean(nmdare_fcds, axis=0)
avg_hc_fcd = np.mean(hc_fcds, axis=0)
avg_nmdare_hist = np.mean(nmdare_hists, axis=0)
avg_hc_hist = np.mean(hc_hists, axis=0)
avg_nmdare_hist_regr = np.mean(nmdare_hists_regr, axis=0)
avg_hc_hist_regr = np.mean(hc_hists_regr, axis=0)

# Plot the average FCD matrices for each group

fig, ax = plt.subplots(1, 2, figsize=(14.5*cm, 8.96*cm), dpi=600)
hc = ax[0].imshow(avg_hc_fcd, cmap="viridis", vmin=0, vmax=1)
ax[0].set_title("Healthy Controls", fontsize=7)
ax[0].set_ylabel("Windowed FC #", fontsize=7)
ax[0].set_xlabel("Windowed FC #", fontsize=7)
nmdare = ax[1].imshow(avg_nmdare_fcd, cmap="viridis", vmin=0, vmax=1)
ax[1].set_title("NMDARE Patients", fontsize=7)
ax[1].set_xlabel("Windowed FC #", fontsize=7)

cbar = fig.colorbar(hc, ax=ax, orientation="vertical", shrink=0.8)
cbar.set_label("Pearson correlation r", fontsize=7)
cbar.ax.set_yticks([0, 0.3, 0.65, 1])
cbar.ax.tick_params(labelsize=7, length=0)
cbar.outline.set_linewidth(0.1)

fig.savefig(f"{args.fcds_path}/figures/task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgFCDcomparison_figure.png", bbox_inches="tight")
    
# Test distribution similarity between groups using Kolmogorov-Smirnov test
from scipy.stats import kstest

p_hist = kstest(np.array(nmdare_hists).mean(axis=0), np.array(hc_hists).mean(axis=0)).pvalue
p_hist_regr = kstest(np.array(nmdare_hists_regr).mean(axis=0), np.array(hc_hists_regr).mean(axis=0)).pvalue

# Plot the average FCD histograms for each group

fig, ax = plt.subplots(1, 1, figsize=(14.5*cm, 8*cm), dpi=600)
hc = ax.plot(avg_hc_hist, label="Healthy controls")
hc_stds = np.std(hc_hists, axis=0)
ax.fill_between(np.arange(100), avg_nmdare_hist-hc_stds, avg_nmdare_hist+hc_stds, color="gray", alpha=0.5)
ax.set_ylabel("Density", fontsize=12)
ax.set_xlabel("Pearson correlation r", fontsize=12)
ax.set_title(f"Average FCD histogram comparison (KS p-value = {p_hist:.3f})", fontsize=14)

ax.set_xticks(np.arange(0, 120, 20), np.arange(0, 120, 20)/100, fontsize=12)
ax.set_yticks(np.arange(0, 1600, 200), np.arange(0, 1600, 200), fontsize=12)

nmdare = ax.plot(avg_nmdare_hist, label="NMDARE patients")
nmdare_stds = np.std(nmdare_hists, axis=0)
ax.fill_between(np.arange(100), avg_nmdare_hist-nmdare_stds, avg_nmdare_hist+nmdare_stds, color="pink", alpha=0.5)

plt.legend(fontsize=11)

fig.savefig(f"{args.fcds_path}/figures/task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgFCDhistComparison_figure.png", bbox_inches="tight")

fig, ax = plt.subplots(1, 1, figsize=(14.5*cm, 8*cm), dpi=600)
hc = ax.plot(avg_hc_hist_regr, label="Healthy controls")
hc_stds = np.std(hc_hists_regr, axis=0)
ax.fill_between(np.arange(100), avg_nmdare_hist_regr-hc_stds, avg_nmdare_hist_regr+hc_stds, color="gray", alpha=0.5)
ax.set_ylabel("Density", fontsize=12)
ax.set_xlabel("Pearson correlation r", fontsize=12)
ax.set_title(f"Average FCD histogram comparison (KS p-value = {p_hist_regr:.3f})", fontsize=14)

ax.set_xticks(np.arange(0, 120, 20), np.arange(0, 120, 20)/100, fontsize=12)
ax.set_yticks(np.arange(0, 1600, 200), np.arange(0, 1600, 200), fontsize=12)

nmdare = ax.plot(avg_nmdare_hist_regr, label="NMDARE patients")
nmdare_stds = np.std(nmdare_hists_regr, axis=0)
ax.fill_between(np.arange(100), avg_nmdare_hist_regr-nmdare_stds, avg_nmdare_hist_regr+nmdare_stds, color="pink", alpha=0.5)

plt.legend(fontsize=11)

fig.savefig(f"{args.fcds_path}/figures/task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgFCDhistComparisonRegressed_figure.png", bbox_inches="tight")

# Create json sidecar
with open("resources/dynamic_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = []
for subid in args.subids:
    sources.append(f"bids:dynamic:/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCD_relmat.pkl")
    sources.append(f"bids:dynamic:/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistogram_histogram.pkl")
    sources.append(f"bids:dynamic:/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-FCDhistogramRegressed_histogram.pkl")
sidecar["Sources"] = sources

with open(os.path.join(args.fcds_path, "figures", "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgFCDcomparison_figure.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fcds_path, "figures", "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgFCDhistComparison_figure.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.fcds_path, "figures", "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-avgFCDhistComparisonRegressed_figure.json"), "w") as f:
    json.dump(sidecar, f)