import nibabel as nib
import os
import json
import pydicom
from os.path import join
import pickle
import argparse

""" DICOM Metadata """
""" We save DICOM metadata about each image so that we can compare them with NIFTI metadata to make sure no changes were introduced by the conversion """

parser = argparse.ArgumentParser(description='Extract DICOM metadata')
parser.add_argument('--dicom_dir', type=str, help='Path to the DICOM directory')
parser.add_argument('--output_dir', type=str, help='Path to save the extracted metadata')
args = parser.parse_args()

dicom_path = args.dicom_dir

dicom_meta = {}

for subdir in os.listdir(dicom_path):
    if subdir != ".DS_Store" and subdir != "demographics.xlsx":
        for n in os.listdir(join(dicom_path, subdir)):
            if n != ".DS_Store":
                interdir = n
        sub_path = join(dicom_path, subdir, interdir)


        t2_found = False
        splarge = False
        for dir in os.listdir(sub_path):
            if "BOLD resting state" in dir:
                bold_path = join(sub_path, dir)
            if "MPRAGE" in dir:
                t1_path = join(sub_path, dir)
            if "t2_sp" in dir:
                d = pydicom.dcmread(join(sub_path, dir, os.listdir(join(sub_path, dir))[0]))
                x, y = d.Rows, d.Columns
                if x == 256:
                    t2_found = True
                    t2_path = join(sub_path, dir)
                else:
                    splarge = True
            if "t2_3Dsp" in dir and (splarge or not t2_found):
                t2_path = join(sub_path, dir)
        
        # Get BOLD metadata

        d = pydicom.dcmread(join(bold_path, os.listdir(bold_path)[0]))
        rt = d.RepetitionTime
        st = d.SliceThickness
        z = d["0019","100A"].value
        x, y = d.AcquisitionMatrix[0], d.AcquisitionMatrix[-1]

        for f in os.listdir(bold_path):
            d = pydicom.dcmread(join(bold_path, f))

            if d.RepetitionTime != rt:
                print(f"{subdir} BOLD rt different for {f}")
            if d.SliceThickness != st:
                print(f"{subdir} BOLD st different for {f}")
            if d["0019","100A"].value != z:
                print(f"{subdir} BOLD z different for {f}")
            if d.AcquisitionMatrix[0] != x:
                print(f"{subdir} BOLD x different for {f}")
            if d.AcquisitionMatrix[-1] != y:
                print(f"{subdir} BOLD y different for {f}")

        if 'LE' in subdir:
            nice_name = subdir[:-3]
        if 'RS' in subdir:
            if 'PROBAND' in subdir:
                nice_name = subdir
            else:
                nice_name = subdir[:10]
        nice_name = nice_name.replace("_", "")
        
        dicom_meta[nice_name] = {}
        
        dicom_meta[nice_name]["BOLD"] = {
            "x": x,
            "y": y,
            "z": z,
            "rt": rt,
            "st": st,
            "ns": len(os.listdir(bold_path))
        }

        # Get T1 metadata

        d = pydicom.dcmread(join(t1_path, os.listdir(t1_path)[0]))
        rt = d.RepetitionTime
        st = d.SliceThickness
        x, y = d.Rows, d.Columns

        for f in os.listdir(t1_path):
            d = pydicom.dcmread(join(t1_path, f))

            if d.RepetitionTime != rt:
                print(f"{subdir} T1 rt different for {f}")
            if d.SliceThickness != st:
                print(f"{subdir} T1 st different for {f}")
            if d.Rows != x:
                print(f"{subdir} T1 x different for {f}")
            if d.Columns != y:
                print(f"{subdir} T1 y different for {f}")
        
        dicom_meta[nice_name]["T1"] = {
            "x": x,
            "y": y,
            "z": len(os.listdir(t1_path)),
            "rt": rt,
            "st": st
        }

        # Get T2 metadata

        d = pydicom.dcmread(join(t2_path, os.listdir(t2_path)[0]))
        rt = d.RepetitionTime
        st = d.SliceThickness
        x, y = d.Rows, d.Columns

        for f in os.listdir(t2_path):
            d = pydicom.dcmread(join(t2_path, f))

            if d.RepetitionTime != rt:
                print(f"{subdir} T2 rt different for {f}")
            if d.SliceThickness != st:
                print(f"{subdir} T2 st different for {f}")
            if d.Rows != x:
                print(f"{subdir} T2 x different for {f}")
            if d.Columns != y:
                print(f"{subdir} T2 y different for {f}")
        
        dicom_meta[nice_name]["T2"] = {
            "x": x,
            "y": y,
            "z": len(os.listdir(t2_path)),
            "rt": rt,
            "st": st
        }

with open(os.path.join(args.output_dir, "desc-dicomMetadata_summary.pkl"), "wb") as f:
    pickle.dump(dicom_meta, f)

# Create json sidecar
with open("resources/qa_sidecar.json", "rb") as f:
    sidecar = json.load(f)

sidecar["Sources"] = [f"{args.dicom_dir}"]

with open(os.path.join(args.output_dir, f"desc-dicomMetadata_summary.json"), "w") as f:
    json.dump(sidecar, f)
with open(os.path.join(args.output_dir, f"desc-getDicomMetadata_log.json"), "w") as f:
    json.dump(sidecar, f)