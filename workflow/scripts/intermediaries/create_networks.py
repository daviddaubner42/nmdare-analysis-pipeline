import os

import pandas as pd
import numpy as np
import pickle
import argparse

parser = argparse.ArgumentParser(description="Create the files describing ROIs and networks they belong to")
parser.add_argument("--seg_file", type=str, help="The path to the atlas segmentation file")
parser.add_argument("--out_dir", type=str, help="Path to directory where results should be stored")
args = parser.parse_args()

# Specify networks of interest and the regions which will not be included in the analysis
network_names = ["DMN", "DAN", "SAN", "AUD", "VIS", "other", "SUBCORT", "CEREBELLUM"]
excluded_regions = ['lh_caudalmiddlefrontal', 'rh_caudalmiddlefrontal'] # For these 2 regions, there was insufficient coverage to get mean BOLD signal in parcellation

atlas_desc = pd.read_csv(args.seg_file, sep='\t')
atlas_labels = list(atlas_desc['label'])
atlas_desc['index'] = np.arange(0, len(atlas_desc))

# Get regions belonging to each network
idxs_to_keep = []
networks = []
for network in network_names:
    cur_nodes = []
    nodes = atlas_desc[atlas_desc['network'] == network]
    for i in range(len(nodes)):
        if not nodes.iloc[i]['label'] in excluded_regions:
            cur_nodes.append(nodes.iloc[i]['label'])
            idxs_to_keep.append(nodes.iloc[i]['index'])
    networks.append(cur_nodes)

# Get indices of all regions that do not belong to regions of interest and delete them from the label list
to_delete_network = []
for i in atlas_desc['index']:
    if i not in idxs_to_keep:
        to_delete_network.append(i)
network_labels = np.delete(atlas_labels, to_delete_network, 0)

# Create a partition excluding the other network, to be used for participation coefficient calculation
partition = []
for i, n in enumerate(networks):
    if network_names[i] != "other":
        partition.append(set(n))

to_delete_partition = []
for idx, node in enumerate(network_labels):
    if atlas_desc[atlas_desc['label'] == node]['network'].item() == 'other':
        to_delete_partition.append(idx)
partition_labels = np.delete(network_labels, to_delete_partition, 0)

# Save the results
outdir = args.out_dir
os.makedirs(outdir, exist_ok=True)

with open(f'{outdir}/networks.pkl', 'wb') as f:
    pickle.dump(networks, f)
with open(f'{outdir}/network_names.pkl', 'wb') as f:
    pickle.dump(network_names, f)
with open(f'{outdir}/partition.pkl', 'wb') as f:
    pickle.dump(partition, f)
with open(f'{outdir}/to_delete_network.pkl', 'wb') as f:
    pickle.dump(to_delete_network, f)
with open(f'{outdir}/to_delete_partition.pkl', 'wb') as f:
    pickle.dump(to_delete_partition, f)
with open(f'{outdir}/network_labels.pkl', 'wb') as f:
    pickle.dump(network_labels, f)
with open(f'{outdir}/partition_labels.pkl', 'wb') as f:
    pickle.dump(partition_labels, f)
