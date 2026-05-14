# """ This file contains rules used to preprocess the raw MRI data in BIDS format to produce a cleaned average timeseries for each ROI """

# derivatives_dir = os.path.join(outdir, "derivatives")

 # Create a bids filter file for each subject, to be used in the fMRIPrep workflow
rule create_bids_filter_file:
    input:
        os.path.join(rawdir, "sub-{subid}", "anat", "sub-{subid}_T1w.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "fmap", "sub-{subid}_magnitude1.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "fmap", "sub-{subid}_magnitude2.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "fmap", "sub-{subid}_phasediff.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "func", "sub-{subid}_task-rest_bold.nii.gz")
    params:
        rawdir=rawdir,
        outdir=outdir
    output:
        os.path.join(outdir, "derivatives", "temp", "sub-{subid}_bidsfilter.json")
    conda:
        os.path.join(environmentdir, "environment.yaml")
    shell:
        "mkdir -p {params.outdir}/derivatives/temp && "
        "python {workflowdir}/scripts/preprocessing/create_bids_filter_file.py --bids_dir {params.rawdir} --subid {wildcards.subid} --output_file {output}"

# Apply fMRIPrep preprocessing pipeline to the data
# https://fmriprep.org/en/stable/
rule fmriprep:
    input:
        filter=os.path.join(outdir, "derivatives", "temp", "sub-{subid}_bidsfilter.json"),
        os.path.join(rawdir, "sub-{subid}", "anat", "sub-{subid}_T1w.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "anat", "sub-{subid}_T2w.nii.gz"), # comment out if your data does not contain T2
        os.path.join(rawdir, "sub-{subid}", "fmap", "sub-{subid}_magnitude1.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "fmap", "sub-{subid}_magnitude2.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "fmap", "sub-{subid}_phasediff.nii.gz"),
        os.path.join(rawdir, "sub-{subid}", "func", "sub-{subid}_task-rest_bold.nii.gz")
    params:
        bids_dir=rawdir,
        out_dir=derivatives_dir,
        fs_license_dir=resourcedir
    threads: 8
    resources:
        mem='16G',
        time='12:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer",
            "sub-{subid}",
            "mri",
            "aseg.mgz"
        ),
        os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer",
            "sub-{subid}",
            "label",
            "lh.aparc.annot"
        ),
        os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer",
            "sub-{subid}",
            "label",
            "rh.aparc.annot"
        ),
        os.path.join(
            derivatives_dir,
            "fmriprep",
            "sub-{subid}",
            "func",
            "sub-{subid}_task-rest_space-fsLR_den-91k_bold.dtseries.nii"
        ),
        os.path.join(
            outdir, 
            "derivatives", 
            "fmriprep", 
            "sub-{subid}", 
            "func", 
            "sub-{subid}_task-rest_desc-confounds_timeseries.tsv"
        )
    container:
        config["containers"]["fmriprep"]
    shell:
        "rm -rf {params.out_dir}/fmriprep/sourcedata/freesurfer/sub-{wildcards.subid} && "
        "fmriprep "
        "{params.bids_dir} {params.out_dir}/fmriprep participant "
        "--fs-license-file {params.fs_license_dir}/license.txt "
        "--skip-bids-validation "
        "--participant_label {wildcards.subid} "
        "--output-spaces MNI152NLin2009cAsym:res-2 fsLR "
        "--cifti-output "
        "--skip-bids-validation "
        "--nthreads 16 "
        "--omp-nthreads 16"
        "--bids-filter-file {input.filter}"

# Register the FreeSurfer subcortical segmentation into the MNI space and convert it to Nifti
rule register_subcortical_segmentation:
    input:
        os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer",
            "sub-{subid}",
            "mri",
            "aseg.mgz"
        )
    params:
        conversion_dir= os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "subcortical"
        ),
        fs_dir=os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer"
        ),
        resource_dir=resourcedir
    threads: 8
    resources:
        mem='32G',
        time='12:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "subcortical",
            "aseg_space-MNI152NonLin_res-2mm.nii.gz"
        )
    container:
        config["containers"]["freesurfer"]
    shell:
        "export FS_LICENSE={params.resource_dir}/license.txt && "
        "mkdir -p {params.conversion_dir} && "
        "export SUBJECTS_DIR={params.fs_dir} && "
        "mri_cvs_register --mov sub-{wildcards.subid} --mni && "
        "mri_convert {params.fs_dir}/sub-{wildcards.subid}/cvs/final_CVSmorphed_tocvs_avg35_inMNI152_aseg.mgz {output}"

