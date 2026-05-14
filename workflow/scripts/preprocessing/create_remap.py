import nibabel as nib
import argparse

parser = argparse.ArgumentParser(description="Create remap from label file.")
parser.add_argument("-input", type=str, help="Path to the label GIFTI file")
parser.add_argument("-output", type=str, help="Path to the label GIFTI file")
args = parser.parse_args()

rh = nib.load(args.input)

og_keys = rh.labeltable.get_labels_as_dict().keys()

with open(args.output, 'w') as f:
    for key in og_keys:
        f.write(f"{key} {key+len(og_keys)}\n")