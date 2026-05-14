import nibabel as nib
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Create remap from label file.")
parser.add_argument("-atlas_file", type=str, help="Path to the label GIFTI file")
parser.add_argument("-output", type=str, help="Path to the label GIFTI file")
args = parser.parse_args()

atlas = nib.load(args.atlas_file)
axes = [atlas.header.get_axis(i) for i in range(atlas.ndim)]

label_dict = axes[0].label[0]

label_df = pd.DataFrame({"index": [], "label": []})

for i, t in label_dict.items():
    if i > 0:
        label_df.loc[i] = [i, t[0]]

label_df.to_csv(args.output, sep='\t', index=False)