# Convert the subcortical segmentation into a label volume, and resample it into the 2mm resolution
rule prepare_subcortical_segmentation_for_merging:
    input:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "subcortical",
            "aseg_space-MNI152NonLin_res-2mm.nii.gz"
        )
    params:
        conversion_dir= os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "subcortical"
        ),
        resource_dir=resourcedir
    threads: 8
    resources:
        mem='1G',
        time='1:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "subcortical",
            "aseg_space-MNI152NLin2009cAsym_res-2mm_dseg.nii.gz"
        )
    container:
        config["containers"]["wb_command"]
    shell:
        "wb_command -volume-label-import "
        "{input} "
        "{params.resource_dir}/FreeSurferAllLut.txt "
        "{params.conversion_dir}/aseg_space-MNI152NonLin_res-2mm_label.nii.gz "
        "-drop-unused-labels && "
        "wb_command -volume-resample "
        "{params.conversion_dir}/aseg_space-MNI152NonLin_res-2mm_label.nii.gz "
        "{params.resource_dir}/MNI152_T1_2mm.nii.gz "
        "ENCLOSING_VOXEL "
        "{output}"

# Convert the FreeSurfer aparc cortical parcellation into the Gifti format
rule convert_aparc_to_gifti:
    input:
        lh=os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer",
            "sub-{subid}",
            "label",
            "lh.aparc.annot"
        ),
        rh=os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer",
            "sub-{subid}",
            "label",
            "rh.aparc.annot"
        )
    params:
        conversion_dir=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical"
        ),
        resource_dir=resourcedir,
        fs_dir=os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer"
        )
    threads: 8
    resources:
        mem='1G',
        time='1:00:00'
    output:
        lh=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "lh.aparc.gii"
        ),
        rh=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "rh.aparc.gii"
        )
    container:
        config["containers"]["freesurfer"]
    shell:
        "export FS_LICENSE={params.resource_dir}/license.txt && "
        "mris_convert --annot {input.lh} "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/lh.midthickness "
        "{output.lh} && "
        "mris_convert --annot {input.rh} "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/rh.midthickness "
        "{output.rh}"

# Resample the cortical parcellation onto the fsLR space
rule resample_cortical_labels:
    input:
        lh=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "lh.aparc.gii"
        ),
        rh=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "rh.aparc.gii"
        )
    params:
        conversion_dir=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical"
        ),
        resource_dir=resourcedir,
        fs_dir=os.path.join(
            derivatives_dir,
            "fmriprep",
            "sourcedata",
            "freesurfer"
        ),
        workflow_dir=workflowdir
    threads: 8
    resources:
        mem='4G',
        time='1:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "aparc.rh.32k_fs_LR.label.gii"
        ),
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "aparc.lh.32k_fs_LR.label.gii"
        )
    container:
        config["containers"]["wb_command"]
    shell:
        "mkdir -p {params.conversion_dir} && "

        "{params.workflow_dir}/scripts/intermediaries/wb_shortcuts.sh -freesurfer-resample-prep "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/lh.white "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/lh.pial "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/lh.sphere.reg "
        "{params.resource_dir}/spheres/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii "
        "{params.conversion_dir}/lh.midthickness.surf.gii "
        "{params.conversion_dir}/lh.midthickness.32k_fs_LR.surf.gii "
        "{params.conversion_dir}/lh.sphere.reg.surf.gii && "

        "{params.workflow_dir}/scripts/intermediaries/wb_shortcuts.sh -freesurfer-resample-prep "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/rh.white "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/rh.pial "
        "{params.fs_dir}/sub-{wildcards.subid}/surf/rh.sphere.reg "
        "{params.resource_dir}/spheres/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii "
        "{params.conversion_dir}/rh.midthickness.surf.gii "
        "{params.conversion_dir}/rh.midthickness.32k_fs_LR.surf.gii "
        "{params.conversion_dir}/rh.sphere.reg.surf.gii && "

        "wb_command -label-resample "
        "{input.lh} "
        "{params.conversion_dir}/lh.sphere.reg.surf.gii "
        "{params.resource_dir}/spheres/fs_LR-deformed_to-fsaverage.L.sphere.32k_fs_LR.surf.gii "
        "ADAP_BARY_AREA "
        "{params.conversion_dir}/aparc.lh.32k_fs_LR.label.gii "
        "-area-surfs "
        "{params.conversion_dir}/lh.midthickness.surf.gii "
        "{params.conversion_dir}/lh.midthickness.32k_fs_LR.surf.gii && "

        "wb_command -label-resample "
        "{input.rh} "
        "{params.conversion_dir}/rh.sphere.reg.surf.gii "
        "{params.resource_dir}/spheres/fs_LR-deformed_to-fsaverage.R.sphere.32k_fs_LR.surf.gii "
        "ADAP_BARY_AREA "
        "{params.conversion_dir}/aparc.rh.32k_fs_LR.label.gii "
        "-area-surfs "
        "{params.conversion_dir}/rh.midthickness.surf.gii "
        "{params.conversion_dir}/rh.midthickness.32k_fs_LR.surf.gii"

