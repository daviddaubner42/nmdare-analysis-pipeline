import matplotlib.pyplot as plt
import matplotlib
import pickle
import scienceplots
import os
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Plot the results of the pairwise FC comparison")
parser.add_argument("--fc_dir", type=str, help="The path to the raw FC directory")
parser.add_argument("--subids", type=str, nargs='+', help="All the subids to be included")
parser.add_argument("--demo_data_path", type=str, help="Path to the demographic data")
parser.add_argument("--network_dir", type=str, help="Path to the directory with network information")
args = parser.parse_args()

# Plotting settings
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
plt.style.use(['ieee'])
plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif"
})

cm = 1/2.54

# Calculate average FC matrix for each group (with regressed confounds)
demo_data = pd.read_csv(args.demo_data_path)

nmdare_fcs_regr = []
hc_fcs_regr = []
for subid in args.subids:
    fc = np.loadtxt(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_FC_regr.csv"), delimiter=',')
    if demo_data[demo_data["ID"] == subid]["nmdare"].item() == 1:
        nmdare_fcs_regr.append(fc)
    else:
        hc_fcs_regr.append(fc)

avg_nmdare_fc = np.mean(nmdare_fcs_regr, axis=0)
avg_hc_fc = np.mean(hc_fcs_regr, axis=0)

# Load network information
with open(os.path.join(args.network_dir, "networks.pkl"), "rb") as f:
    networks = pickle.load(f)
with open(os.path.join(args.network_dir, "network_names.pkl"), "rb") as f:
    network_names = pickle.load(f)

# Plot the average FC matrices for each group, with network boundaries
fig, ax = plt.subplots(1, 2, figsize=(14.5*cm,8.96*cm), dpi=600)
hc = ax[0].imshow(avg_hc_fc, cmap="viridis", vmin=-0.2, vmax=0.8)
ax[0].set_title("Healthy Controls", fontsize=7)
nmdare = ax[1].imshow(avg_nmdare_fc, cmap="viridis", vmin=-0.2, vmax=0.8)
ax[1].set_title("NMDARE Patients", fontsize=7)

n = len(avg_nmdare_fc)

start = 0
end = 0
region_centers = []
for network in networks:
    end += len(network)
    if end < 84:
        ax[0].hlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[0].vlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[1].hlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[1].vlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
    region_centers.append(start + (end-start)/2)
    start = end
ax[0].set_yticks(region_centers, network_names, fontsize=7)
ax[0].set_xticks(region_centers, network_names, fontsize=7, rotation=90)
ax[1].set_yticks([])
ax[1].set_xticks(region_centers, network_names, fontsize=7, rotation=90)

ax[0].tick_params(length = 0)
ax[1].tick_params(length = 0)

for part in ['bottom', 'left', 'right', 'top']:
    ax[0].spines[part].set_linewidth(0.2)
    ax[1].spines[part].set_linewidth(0.2)

cbar = fig.colorbar(hc, ax=ax, orientation='vertical', shrink=0.6)
cbar.set_label('Pearson correlation $r$', fontsize=7)
cbar.ax.set_yticks([-0.2, 0.0, 0.8])
cbar.ax.tick_params(labelsize=7, length=0)
cbar.outline.set_linewidth(0.1)

fig.savefig(os.path.join(args.fc_dir, "images", "avg_fc_comparison.png"), bbox_inches='tight')

# Plot the significant differences between the average FC matrices, with network boundaries
with open(os.path.join(args.fc_dir, "p_vals.csv"), "rb") as f:
    p_vals = np.loadtxt(f, delimiter=',')
with open(os.path.join(args.fc_dir, "stats.csv"), "rb") as f:
    stats = np.loadtxt(f, delimiter=',')
with open(os.path.join(args.fc_dir, "p_vals_fdr.csv"), "rb") as f:    
    p_vals_fdr = np.loadtxt(f, delimiter=',')

fig, ax = plt.subplots(1, 2, figsize=(14.5*cm,8.96*cm), dpi=600)
hc = ax[0].imshow(avg_hc_fc, cmap="viridis", vmin=-0.2, vmax=0.8)
ax[0].set_title("Healthy Controls", fontsize=7)
nmdare = ax[1].imshow(avg_nmdare_fc, cmap="viridis", vmin=-0.2, vmax=0.8)
ax[1].set_title("NMDARE Patients", fontsize=7)

n = len(avg_nmdare_fc)

start = 0
end = 0
region_centers = []
for network in networks:
    end += len(network)
    if end < 84:
        ax[0].hlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[0].vlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[1].hlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[1].vlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
    region_centers.append(start + (end-start)/2)
    start = end
ax[0].set_yticks(region_centers, network_names, fontsize=7)
ax[0].set_xticks(region_centers, network_names, fontsize=7, rotation=90)
# ax[1].set_yticks(region_centers, network_names, fontsize=3)
ax[1].set_yticks([])
ax[1].set_xticks(region_centers, network_names, fontsize=7, rotation=90)

for i in range(p_vals.shape[0]):
    for j in range(p_vals.shape[1]):
        if p_vals[i, j] < 0.001:
            if stats[i, j] > 0:
                ax[0].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='red', linewidth=0.5))
                ax[1].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='red', linewidth=0.5))
            if stats[i, j] < 0:
                ax[0].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='cyan', linewidth=0.5))
                ax[1].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='cyan', linewidth=0.5))

