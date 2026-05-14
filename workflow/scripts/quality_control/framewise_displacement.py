import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
import scienceplots
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

parser = argparse.ArgumentParser(description='Calculate framewise displacement from fmriprep confounds')
parser.add_argument('--derivatives_dir', type=str, required=True, help='Path to the derivatives directory')
parser.add_argument('--output_dir', type=str, required=True, help='Path to the output directory where results will be saved')
args = parser.parse_args()

""" Framewise displacement """

derivatives_dir = args.derivatives_dir

subids = [i[4:] for i in os.listdir(os.path.join(derivatives_dir, "fmriprep", "sourcedata", "freesurfer")) if i.startswith("sub-")]

assert len(subids) == 81

max_fds_trans = {}
mean_fds_trans = {}
pct_over_soft_trans = {}
pct_over_hard_trans = {}
max_fds_rot = {}
mean_fds_rot = {}
pct_over_soft_rot = {}
pct_over_hard_rot = {}

# Calculate framewise displacement based on motion confounds calculated by fmriprep
for subid in subids:
    confounds = pd.read_csv(os.path.join(
        derivatives_dir,
        "fmriprep",
        f"sub-{subid}",
        "func",
        f"sub-{subid}_task-rest_desc-confounds_timeseries.tsv"
    ), sep='\t')

    trans_x = confounds["trans_x"]
    trans_y = confounds["trans_y"]
    trans_z = confounds["trans_z"]

    rot_x = confounds["rot_x"]
    rot_y = confounds["rot_y"]
    rot_z = confounds["rot_z"]

    n_slices = len(trans_x)

    fd_trans = np.array([math.sqrt(float(x) ** 2 + float(y) ** 2 + float(z) ** 2) for x, y, z in zip(trans_x, trans_y, trans_z)])
    fd_rot = np.array([math.sqrt(float(x) ** 2 + float(y) ** 2 + float(z) ** 2) for x, y, z in zip(rot_x, rot_y, rot_z)])

    os.makedirs(f"{args.output_dir}/sub-{subid}/figures", exist_ok=True)

    fig, ax = plt.subplots(1, 2, figsize=(14.5*cm, 5*cm))

    ax[0].plot(range(len(fd_trans)), fd_trans)
    ax[0].set_title("REST Framewise Displacement Translation", fontsize=7)
    ax[0].set_xlabel('frames number', fontsize=7)
    ax[0].set_ylabel('translation (in mm)', fontsize=7)
    ax[0].axhline(y=1.5, color='r', linestyle='--')  
    ax[0].axhline(y=3, color='r', linestyle='-')

    ax[1].plot(range(len(fd_rot)), fd_rot)
    ax[1].set_title("REST Framewise Displacement Rotation", fontsize=7)
    ax[1].set_xlabel('frames number', fontsize=7)
    ax[1].set_ylabel('rotation (in degrees)', fontsize=7)
    ax[1].axhline(y=1.5, color='r', linestyle='--')  
    ax[1].axhline(y=3, color='r', linestyle='-')

    fig.savefig(f"{args.output_dir}/sub-{subid}/figures/sub-{subid}_task-rest_desc-framewiseDisplacement_figure.png", bbox_inches="tight")
    plt.close()

    np.savetxt(f"{args.output_dir}/sub-{subid}/sub-{subid}_task-rest_desc-framewiseDisplacementTranslational_timeseries.tsv", fd_trans, delimiter='\t')
    np.savetxt(f"{args.output_dir}/sub-{subid}/sub-{subid}_task-rest_desc-framewiseDisplacementRotational_timeseries.tsv", fd_rot, delimiter='\t')

    # Create json sidecar
    with open("resources/qa_sidecar.json", "rb") as f:
        sidecar = json.load(f)

    sidecar["Sources"] = [f"derivatives:fmriprep:sub-{subid}/func/sub-{subid}_task-rest_desc-confounds_timeseries.tsv"]

    with open(os.path.join(args.output_dir, f"sub-{subid}/sub-{subid}_task-rest_desc-framewiseDisplacementTranslational_timeseries.json"), "w") as f:
        json.dump(sidecar, f)
    with open(os.path.join(args.output_dir, f"sub-{subid}/sub-{subid}_task-rest_desc-framewiseDisplacementRotational_timeseries.json"), "w") as f:
        json.dump(sidecar, f)
    with open(os.path.join(args.output_dir, f"sub-{subid}/figures/sub-{subid}_task-rest_desc-framewiseDisplacement_figure.json"), "w") as f:
        json.dump(sidecar, f)


    max_fds_trans[subid] = np.max(fd_trans)
    mean_fds_trans[subid] = np.mean(fd_trans)
    pct_over_soft_trans[subid] = len(np.where(fd_trans > 1.5)) / len(fd_trans)
    pct_over_hard_trans[subid] = len(np.where(fd_trans > 3)) / len(fd_trans)
    max_fds_rot[subid] = np.max(fd_rot)
    mean_fds_rot[subid] = np.mean(fd_rot)
    pct_over_soft_rot[subid] = len(np.where(fd_rot > 1.5)) / len(fd_rot)
    pct_over_hard_rot[subid] = len(np.where(fd_rot > 3)) / len(fd_rot)

    if np.max(fd_trans) >= 3:
        print(f"sub-{subid} translational framewise displacement {np.max(fd_trans):.2f} crossed the 3mm treshold and should be excluded.")
    elif np.max(fd_trans) >= 1.5:
        print(f"sub-{subid} translational framewise displacement {np.max(fd_trans):.2f} crossed the 1.5mm treshold and should be inspected.")
    
    if np.max(fd_rot) >= 3:
        print(f"sub-{subid} rotational framewise displacement {np.max(fd_rot):.2f} crossed the 3 degree treshold and should be excluded.")
    elif np.max(fd_rot) >= 1.5:
        print(f"sub-{subid} rotational framewise displacement {np.max(fd_rot):.2f} crossed the 1.5 degree treshold and should be inspected.")

