import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
import scienceplots
from scipy.stats import pearsonr
import pickle
import nibabel as nib
import argparse
import json

# Plotting settings

matplotlib.rcParams.update(matplotlib.rcParamsDefault)
plt.style.use(['ieee'])

plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "stix"
})

cm = 1/2.54

parser = argparse.ArgumentParser(description="QC-FC correlation")
parser.add_argument("--motion_summary", type=str, help="Path to the motion summary CSV file"),
parser.add_argument("--atlas_csv", type=str, help="Path to the atlas CSV file containing ROI labels"),
parser.add_argument("--atlas_img", type=str, help="Path to the atlas image file"),
parser.add_argument("--network_labels", type=str, help="Path to the pickle file containing network labels"),
parser.add_argument("--fc_dir", type=str, help="Path to the FC directory containing participant FC matrices"),
parser.add_argument("--output_dir", type=str, help="Path to the output directory")
args = parser.parse_args()

""" QC-FC correlation """

output_dir = args.output_dir
fc_dir = args.fc_dir

subids = [i[4:] for i in os.listdir(fc_dir) if i.startswith("sub-")]

motion = pd.read_csv(args.motion_summary, sep='\t')
fds_df_trans = motion[["subid", "mean_fd_trans"]]
fds_df_rot = motion[["subid", "mean_fd_rot"]]

subid_order = []

all_fcs = []