ax[0].tick_params(length = 0)
ax[1].tick_params(length = 0)

for part in ['bottom', 'left', 'right', 'top']:
    ax[0].spines[part].set_linewidth(0.2)
    ax[1].spines[part].set_linewidth(0.2)

cbar = fig.colorbar(hc, ax=ax, orientation='vertical', shrink=0.6)
cbar.set_label('Pearson correlation $r$', fontsize=7)
cbar.ax.set_yticks([-0.2, 0.0, 0.8])
cbar.ax.tick_params(labelsize=7, length=0)
cbar.outline.set_linewidth(0.1)

fig.savefig(os.path.join(args.fc_dir, "images", "p_vals_uncorrected.png"), bbox_inches='tight')

# Plot the corrected p-values
fig, ax = plt.subplots(1, 2, figsize=(14.5*cm,8.96*cm), dpi=600)
hc = ax[0].imshow(avg_hc_fc, cmap="viridis", vmin=-0.2, vmax=0.8)
ax[0].set_title("Healthy Controls", fontsize=7)
nmdare = ax[1].imshow(avg_nmdare_fc, cmap="viridis", vmin=-0.2, vmax=0.8)
ax[1].set_title("NMDARE Patients", fontsize=7)

n = len(avg_nmdare_fc)

start = 0
end = 0
region_centers = []
for network in networks:
    end += len(network)
    if end < 84:
        ax[0].hlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[0].vlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[1].hlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
        ax[1].vlines(end-0.5, 0, n-0.5, colors="white", linewidth=0.15)
    region_centers.append(start + (end-start)/2)
    start = end
ax[0].set_yticks(region_centers, network_names, fontsize=7)
ax[0].set_xticks(region_centers, network_names, fontsize=7, rotation=90)
# ax[1].set_yticks(region_centers, network_names, fontsize=3)
ax[1].set_yticks([])
ax[1].set_xticks(region_centers, network_names, fontsize=7, rotation=90)

for i in range(p_vals.shape[0]):
    for j in range(p_vals.shape[1]):
        if p_vals_fdr[i, j] < 0.05:
            if stats[i, j] > 0:
                ax[0].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='red', linewidth=0.5))
                ax[1].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='red', linewidth=0.5))
            if stats[i, j] < 0:
                ax[0].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='cyan', linewidth=0.5))
                ax[1].add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='cyan', linewidth=0.5))

ax[0].tick_params(length = 0)
ax[1].tick_params(length = 0)

for part in ['bottom', 'left', 'right', 'top']:
    ax[0].spines[part].set_linewidth(0.2)
    ax[1].spines[part].set_linewidth(0.2)

cbar = fig.colorbar(hc, ax=ax, orientation='vertical', shrink=0.6)
cbar.set_label('Pearson correlation $r$', fontsize=7)
cbar.ax.set_yticks([-0.2, 0.0, 0.8])
cbar.ax.tick_params(labelsize=7, length=0)
cbar.outline.set_linewidth(0.1)

fig.savefig(os.path.join(args.fc_dir, "images", "p_vals_fdr.png"), bbox_inches='tight')