# Create a remap of the right hemisphere label keys so they don't clash with the left hemisphere ones
rule generate_remap:
    input:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "aparc.rh.32k_fs_LR.label.gii"
        )
    params:
        conversion_dir=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical"
        ),
        workflow_dir=workflowdir
    threads: 8
    resources:
        mem='1G',
        time='1:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "remap.txt"
        )
    conda:
        os.path.join(
            environmentdir,
            "environment.yaml"
        )
    shell:
        "python {params.workflow_dir}/scripts/intermediaries/create_remap.py "
        "-input {params.conversion_dir}/aparc.rh.32k_fs_LR.label.gii "
        "-output {params.conversion_dir}/remap.txt"

# Apply the remap to the right hemisphere keys, and add the hemisphere prefixes to the labels
rule fix_cortical_labels:
    input:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "remap.txt"
        ),
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "aparc.rh.32k_fs_LR.label.gii"
        ),
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "aparc.lh.32k_fs_LR.label.gii"
        )
    params:
        conversion_dir=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical"
        )
    threads: 8
    resources:
        mem='1G',
        time='1:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "rh_seg-aparc_den-32k_fs_LR.label.gii"
        ),
        os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "lh_seg-aparc_den-32k_fs_LR.label.gii"
        )
    container:
        config["containers"]["wb_command"]
    shell:
        "wb_command -label-modify-keys {params.conversion_dir}/aparc.rh.32k_fs_LR.label.gii "
        "{params.conversion_dir}/remap.txt "
        "{params.conversion_dir}/aparc.rh.32k_fs_LR.label.gii && "

        "wb_command -gifti-label-add-prefix "
        "{params.conversion_dir}/aparc.lh.32k_fs_LR.label.gii "
        "lh_ "
        "{params.conversion_dir}/lh_seg-aparc_den-32k_fs_LR.label.gii && "

        "wb_command -gifti-label-add-prefix "
        "{params.conversion_dir}/aparc.rh.32k_fs_LR.label.gii "
        "rh_ "
        "{params.conversion_dir}/rh_seg-aparc_den-32k_fs_LR.label.gii"
    
# Combine the subcortical and cortical atlases into a Cifti atlas
rule combine_into_cifti_label:
    input:
        rh=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "rh_seg-aparc_den-32k_fs_LR.label.gii"
        ),
        lh=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "cortical",
            "lh_seg-aparc_den-32k_fs_LR.label.gii"
        ),
        vol=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}",
            "subcortical",
            "aseg_space-MNI152NLin2009cAsym_res-2mm_dseg.nii.gz"
        )
    params:
        conversion_dir=os.path.join(
            derivatives_dir,
            "conversion",
            "sub-{subid}"
        ),
        resource_dir=resourcedir,
        workflow_dir=workflowdir,
        out_dir=derivatives_dir
    threads: 8
    resources:
        mem='4G',
        time='1:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany",
            "atlas-DesikanKilliany_space-fsLR_den-32k_dseg.dlabel.nii"
        )
    container:
        config["containers"]["wb_command"]
    shell:
        "wb_command -cifti-create-label "
        "{params.conversion_dir}/cortical/aparc.32k_fs_LR.dlabel.nii "
        "-left-label {input.lh} "
        "-right-label {input.rh} && "

        "mkdir -p {params.out_dir}/atlases/sub-{wildcards.subid}/atlas-DesikanKilliany && "

        "wb_command -cifti-create-dense-from-template {params.resource_dir}/91282_Greyordinates.dscalar.nii "
        "{params.out_dir}/atlases/sub-{wildcards.subid}/atlas-DesikanKilliany/atlas-DesikanKilliany_space-fsLR_den-32k_dseg.dlabel.nii "
        "-volume-all {input.vol} "
        "-cifti {params.conversion_dir}/cortical/aparc.32k_fs_LR.dlabel.nii "
        "-label-collision SURFACES_FIRST"

