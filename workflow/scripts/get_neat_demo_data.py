import pandas as pd
import os
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Transform an excel file into a neat demographics pandas table")
parser.add_argument("--input_file", type=str, help="The path to the file to be transformed")
parser.add_argument("--output_file", type=str, help="Path where the resulting file should be stored")
args = parser.parse_args()

demo_data = pd.read_excel(args.input_file)

neat_subids = []
for id in demo_data["ID"]:
    if id.startswith("RS_GK") or id.startswith("LE_GK"):
        neat_subids.append(id[:9].replace("_", ""))
    elif id.startswith("LE-GK"):
        neat_subids.append(id[:9].replace("-", ""))
    elif id.startswith("rs_gk"):
        neat_subids.append("RSGK" + id[6:])
    elif id.startswith("LE_U"):
        neat_subids.append("LEUNKNOWN" + id[11:14])
    elif id.startswith("LE_"):
        if id[3:] in ["18", "96", "150", "153", "162", "163"]:
            if len(id[3:]) == 3:
                neat_subids.append("LEOVERLAP" + id[3:])
            else:
                neat_subids.append("LEOVERLAP0" + id[3:])
        else:
            if id[3:] == "126":
                neat_subids.append("LENDMA" + id[3:])
            elif len(id[3:]) == 3:
                neat_subids.append("LENMDA" + id[3:])
            elif id[3:] in ["32", "33"]:
                neat_subids.append("LENDMA0" + id[3:])
            else:
                neat_subids.append("LENMDA0" + id[3:])
    else:
        neat_subids.append("PROBANDRS" + id[11:])

demo_data["ID"] = neat_subids
demo_data = demo_data.rename(columns={"group (nmdare=1;controls=0)": "nmdare"})

demo_data.to_csv(args.output_file, index=False)