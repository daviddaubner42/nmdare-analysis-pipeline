import numpy as np
import networkx as nx
from networkx_robustness import networkx_robustness
import pickle
from nilearn import datasets, image, plotting
import nibabel as nib
import os
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Plot ROIs with significant local metric differences")
parser.add_argument("--res_dir", type=str, help="The path to the local metric results directory")
parser.add_argument("--metric", type=str, help="The metric to be plotted")
parser.add_argument("--atlas_img", type=str, help="Path to the atlas img")
args = parser.parse_args()

