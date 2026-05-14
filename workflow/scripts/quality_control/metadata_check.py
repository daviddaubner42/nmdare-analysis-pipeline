import nibabel as nib
import os
import json
import pydicom
from os.path import join
import pickle
import argparse

""" NIFTI Metadata """
""" We get NIFTI metadata to compare with DICOM, and to check consistency across subjects """

parser = argparse.ArgumentParser(description='Check metadata consistency in the BIDS dataset.')
parser.add_argument('--dicom_meta', type=str, required=True, help='Path to the DICOM metadata file.')
parser.add_argument('--bids_dir', type=str, required=True, help='Path to the BIDS dataset directory.')
parser.add_argument('--output_dir', type=str, required=True, help='Path to the output directory for QA results.')
args = parser.parse_args()

rawdir = args.bids_dir

with open(args.dicom_meta, 'rb') as f:
    dicom_meta = pickle.load(f)

subids = [subid[4:] for subid in os.listdir(rawdir) if subid.startswith("sub-")]

assert len(subids) == 81

# Check if files exist
for subid in subids:
    try:
        assert os.path.exists(os.path.join(
            rawdir,
            f"sub-{subid}",
            "anat",
            f"sub-{subid}_T1w.nii.gz"
        ))
        assert os.path.exists(os.path.join(
            rawdir,
            f"sub-{subid}",
            "anat",
            f"sub-{subid}_T2w.nii.gz"
        ))

        assert os.path.exists(os.path.join(
            rawdir,
            f"sub-{subid}",
            "func",
            f"sub-{subid}_task-rest_bold.nii.gz"
        ))

        assert os.path.exists(os.path.join(
            rawdir,
            f"sub-{subid}",
            "fmap",
            f"sub-{subid}_magnitude1.nii.gz"
        ))
        assert os.path.exists(os.path.join(
            rawdir,
            f"sub-{subid}",
            "fmap",
            f"sub-{subid}_magnitude2.nii.gz"
        ))
        assert os.path.exists(os.path.join(
            rawdir,
            f"sub-{subid}",
            "fmap",
            f"sub-{subid}_phasediff.nii.gz"
        ))
    except AssertionError:
        print(f"sub-{subid} - files missing.")
print("All files present.")

t1_size = (176, 256, 256)
t1_tr = 1.9
t2_sizes = (176, 256, 256)
t2_tr = 6
bold_size = (64, 64, 37, 260)
bold_tr = 2.25
bold_slice_thickness = 3.4

