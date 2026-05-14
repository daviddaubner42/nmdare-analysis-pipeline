import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
import scienceplots
import toml
import nibabel as nib
from scipy.stats import zscore
from os.path import join
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

parser = argparse.ArgumentParser(description="Denoising verification")
parser.add_argument("--derivatives_dir", type=str, help="Path to the derivatives directory")
parser.add_argument("--output_dir", type=str, help="Path to the output directory for QA plots")
args = parser.parse_args()

""" Denoising verification """

derivatives_dir = args.derivatives_dir

excluded = ["RSGK017"] # Subjects excluded in previous QC steps
subids = [i[4:] for i in os.listdir(os.path.join(derivatives_dir, "fmriprep", "sourcedata", "freesurfer")) if i.startswith("sub-") and not i[4:] in excluded]

assert len(subids) == 81 - len(excluded)

# Check if smoothing, despiking and filtering was applied
for subid in subids:
    log_dir = os.listdir(os.path.join(derivatives_dir, "xcp_d", f"sub-{subid}", "log"))[-1]

    with open(os.path.join(derivatives_dir, "xcp_d", f"sub-{subid}", "log", log_dir, "xcp_d.toml"), 'r') as f:
        log = toml.load(f)
    
    try:
        if log["workflow"]["smoothing"] != 6.0:
            print(f"sub-{subid} smoothing not applied: {log["workflow"]['smoothing']}")
    except KeyError:
        print(f"sub-{subid} no smoothing field")

    try:
        if not log["workflow"]["despike"]:
            print(f"sub-{subid} despiking not applied")
    except KeyError:
        print(f"sub-{subid} no despike field")
    
    try:
        if not log["workflow"]["bandpass_filter"]:
            print(f"sub-{subid} filtering not applied")
    except KeyError:
        print(f"sub-{subid} no filter field")

# Plot the raw vs cleaned BOLD timeseries
os.makedirs(join(derivatives_dir, "quality_control", "temp"), exist_ok=True)
for subid in subids:

    # Parcellate the raw timeseries
    os.system(f"wb_command -cifti-parcellate {derivatives_dir}/fmriprep/sub-{subid}/func/sub-{subid}_task-rest_space-fsLR_den-91k_bold.dtseries.nii {derivatives_dir}/atlases/sub-{subid}/atlas-DesikanKilliany/atlas-DesikanKilliany_space-fsLR_den-32k_dseg.dlabel.nii COLUMN {derivatives_dir}/quality_control/temp/sub-{subid}_task-rest_space-fsLR_den-32k_timeseries.ptseries.nii")

    raw_ts = np.array(nib.load(join(
        derivatives_dir,
        "quality_control",
        "temp",
        f"sub-{subid}_task-rest_space-fsLR_den-32k_timeseries.ptseries.nii"
    )).dataobj)

    clean_ts = np.array(nib.load(join(
        derivatives_dir,
        "xcp_d",
        f"sub-{subid}",
        "func",
        f"sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_stat-mean_timeseries.ptseries.nii"
    )).dataobj)

    fd_trans = np.loadtxt(f"{derivatives_dir}/quality_control/sub-{subid}/sub-{subid}_task-rest_desc-framewiseDisplacementTranslational_timeseries.tsv", delimiter='\t')

    ts_idxs = np.random.randint(0, 111, 10)

    cm = 1/2.54
    fig, (ax1, ax3) = plt.subplots(1, 2, figsize=(14.5*cm, 5*cm))
    ax1.plot(zscore(raw_ts)[:, ts_idxs], linestyle="solid", c="black", alpha=0.3, linewidth=1)
    ax1.set_ylim(-10, 10)
    ax1.set_xlabel("Slice number", fontsize=7)
    ax1.set_xticks([0, 50, 100, 150, 200, 250])
    ax1.set_xticklabels(np.arange(0, 300, 50), fontsize=7)
    ax1.set_ylabel("Z-scored BOLD", fontsize=7)
    ax1.set_yticklabels(np.arange(-10, 15, 5), fontsize=7)
    ax1.set_title("Before denoising", fontsize=7)

    ax2=ax1.twinx()
    ax2.set_ylim(0, 3)
    ax2.set_yticklabels(np.arange(0, 4, 1), fontsize=7)
    ax2.set_ylabel("Translational FD (mm)", fontsize=7)

    ax2.plot(fd_trans, c="red", alpha=0.5, linestyle="solid", linewidth=1)

    ax3.plot(zscore(clean_ts)[:, ts_idxs], linestyle="solid", c="black", alpha=0.3, linewidth=1)
    ax3.set_ylim(-10, 10)
    ax3.set_xlabel("Slice number", fontsize=7)
    ax3.set_xticks([0, 50, 100, 150, 200, 250])
    ax3.set_xticklabels(np.arange(0, 300, 50), fontsize=7)
    ax3.set_ylabel("Z-scored BOLD", fontsize=7)
    ax3.set_yticklabels(np.arange(-10, 15, 5), fontsize=7)
    ax3.set_title("After denoising", fontsize=7)

    ax4=ax3.twinx()
    ax4.set_ylim(0, 3)
    ax4.set_yticklabels(np.arange(0, 4, 1), fontsize=7)
    ax4.set_ylabel("Translational FD (mm)", fontsize=7)

    ax4.plot(fd_trans, c="red", alpha=0.5, linestyle="solid", linewidth=1)

    plt.tight_layout()

    os.makedirs(f"{args.output_dir}/sub-{subid}/figures", exist_ok=True)
    fig.savefig(f"{args.output_dir}/sub-{subid}/figures/sub-{subid}_task-rest_desc-rawVsClean_figure.png", bbox_inches="tight")

    # Create json sidecar
    with open("resources/qa_sidecar.json", "rb") as f:
        sidecar = json.load(f)

    sidecar["Sources"] = [
        f"derivatives:xcp_d:sub-{subid}/func/sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_stat-mean_timeseries.ptseries.nii",
        f"derivatives:quality_control:temp/sub-{subid}_task-rest_space-fsLR_den-32k_timeseries.ptseries.nii"
    ]

    with open(os.path.join(args.output_dir, f"{args.output_dir}/sub-{subid}/figures/sub-{subid}_task-rest_desc-rawVsClean_figure.json"), "w") as f:
        json.dump(sidecar, f)

# Delete the temporary parcellated timeseries
os.system(f"rm -rf {join(derivatives_dir, 'quality_control', 'temp')}")

# Create json sidecar
with open("resources/qa_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = []
for subid in subids:
    log_dir = os.listdir(os.path.join(derivatives_dir, "xcp_d", f"sub-{subid}", "log"))[-1]
    sources.append(f"derivatives:xcp_d:/sub-{subid}/log/{log_dir}/xcp_d.toml")
sidecar["Sources"] = sources

with open(os.path.join(args.output_dir, f"task-rest_desc-denoisingVerification_log.json"), "w") as f:
    json.dump(sidecar, f)