subids = list(mean_fds_trans.keys())
pd.DataFrame({
    "subid": subids,
    "max_fd_trans": list(max_fds_trans.values()),
    "max_fd_rot": list(max_fds_rot.values()), 
    "mean_fd_trans": list(mean_fds_trans.values()),
    "mean_fd_rot": list(mean_fds_rot.values()),
    "pct_over_soft_trans": list(pct_over_soft_trans.values()),
    "pct_over_hard_trans": list(pct_over_hard_trans.values()),
    "pct_over_soft_rot": list(pct_over_soft_rot.values()),
    "pct_over_hard_rot": list(pct_over_hard_rot.values())
}).to_csv(f"{args.output_dir}/task-rest_desc-framewiseDisplacement_summary.tsv", index=False, sep='\t')

fig, ax = plt.subplots(1, 1, figsize=(7.25*cm, 5*cm))
ax.scatter(list(max_fds_trans.values()), list(max_fds_rot.values()), s=1)
# ax.set_title("Max FD", fontsize=7)
ax.set_xlim(0, 3.5)
ax.set_xlabel("Max. translation FD (mm)", fontsize=7)
ax.set_xticklabels([0, 1, 2, 3], fontsize=7)
ax.set_ylim(0, 0.1)
ax.set_ylabel("Max. rotation FD (degrees)", fontsize=7)
ax.set_yticklabels(np.arange(0, 0.06, 0.01), fontsize=7)
ax.vlines([1.5, 3], 0, 0.099, "red", linestyles=["dashed", "solid"], lw=1)
os.makedirs(os.path.join(args.output_dir, "figures"), exist_ok=True)
fig.savefig(f"{args.output_dir}/figures/task-rest_desc-maxFramewiseDisplacementScatter_figure.png", bbox_inches="tight")
plt.close()

# Create json sidecar
with open("resources/qa_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = []
for subid in subids:
    sources.append(f"derivatives:fmriprep:sub-{subid}/func/sub-{subid}_task-rest_desc-confounds_timeseries.tsv")

sidecar["Sources"] = sources

with open(os.path.join(args.output_dir, f"task-rest_desc-framewiseDisplacement_summary.json"), "w") as f:
    json.dump(sidecar, f)

with open(os.path.join(args.output_dir, f"figures/task-rest_desc-maxFramewiseDisplacementScatter_figure.json"), "w") as f:
    json.dump(sidecar, f)

with open(os.path.join(args.output_dir, f"task-rest_desc-framewiseDisplacement_log.json"), "w") as f:
    json.dump(sidecar, f)