for subid in subids:
    t1 = nib.load(os.path.join(
        rawdir,
        f"sub-{subid}",
        "anat",
        f"sub-{subid}_T1w.nii.gz"
    ))
    t2 = nib.load(os.path.join(
        rawdir,
        f"sub-{subid}",
        "anat",
        f"sub-{subid}_T2w.nii.gz"
    ))
    bold = nib.load(os.path.join(
        rawdir,
        f"sub-{subid}",
        "func",
        f"sub-{subid}_task-rest_bold.nii.gz"
    ))

    with open(os.path.join(
        rawdir,
        f"sub-{subid}",
        "func",
        f"sub-{subid}_task-rest_bold.json"
    )) as f:
        bold_info = json.load(f)
    
    with open(os.path.join(
        rawdir,
        f"sub-{subid}",
        "anat",
        f"sub-{subid}_T1w.json"
    )) as f:
        t1_info = json.load(f)

    with open(os.path.join(
        rawdir,
        f"sub-{subid}",
        "anat",
        f"sub-{subid}_T2w.json"
    )) as f:
        t2_info = json.load(f)

    # Check if metadata are consistent across subjects
    print(f"sub-{subid}:")

    if t1.dataobj.shape != t1_size:
        print(f"T1w size not matching: {t1.dataobj.shape}")
    if t1_info["RepetitionTime"] != t1_tr:
        print(f"T1 TR not matching: {t1_info["RepetitionTime"]}")

    if t2.dataobj.shape != t2_sizes:
        print(f"T2w size not matching: {t2.dataobj.shape}")
    if t2_info["RepetitionTime"] != t2_tr:
        print(f"T2 TR not matching: {t2_info["RepetitionTime"]}")

    if bold.dataobj.shape != bold_size:
        print(f"BOLD size not matching: {bold.dataobj.shape}")
    if bold_info["RepetitionTime"] != bold_tr:
        print(f"BOLD TR not matching: {bold_info["RepetitionTime"]}")
    if bold_info["SliceThickness"] != bold_slice_thickness:
        print(f"BOLD slice thickness not matching: {bold_info["SliceThickness"]}")
    
    # Check consistency with DICOM

    z = t1.dataobj.shape[0]
    x = t1.dataobj.shape[1]
    y = t1.dataobj.shape[2]
    rt = t1_info["RepetitionTime"] * 1000
    st = t1_info["SliceThickness"]
    if x != dicom_meta[subid]["T1"]["x"]:
        print(f"T1 x not same, NIFTI {x} != DICOM {dicom_meta[subid]["T1"]["x"]}")
    if y != dicom_meta[subid]["T1"]["y"]:
        print(f"T1 y not same, NIFTI {y} != DICOM {dicom_meta[subid]["T1"]["y"]}")
    if z != dicom_meta[subid]["T1"]["z"]:
        print(f"T1 z not same, NIFTI {z} != DICOM {dicom_meta[subid]["T1"]["z"]}")
    if rt != dicom_meta[subid]["T1"]["rt"]:
        print(f"T1 rt not same, NIFTI {rt} != DICOM {dicom_meta[subid]["T1"]["rt"]}")
    if st != dicom_meta[subid]["T1"]["st"]:
        print(f"T1 st not same, NIFTI {st} != DICOM {dicom_meta[subid]["T1"]["st"]}")
    

    z = t2.dataobj.shape[0]
    x = t2.dataobj.shape[1]
    y = t2.dataobj.shape[2]
    rt = t2_info["RepetitionTime"] * 1000
    st = t2_info["SliceThickness"]
    if x != dicom_meta[subid]["T2"]["x"]:
        print(f"T2 x not same, NIFTI {x} != DICOM {dicom_meta[subid]["T2"]["x"]}")
    if y != dicom_meta[subid]["T2"]["y"]:
        print(f"T2 y not same, NIFTI {y} != DICOM {dicom_meta[subid]["T2"]["y"]}")
    if z != dicom_meta[subid]["T2"]["z"]:
        print(f"T2 z not same, NIFTI {z} != DICOM {dicom_meta[subid]["T2"]["z"]}")
    if rt != dicom_meta[subid]["T2"]["rt"]:
        print(f"T2 rt not same, NIFTI {rt} != DICOM {dicom_meta[subid]["T2"]["rt"]}")
    if st != dicom_meta[subid]["T2"]["st"]:
        print(f"T2 st not same, NIFTI {st} != DICOM {dicom_meta[subid]["T2"]["st"]}")

    z = bold.dataobj.shape[2]
    x = bold.dataobj.shape[0]
    y = bold.dataobj.shape[1]
    rt = bold_info["RepetitionTime"] * 1000
    st = bold_info["SliceThickness"]
    if x != dicom_meta[subid]["BOLD"]["x"]:
        print(f"bold x not same, NIFTI {x} != DICOM {dicom_meta[subid]["BOLD"]["x"]}")
    if y != dicom_meta[subid]["BOLD"]["y"]:
        print(f"bold y not same, NIFTI {y} != DICOM {dicom_meta[subid]["BOLD"]["y"]}")
    if z != dicom_meta[subid]["BOLD"]["z"]:
        print(f"bold z not same, NIFTI {z} != DICOM {dicom_meta[subid]["BOLD"]["z"]}")
    if rt != dicom_meta[subid]["BOLD"]["rt"]:
        print(f"bold rt not same, NIFTI {rt} != DICOM {dicom_meta[subid]["BOLD"]["rt"]}")
    if abs(st - dicom_meta[subid]["BOLD"]["st"]) > 0.00001:
        print(f"bold st not same, NIFTI {st} != DICOM {dicom_meta[subid]["BOLD"]["st"]}")

# Create json sidecar
with open("resources/qa_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sources = [f"derivatives:quality_control:/desc-dicomMetadata_summary.pkl"]
for subid in subids:
    sources.append(os.path.join(
        rawdir,
        f"sub-{subid}",
        "anat",
        f"sub-{subid}_T1w.nii.gz"
    ))
    sources.append(os.path.join(
        rawdir,
        f"sub-{subid}",
        "anat",
        f"sub-{subid}_T2w.nii.gz"
    ))
    sources.append(os.path.join(
        rawdir,
        f"sub-{subid}",
        "func",
        f"sub-{subid}_task-rest_bold.nii.gz"
    ))

sidecar["Sources"] = sources

with open(os.path.join(args.output_dir, f"desc-metadataCheck_log.json"), "w") as f:
    json.dump(sidecar, f)