# Get all participant FC matrices
for subid in subids:
    fc = np.loadtxt(os.path.join(args.fc_dir, f"sub-{subid}", f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"), delimiter='\t')
    all_fcs.append(fc)
    subid_order.append(subid)
all_fcs = np.array(all_fcs)

# Get FD values for each participant
fds_trans = []
fds_rot = []
for subid in subid_order:
    fds_trans.append(fds_df_trans[fds_df_trans['subid'] == subid].mean_fd_trans.item())
    fds_rot.append(fds_df_rot[fds_df_rot['subid'] == subid].mean_fd_rot.item())

# Calculate FD-FC correlations for each pair of ROIs
corrs_trans = np.zeros_like(all_fcs[0])
ps_trans = np.zeros_like(all_fcs[0])
corrs_rot = np.zeros_like(all_fcs[0])
ps_rot = np.zeros_like(all_fcs[0])

n = len(corrs_trans)

for i in range(n):
    for j in range(n):
        res = pearsonr(all_fcs[:, i, j], fds_trans)
        corrs_trans[i, j] = res.statistic
        ps_trans[i, j] = res.pvalue

        res = pearsonr(all_fcs[:, i, j], fds_rot)
        corrs_rot[i, j] = res.statistic
        ps_rot[i, j] = res.pvalue

# Calculate summary FD-FC correlation statistics
print(f"QC-FC correlations median translational FD = {np.nanmedian(np.abs(corrs_trans))}")
print(f"QC-FC correlations median rotational FD = {np.nanmedian(np.abs(corrs_rot))}")

# Plot the results
trans_hist = np.histogram(corrs_trans[~np.isnan(corrs_trans)], 100)
rot_hist = np.histogram(corrs_rot[~np.isnan(corrs_rot)], 100)

fig, ax = plt.subplots(1, 2, figsize=(14.5*cm, 5*cm), dpi=600, sharey=True)
ax[0].plot(trans_hist[1][:-1], trans_hist[0], label="translation FD-FC corr")
ax[0].fill_between(trans_hist[1][:-1], trans_hist[0], alpha=0.7)
ax[0].set_xticks([-0.6, -0.3, 0,np.nanmedian(np.abs(corrs_trans)), 0.3, 0.6], labels=[-0.6, -0.3, 0, f"{np.nanmedian(np.abs(corrs_trans)):.2f}", 0.3, 0.6], fontsize=9)
ax[0].set_yticks(range(0, 250, 50), labels=range(0, 250, 50), fontsize=9)
ax[0].set_ylabel("Density", fontsize=9)
ax[0].set_xlabel("Pearson correlation $r$", fontsize=9)
ax[0].set_title("Translation mean FD-FC correlation", fontsize=9)
ax[0].vlines(np.nanmedian(np.abs(corrs_trans)), 0, 210, colors='red', linestyles='dashed', lw=1)
# ax[0].set_ylim(0, 240)
ax[1].plot(rot_hist[1][:-1], rot_hist[0], label="rotation FD-FC corr")
ax[1].fill_between(rot_hist[1][:-1], rot_hist[0], alpha=0.7)
ax[1].set_xticks([-0.6, -0.3, 0, np.nanmedian(np.abs(corrs_rot)), 0.3, 0.6], labels=[-0.6, -0.3, 0, f"{np.nanmedian(np.abs(corrs_rot)):.2f}", 0.3, 0.6], fontsize=9)
# ax[1].set_ylim(0, 240)
ax[1].set_xlabel("Pearson correlation $r$", fontsize=9)
ax[1].set_title("Rotation mean FD-FC correlation", fontsize=9)
ax[1].vlines(np.nanmedian(np.abs(corrs_rot)), 0, 210, colors='red', linestyles='dashed', lw=1)

fig.savefig(f"{args.output_dir}/figures/task-rest_desc-qcFcCorrelationHistograms_figure.png", bbox_inches="tight")

""" QC-FC distance dependency """

# Transform region labels to format compatible with atlas containing ROI centroid coordinates
with open(args.network_labels, "rb") as f:
    network_labels = pickle.load(f)

network_labels[np.where(network_labels == 'LEFT-THALAMUS-PROPER')] = 'lh_thalamusproper'
network_labels[np.where(network_labels == 'RIGHT-THALAMUS-PROPER')] = 'rh_thalamusproper'
network_labels[np.where(network_labels == 'LEFT-CAUDATE')] = 'lh_caudate'
network_labels[np.where(network_labels == 'RIGHT-CAUDATE')] = 'rh_caudate'
network_labels[np.where(network_labels == 'LEFT-PUTAMEN')] = 'lh_putamen'
network_labels[np.where(network_labels == 'RIGHT-PUTAMEN')] = 'rh_putamen'
network_labels[np.where(network_labels == 'LEFT-PALLIDUM')] = 'lh_pallidum'
network_labels[np.where(network_labels == 'RIGHT-PALLIDUM')] = 'rh_pallidum'
network_labels[np.where(network_labels == 'LEFT-HIPPOCAMPUS')] = 'lh_hippocampus'
network_labels[np.where(network_labels == 'RIGHT-HIPPOCAMPUS')] = 'rh_hippocampus'
network_labels[np.where(network_labels == 'LEFT-AMYGDALA')] = 'lh_amygdala'
network_labels[np.where(network_labels == 'RIGHT-AMYGDALA')] = 'rh_amygdala'
network_labels[np.where(network_labels == 'LEFT-ACCUMBENS-AREA')] = 'lh_accumbensarea'
network_labels[np.where(network_labels == 'RIGHT-ACCUMBENS-AREA')] = 'rh_accumbensarea'


nifti_dk_labels = pd.read_csv(args.atlas_csv)
nifti_dk_labels.set_index('id', inplace=True)
nifti_dk_labels.drop(list(nifti_dk_labels[(nifti_dk_labels['label'] == 'caudalmiddlefrontal') | (nifti_dk_labels['label'] == 'brainstem')].index), inplace=True)

# Get centroid coordinates for each ROI
dk = nib.load(args.atlas_img)

dk_labels = dk.get_fdata()
dk_affine = dk.affine

centroids_full = {}
centroids = {}
to_delete = []
for i, label in enumerate(network_labels):
    if '_' in label:
        hem, name = label.split('_')
        if name in list(nifti_dk_labels['label']):
            if hem == 'lh':
                id = nifti_dk_labels[(nifti_dk_labels['label'] == name) & (nifti_dk_labels['hemisphere'] == 'L')].index.item()
            elif hem == 'rh':
                id = nifti_dk_labels[(nifti_dk_labels['label'] == name) & (nifti_dk_labels['hemisphere'] == 'R')].index.item()
            else:
                raise ValueError("Not lh or rh")
            
            where = np.where(dk_labels == id)
            xs = []
            ys = []
            zs = []
            for x, y, z in zip(where[0], where[1], where[2]):
                xs.append(x)
                ys.append(y)
                zs.append(z)
            centroids[label] = (np.mean(xs), np.mean(ys), np.mean(zs))
    else:
        to_delete.append(i)
    if hem == 'lh':
        id = nifti_dk_labels[(nifti_dk_labels['label'] == name) & (nifti_dk_labels['hemisphere'] == 'L')].index.item()
    elif hem == 'rh':
        id = nifti_dk_labels[(nifti_dk_labels['label'] == name) & (nifti_dk_labels['hemisphere'] == 'R')].index.item()
    else:
        raise ValueError("Not lh or rh")
    
    where = np.where(dk_labels == id)
    xs = []
    ys = []
    zs = []
    for x, y, z in zip(where[0], where[1], where[2]):
        xs.append(x)
        ys.append(y)
        zs.append(z)
    centroids_full[label] = (np.mean(xs), np.mean(ys), np.mean(zs))

coords = []
for x, y, z in list(centroids_full.values()):
    coords.append([x, y, z])
coords = np.array(coords)

# Calculate correlations between QC-FC values and distance between ROIs

centre_corrs = []
for cor in list(centroids.values()):
    centre_corrs.append(np.array([cor[0], cor[1], cor[2]]))

corrs_trans_cropped = np.delete(corrs_trans, to_delete, 0)
corrs_trans_cropped = np.delete(corrs_trans_cropped, to_delete, 1)

corrs_rot_cropped = np.delete(corrs_rot, to_delete, 0)
corrs_rot_cropped = np.delete(corrs_rot_cropped, to_delete, 1)

dist = np.zeros_like(corrs_trans_cropped)

N = corrs_trans_cropped.shape[0]
for i in range(N):
    for j in range(N):
        dist[i, j] = np.linalg.norm(centre_corrs[i] - centre_corrs[j])

from scipy.stats import pearsonr

res = pearsonr(
    dist[np.triu_indices_from(dist, k=1)], 
    corrs_trans_cropped[np.triu_indices_from(corrs_trans_cropped, k=1)]
)
dist_corr_trans = res.statistic
dist_p_trans = res.pvalue

res = pearsonr(
    dist[np.triu_indices_from(dist, k=1)],
    corrs_rot_cropped[np.triu_indices_from(corrs_rot_cropped, k=1)]
)
dist_corr_rot = res.statistic
dist_p_rot = res.pvalue

print(f"QC-FC distance correlation translational FD: {dist_corr_trans}")
print(f"QC-FC distance correlation p-value translational FD: {dist_p_trans}")
print(f"QC-FC distance correlation rotational FD: {dist_corr_rot}")
print(f"QC-FC distance correlation p-value rotational FD: {dist_p_rot}")

# Plot the results
fig, ax = plt.subplots(1, 2, figsize=(14.5*cm,7*cm), dpi=600)

ax[0].scatter(dist[np.triu_indices_from(dist, k=1)], 
    corrs_trans_cropped[np.triu_indices_from(corrs_trans_cropped, k=1)], s=1)
ax[0].set_xlabel("Distance between regions", fontsize=10)
ax[0].set_ylabel("Translational mean FD-FC correlation", fontsize=10)
ax[0].tick_params(labelsize=10)

ax[1].scatter(dist[np.triu_indices_from(dist, k=1)], 
    corrs_rot_cropped[np.triu_indices_from(corrs_rot_cropped, k=1)], s=1)
ax[1].set_xlabel("Distance between regions", fontsize=10)
ax[1].set_ylabel("Rotational mean FD-FC correlation", fontsize=10)
ax[1].tick_params(labelsize=10)

plt.tight_layout()

fig.savefig(f"{output_dir}/figures/task-rest_desc-qcFcDistanceCorrelation_figure.png", bbox_inches="tight")

# Create json sidecar
with open("resources/qa_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = ["derivatives:quality_control:/motion_summary.csv", "resources/atlas-desikankilliany.csv", "resources/atlas-desikankilliany.nii.gz", "resources/network_labels.pkl"]
for subid in subids:
    sources.append(f"{args.fc_dir}/sub-{subid}/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv")
sidecar["Sources"] = sources

with open(os.path.join(args.output_dir, "figures", "task-rest_desc-qcFcCorrelationHistograms_figure.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.output_dir, "figures", "task-rest_desc-qcFcDistanceCorrelation_figure.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.output_dir, "task-rest_desc-qcFc_log.json"), "w") as f:
    json.dump(sidecar, f)