# Create additional atlas files required by XCP-D
rule create_atlas_info:
    input:
        os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany",
            "atlas-DesikanKilliany_space-fsLR_den-32k_dseg.dlabel.nii"
        )
    params:
        resource_dir=resourcedir,
        workflow_dir=workflowdir,
        out_dir=derivatives_dir
    threads: 8
    resources:
        mem='1G',
        time='1:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany",
            "atlas-DesikanKilliany_dseg.tsv"
        ),
        os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany",
            "dataset_description.json"
        )
    conda:
        os.path.join(
            environmentdir,
            "environment.yaml"
        )
    shell:
        "python {params.workflow_dir}/scripts/intermediaries/create_atlas_info.py "
        "-atlas_file {params.out_dir}/atlases/sub-{wildcards.subid}/atlas-DesikanKilliany/atlas-DesikanKilliany_space-fsLR_den-32k_dseg.dlabel.nii "
        "-output {params.out_dir}/atlases/sub-{wildcards.subid}/atlas-DesikanKilliany/atlas-DesikanKilliany_dseg.tsv && "

        "cp {params.resource_dir}/dataset_description.json {params.out_dir}/atlases/sub-{wildcards.subid}/atlas-DesikanKilliany/dataset_description.json"

# Apply XCP-D to the fMRIPrep processed data using the Desikan-Killiany atlas we created from FreeSurfer parcellation
# To change the preprocessing parameters, such as the smoothing kernel width, confounds to be used for denoising, etc.
# you can change the command line arguments to XCP-D in the shell command bellow. The usage instructions can be found here:
# https://xcp-d.readthedocs.io/en/latest/usage.html#command-line-arguments
rule xcp_d:
    input:
        os.path.join(
            derivatives_dir,
            "fmriprep",
            "sub-{subid}",
            "func",
            "sub-{subid}_task-rest_space-fsLR_den-91k_bold.dtseries.nii"
        ),
        os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany",
            "atlas-DesikanKilliany_space-fsLR_den-32k_dseg.dlabel.nii"
        ),
        os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany",
            "atlas-DesikanKilliany_dseg.tsv"
        ),
        os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany",
            "dataset_description.json"
        )
    params:
        out_dir=derivatives_dir,
        fs_license_dir=resourcedir,
        workflow_dir=workflowdir,
        atlas_dir=os.path.join(
            derivatives_dir,
            "atlases",
            "sub-{subid}",
            "atlas-DesikanKilliany"
        )
    threads: 8
    resources:
        mem='32G',
        time='12:00:00'
    output:
        os.path.join(
            derivatives_dir,
            "xcp_d",
            "sub-{subid}",
            "func",
            "sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_stat-mean_timeseries.ptseries.nii"
        ),
        os.path.join(
            derivatives_dir,
            "xcp_d",
            "sub-{subid}",
            "func",
            "sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_stat-pearsoncorrelation_boldmap.pconn.nii"
        )
    container:
        config["containers"]["xcp_d"]
    shell:
        "rm -rf {params.workflow_dir}/working_dir && "
        "xcp_d "
        "{params.out_dir}/fmriprep "
        "{params.out_dir}/xcp_d "
        "participant "
        "--participant-label {wildcards.subid} "
        "--mode linc "
        "--despike "
        "--nuisance-regressors acompcor "
        "--datasets DesikanKilliany={params.atlas_dir} "
        "--atlases DesikanKilliany "
        "--head_radius 40 "
        "--fs-license-file {params.fs_license_dir}/license.txt "
        "--smoothing 6 "
        "--n_cpus 16"