import matplotlib.pyplot as plt
import matplotlib
import pickle
import scienceplots
import os
import json
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Plot the comparison of global metrics between NMDARE patients and healthy controls")
parser.add_argument("--global_metrics_dir", type=str, help="The path to the directory with the global metric data to be plotted")
args = parser.parse_args()

# Plotting settings
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
plt.style.use(['ieee'])
plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif"
})

cm = 1/2.54

# Load the global metrics data
graph_props = pd.read_table(os.path.join(args.global_metrics_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetrics_relmat.tsv"))
with open(os.path.join(args.global_metrics_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetricPvals_relmat.pkl"), "rb") as f:
    ps = pickle.load(f)
with open(os.path.join(args.global_metrics_dir, "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetricStats.pkl"), "rb") as f:
    stats = pickle.load(f)

fig, ax = plt.subplots(4, 2, figsize=(14.5*cm, 20*cm), dpi=600)

nmdares = []
hcs = []

metric = 'abs_mean_connectivity'

for subid in graph_props["subid"]:
        if graph_props[graph_props["subid"] == subid].NMDARE.item() == 1:
            nmdares.append(graph_props[graph_props["subid"] == subid][metric].item())
        else:
            hcs.append(graph_props[graph_props["subid"] == subid][metric].item())

nmdare_idxs = 2*np.ones(len(nmdares))
hc_idxs = np.ones(len(hcs))
idxs = np.concatenate([hc_idxs, nmdare_idxs])

ax[0][0].violinplot([hcs, nmdares], showmeans=True, showextrema=False)
ax[0][0].scatter(idxs, np.concatenate([hcs, nmdares]), s=3, color=(0, 0, 0, 0.2))
ax[0][0].tick_params(labelsize=9)
ax[0][0].set_xticks([1, 2], ["Healthy Controls", "NMDARE Patients"], fontsize=9)
ax[0][0].set_ylabel("Abs. mean connectivity $u_c$", fontsize=9)


if ps[metric] < 0.05:
    ymax = max(np.max(nmdares), np.max(hcs))
    y_offset = ymax / 10
    ax[0][0].plot([1, 1, 2, 2], [ymax, ymax + y_offset, ymax + y_offset, ymax], color='black')
    ax[0][0].set_facecolor("#eeebeb")
    ax[0][0].text(1.5, ymax + y_offset + 0.1, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 10:
    ax[0][0].text(1.5, ymax + y_offset + 0.2, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 100:
    ax[0][0].text(1.5, ymax + y_offset + 0.3, '*', fontsize=16, ha='center')


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

nmdares = []
hcs = []

metric = 'avg_clustering'

for subid in graph_props["subid"]:
        if graph_props[graph_props["subid"] == subid].NMDARE.item() == 1:
            nmdares.append(graph_props[graph_props["subid"] == subid][metric].item())
        else:
            hcs.append(graph_props[graph_props["subid"] == subid][metric].item())

nmdare_idxs = 2*np.ones(len(nmdares))
hc_idxs = np.ones(len(hcs))
idxs = np.concatenate([hc_idxs, nmdare_idxs])

ax[0][1].violinplot([hcs, nmdares], showmeans=True, showextrema=False)
ax[0][1].scatter(idxs, np.concatenate([hcs, nmdares]), s=3, color=(0, 0, 0, 0.2))
ax[0][1].tick_params(labelsize=9)
ax[0][1].set_xticks([1, 2], ["Healthy Controls", "NMDARE Patients"], fontsize=9)
ax[0][1].set_ylabel("Avg. clustering coefficient $C$", fontsize=9)

if ps[metric] < 0.05:
    ymax = max(np.max(nmdares), np.max(hcs))
    y_offset = ymax / 10
    ax[0][1].plot([1, 1, 2, 2], [ymax, ymax + y_offset, ymax + y_offset, ymax], color='black')
    ax[0][1].set_facecolor("#eeebeb")
    ax[0][1].text(1.5, ymax + y_offset + ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 10:
    ax[0][1].text(1.5, ymax + y_offset + 2*ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 100:
    ax[0][1].text(1.5, ymax + y_offset + 3*ymax/50, '*', fontsize=16, ha='center')

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

nmdares = []
hcs = []

metric = 'modularity'

for subid in graph_props["subid"]:
        if graph_props[graph_props["subid"] == subid].NMDARE.item() == 1:
            nmdares.append(graph_props[graph_props["subid"] == subid][metric].item())
        else:
            hcs.append(graph_props[graph_props["subid"] == subid][metric].item())

nmdare_idxs = 2*np.ones(len(nmdares))
hc_idxs = np.ones(len(hcs))
idxs = np.concatenate([hc_idxs, nmdare_idxs])

violin = ax[1][0].violinplot([hcs, nmdares], showmeans=(True), showextrema=False)
ax[1][0].scatter(idxs, np.concatenate([hcs, nmdares]), s=3, color=(0, 0, 0, 0.2))
ax[1][0].tick_params(labelsize=9)
ax[1][0].set_xticks([1, 2], ["Healthy Controls", "NMDARE Patients"], fontsize=9)
ax[1][0].set_ylabel("Modularity $M$", fontsize=9)

ymax = max(np.max(nmdares), np.max(hcs))

# ax[1][0].set_ylim(top = ymax + 2.5*ymax/10)

if ps[metric] < 0.05:
    ymax = max(np.max(nmdares), np.max(hcs))
    y_offset = ymax / 10
    ax[1][0].plot([1, 1, 2, 2], [ymax, ymax + y_offset, ymax + y_offset, ymax], color='black')
    ax[1][0].set_facecolor("#eeebeb")
    ax[1][0].text(1.5, ymax + y_offset + ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 10:
    ax[1][0].text(1.5, ymax + y_offset + 2*ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 100:
    ax[1][0].text(1.5, ymax + y_offset + 3*ymax/50, '*', fontsize=16, ha='center')


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


nmdares = []
hcs = []

metric = 'global_efficiency'

for subid in graph_props["subid"]:
        if graph_props[graph_props["subid"] == subid].NMDARE.item() == 1:
            nmdares.append(graph_props[graph_props["subid"] == subid][metric].item())
        else:
            hcs.append(graph_props[graph_props["subid"] == subid][metric].item())

nmdare_idxs = 2*np.ones(len(nmdares))
hc_idxs = np.ones(len(hcs))
idxs = np.concatenate([hc_idxs, nmdare_idxs])

violin = ax[1][1].violinplot([hcs, nmdares], showmeans=(True), showextrema=False)
ax[1][1].scatter(idxs, np.concatenate([hcs, nmdares]), s=3, color=(0, 0, 0, 0.2))
ax[1][1].tick_params(labelsize=9)
ax[1][1].set_xticks([1, 2], ["Healthy Controls", "NMDARE Patients"], fontsize=9)
ax[1][1].set_ylabel("Global efficiency $E$", fontsize=9)

if ps[metric] < 0.05:
    ymax = max(np.max(nmdares), np.max(hcs))
    y_offset = ymax / 10
    ax[1][1].plot([1, 1, 2, 2], [ymax, ymax + y_offset, ymax + y_offset, ymax], color='black')
    ax[1][1].set_facecolor("#eeebeb")
    ax[1][1].text(1.5, ymax + y_offset + ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 10:
    ax[1][1].text(1.5, ymax + y_offset + 2*ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 100:
    ax[1][1].text(1.5, ymax + y_offset + 3*ymax/50, '*', fontsize=16, ha='center')


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

nmdares = []
hcs = []

metric = 'assortativity'

for subid in graph_props["subid"]:
        if graph_props[graph_props["subid"] == subid].NMDARE.item() == 1:
            nmdares.append(graph_props[graph_props["subid"] == subid][metric].item())
        else:
            hcs.append(graph_props[graph_props["subid"] == subid][metric].item())

nmdare_idxs = 2*np.ones(len(nmdares))
hc_idxs = np.ones(len(hcs))
idxs = np.concatenate([hc_idxs, nmdare_idxs])

ax[3][0].violinplot([hcs, nmdares], showmeans=True, showextrema=False)
ax[3][0].scatter(idxs, np.concatenate([hcs, nmdares]), s=3, color=(0, 0, 0, 0.2))
ax[3][0].tick_params(labelsize=9)
ax[3][0].set_xticks([1, 2], ["Healthy Controls", "NMDARE Patients"], fontsize=9)
ax[3][0].set_ylabel("Assortativity $r$", fontsize=9)

if ps[metric] < 0.05:
    ymax = max(np.max(nmdares), np.max(hcs))
    y_offset = ymax / 10
    ax[3][0].plot([1, 1, 2, 2], [ymax, ymax + y_offset, ymax + y_offset, ymax], color='black')
    ax[3][0].set_facecolor("#eeebeb")
    ax[3][0].text(1.5, ymax + y_offset + ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 10:
    ax[3][0].text(1.5, ymax + y_offset + 2*ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 100:
    ax[3][0].text(1.5, ymax + y_offset + 3*ymax/50, '*', fontsize=16, ha='center')


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


nmdares = []
hcs = []

metric = 'robustness_random'

for subid in graph_props["subid"]:
        if graph_props[graph_props["subid"] == subid].NMDARE.item() == 1:
            nmdares.append(graph_props[graph_props["subid"] == subid][metric].item())
        else:
            hcs.append(graph_props[graph_props["subid"] == subid][metric].item())

nmdare_idxs = 2*np.ones(len(nmdares))
hc_idxs = np.ones(len(hcs))
idxs = np.concatenate([hc_idxs, nmdare_idxs])

ax[2][0].violinplot([hcs, nmdares], showmeans=True, showextrema=False)
ax[2][0].scatter(idxs, np.concatenate([hcs, nmdares]), s=3, color=(0, 0, 0, 0.2))
ax[2][0].tick_params(labelsize=9)
ax[2][0].set_xticks([1, 2], ["Healthy Controls", "NMDARE Patients"], fontsize=9)
ax[2][0].set_ylabel(r"Robustness $R_{random}$", fontsize=9)
ax[2][0].set_ylim(32.5, 41.5)

if ps[metric] < 0.05:
    ymax = max(np.max(nmdares), np.max(hcs))
    y_offset = ymax / 10
    ax[2][0].plot([1, 1, 2, 2], [ymax, ymax + y_offset, ymax + y_offset, ymax], color='black')
    ax[2][0].set_facecolor("#eeebeb")
    ax[2][0].text(1.5, ymax + y_offset + ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 10:
    ax[2][0].text(1.5, ymax + y_offset + 2*ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 100:
    ax[2][0].text(1.5, ymax + y_offset + 3*ymax/50, '*', fontsize=16, ha='center')


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


nmdares = []
hcs = []

metric = 'robustness_targeted'

for subid in graph_props["subid"]:
        if graph_props[graph_props["subid"] == subid].NMDARE.item() == 1:
            nmdares.append(graph_props[graph_props["subid"] == subid][metric].item())
        else:
            hcs.append(graph_props[graph_props["subid"] == subid][metric].item())

nmdare_idxs = 2*np.ones(len(nmdares))
hc_idxs = np.ones(len(hcs))
idxs = np.concatenate([hc_idxs, nmdare_idxs])

ax[2][1].violinplot([hcs, nmdares], showmeans=True, showextrema=False)
ax[2][1].scatter(idxs, np.concatenate([hcs, nmdares]), s=3, color=(0, 0, 0, 0.2))
ax[2][1].tick_params(labelsize=9)
ax[2][1].set_xticks([1, 2], ["Healthy Controls", "NMDARE Patients"], fontsize=9)
ax[2][1].set_ylabel(r"Robustness $R_{targeted}$", fontsize=9)
ax[2][1].set_ylim(32.5, 41.5)

if ps[metric] < 0.05:
    ymax = max(np.max(nmdares), np.max(hcs))
    y_offset = ymax / 10
    ax[2][1].plot([1, 1, 2, 2], [ymax, ymax + y_offset, ymax + y_offset, ymax], color='black')
    ax[2][1].set_facecolor("#eeebeb")
    ax[2][1].text(1.5, ymax + y_offset + ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 10:
    ax[2][1].text(1.5, ymax + y_offset + 2*ymax/50, '*', fontsize=16, ha='center')
if ps[metric] < 0.05 / 100:
    ax[2][1].text(1.5, ymax + y_offset + 3*ymax/50, '*', fontsize=16, ha='center')

ax[3][1].axis('off')

plt.tight_layout()

fig.savefig(os.path.join(args.global_metrics_dir, "figures", "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetricComparison_figure.png"), bbox_inches='tight')

# Create json sidecar
with open("resources/graph_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [
     "bids:graph_theory/global:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetrics_relmat.tsv",
     "bids:graph_theory/global:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetricPvals_relmat.pkl",
     "bids:graph_theory/global:task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetricStats.pkl"
]

with open(os.path.join(args.global_metrics_dir, "figures", "task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-globalMetricComparison_figure.json"), "w") as f:
    json.dump(sidecar, f)