import nibabel as nib
import os
import json
import argparse

parser = argparse.ArgumentParser(description='Create BIDS filter file')
parser.add_argument('--bids_dir', type=str, help='Path to the BIDS dataset directory')
parser.add_argument('--subid', type=str, help='The subid for which to create the filter file')
parser.add_argument('--output_path', type=str, help='Path to save the filter file')
args = parser.parse_args()

filter = {
  "fmap": {"datatype": "fmap"},
  "bold": {"datatype": "func", "suffix": "bold"},
  "sbref": {"datatype": "func", "suffix": "sbref"},
  "flair": {"datatype": "anat", "suffix": "FLAIR"},
  "t2w": {"datatype": "anat", "suffix": "T2w"},
  "t1w": {"datatype": "anat", "suffix": "T1w"},
  "roi": {"datatype": "anat", "suffix": "roi"}
}

t2_options = []
for f in os.listdir(os.path.join(args.bids_dir, f"sub-{args.subid}", "anat")):
    print(f)
    if "T2" in f and not ".json" in f:
        t2_options.append(f)

good_options = []
for f in t2_options:
    t2 = nib.load(os.path.join(args.bids_dir, f"sub-{args.subid}", "anat", f))
    with open(os.path.join(args.bids_dir, f"sub-{args.subid}", "anat", f.replace(".nii.gz", ".json")), "r") as j:
        t2_header = json.load(j)
    if t2.dataobj.shape[1] == 256 and t2_header["RepetitionTime"] == 6.0:
        good_options.append(f)

if len(good_options) == 1:
    final = good_options[0]
elif len(good_options) == 0:
    for f in t2_options:
        t2 = nib.load(os.path.join(args.bids_dir, f"sub-{args.subid}", "anat", f))
        if t2.dataobj.shape[1] == 256:
            final = f
elif len(good_options) > 1:
    for f in good_options:
        if "acq-SPACE" in f:
            final = f

if "acq-3DSPACE" in final:
    filter["t2w"]["acquistion"] = "3DSPACE"
elif "acq-SPACE" in final:
    filter["t2w"]["acquistion"] = "SPACE"

with open(args.output_path, "w") as f:
    json.dump(filter, f, indent=4)