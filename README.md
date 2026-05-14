# BIDS-TO-FC-GRAPH

Snakemake pipeline to create static, dynamic and graph theory derivatives from raw BIDS data.

## Key features

- **BIDS in / BIDS out** All the produced derivatives are stored in the BIDS format, ensuring further interoperability with other pipelines.
- **Modular design** Thanks to the use of Snakemake, the pipeline is built out of smaller subcomponents that can be modified, excluded or exchanged for other implementations without the need to modify the whole pipeline.

## Installation

Download the code:

```bash
git clone [LINK]
```

Prepare a conda environment with Snakemake:

```bash
conda create -n snake snakemake
conda activate snake
```

Specify input and root directories in `config/config.yaml`, launch a terminal in the `rootdir` specified in the `config/config.yaml`, and run

```bash
snakemake --cores all --sdm apptainer conda --singularity-args="--cleanenv -B $DATADIR:$DATADIR -B $ROOTDIR:$ROOTDIR"
```
(or whatever the desired number of cores is). The singularity arguments clear environmental variables and bind the data and pipeline directories into the container, to avoid naming conflicts inside the containers.

To run using SLURM, first install the SLURM executor for Snakemake:

```bash
conda install snakemake-executor-plugin-slurm
```

And then when running specify SLURM as the executor:

```bash
snakemake --cores all --sdm apptainer conda --executor slurm --singularity-args="--cleanenv -B $DATADIR:$DATADIR -B $ROOTDIR:$ROOTDIR"
```

## Citation

[INSERT WHEN READY]

Copyright © Charité Universitätsmedizin Berlin