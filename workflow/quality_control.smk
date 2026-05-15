""" Quality assurance procedure rules """

# rule create_data_description_qa:
#     input:
#         os.path.join("resources", "dataset_description_qa.json")
#     params:
#         workflowdir = workflowdir,
#         outdir = outdir
#     output:
#         os.path.join(outdir, "derivatives", "quality_control", "dataset_description.json")
#     conda:
#         os.path.join(environmentdir, "environment.yaml")
#     shell:
#         "mkdir -p {params.outdir}/derivatives/quality_control && "
#         "cp {input} {output}"

rule get_dicom_metadata:
    input:
        os.path.join(outdir, "dicom", "LE_GK_010_1_", "20120707_PAUL_KOPF", "MR_Seq._10_FieldMapping_BOLD", "0000.dcm")
    params:
        dicomdir=os.path.join(outdir, "dicom"),
        outdir=outdir,
        workflowdir=workflowdir
    output:
        os.path.join(outdir, "derivatives", "quality_control", "desc-dicomMetadata_summary.pkl"),
        os.path.join(outdir, "derivatives", "quality_control", "desc-dicomMetadata_summary.json"),
        os.path.join(outdir, "derivatives", "quality_control", "desc-getDicomMetadata_log.txt"),
        os.path.join(outdir, "derivatives", "quality_control", "desc-getDicomMetadata_log.json")
    conda:
        os.path.join(environmentdir, "environment.yaml")
    shell:
        "mkdir -p {params.outdir}/derivatives/quality_control && "
        "python {params.workflowdir}/scripts/quality_control/get_dicom_metadata.py --dicom_dir {params.dicomdir} --output_dir {params.outdir}/derivatives/quality_control > {params.outdir}/derivatives/quality_control/desc-getDicomMetadata_log.txt"

rule metadata_check:
    input:
        os.path.join(outdir, "derivatives", "quality_control", "desc-dicomMetadata_summary.pkl"),
        expand(os.path.join(rawdir, "sub-{subid}", "func", "sub-{subid}_task-rest_bold.nii.gz"), subid=subids),
        expand(os.path.join(outdir, "derivatives", "temp", "sub-{subid}_bidsfilter.json"), subid=subids_all)
    params:
        outdir=outdir,
        workflowdir=workflowdir,
        rawdir=rawdir
    output:
        os.path.join(outdir, "derivatives", "quality_control", "desc-metadataCheck_log.txt"),
        os.path.join(outdir, "derivatives", "quality_control", "desc-metadataCheck_log.json")
    conda:
        os.path.join(environmentdir, "environment.yaml")
    shell:
        "python {params.workflowdir}/scripts/quality_control/metadata_check.py --dicom_meta {input[0]} --bids_dir {params.rawdir} --output_dir {params.outdir}/derivatives/quality_control > {output[0]}"

rule framewise_displacement:
    input:
        expand(os.path.join(outdir, "derivatives", "fmriprep", "sub-{subid}", "func", "sub-{subid}_task-rest_desc-confounds_timeseries.tsv"), subid=subids)
    params:
        outdir=outdir,
        workflowdir=workflowdir
    output:
        expand([os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "figures", "sub-{subid}_task-rest_desc-framewiseDisplacement_figure.png"),
        os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "figures", "sub-{subid}_task-rest_desc-framewiseDisplacement_figure.json"),
        os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "sub-{subid}_task-rest_desc-framewiseDisplacementTranslational_timeseries.tsv"),
        os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "sub-{subid}_task-rest_desc-framewiseDisplacementTranslational_timeseries.json"),
        os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "sub-{subid}_task-rest_desc-framewiseDisplacementRotational_timeseries.tsv"),
        os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "sub-{subid}_task-rest_desc-framewiseDisplacementRotational_timeseries.json")], subid=subids),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-framewiseDisplacement_summary.tsv"),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-framewiseDisplacement_summary.json"),
        os.path.join(outdir, "derivatives", "quality_control", "figures", "task-rest_desc-maxFramewiseDisplacementScatter_figure.png"),
        os.path.join(outdir, "derivatives", "quality_control", "figures", "task-rest_desc-maxFramewiseDisplacementScatter_figure.json"),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-framewiseDisplacement_log.txt"),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-framewiseDisplacement_log.json")
    conda:
        os.path.join(environmentdir, "environment.yaml")
    shell:
        "mkdir -p {params.outdir}/derivatives/quality_control/figures && "
        "python {params.workflowdir}/scripts/quality_control/framewise_displacement.py --derivatives_dir {params.outdir}/derivatives --output_dir {params.outdir}/derivatives/quality_control > {params.outdir}/derivatives/quality_control/task-rest_desc-framewiseDisplacement_log.txt"

rule denoising_verification:
    input:
        expand(os.path.join(outdir, "derivatives", "xcp_d", "sub-{subid}", "func", "sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_stat-mean_timeseries.ptseries.nii"), subid=subids),
        expand(os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "sub-{subid}_task-rest_desc-framewiseDisplacementTranslational_timeseries.tsv"), subid=subids),
        expand(os.path.join(outdir, "derivatives", "atlases", "sub-{subid}", "atlas-DesikanKilliany", "atlas-DesikanKilliany_space-fsLR_den-32k_dseg.dlabel.nii"), subid=subids)
    params:
        outdir=outdir,
        workflowdir=workflowdir
    output:
        expand([os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "figures", "sub-{subid}_task-rest_desc-rawVsClean_figure.png"),
        os.path.join(outdir, "derivatives", "quality_control", "sub-{subid}", "figures", "sub-{subid}_task-rest_desc-rawVsClean_figure.json")], subid=subids),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-denoisingVerification_log.txt"),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-denoisingVerification_log.json")
    # container:
    #     config["containers"]["wb_command"]
    conda:
        os.path.join(environmentdir, "environment.yaml")
    shell:
        "python {params.workflowdir}/scripts/quality_control/denoising_verification.py --derivatives_dir {params.outdir}/derivatives --output_dir {params.outdir}/derivatives/quality_control > {params.outdir}/derivatives/quality_control/task-rest_desc-denoisingVerification_log.txt"

rule qc_fc:
    input:
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-framewiseDisplacement_summary.tsv"),
        os.path.join(resourcedir, "atlas-desikankilliany.csv"),
        os.path.join(resourcedir, "atlas-desikankilliany.nii.gz"),
        os.path.join(outdir, "intermediaries", "networks", "network_labels.pkl"),
        expand(os.path.join(outdir, "derivatives", "static", "sub-{subid}", "sub-{subid}_task-rest_space-fsLR_seg-DesikanKilliany_den-91k_desc-rawFC_relmat.tsv"), subid=subids)
    params:
        outdir=outdir,
        workflowdir=workflowdir
    output:
        os.path.join(outdir, "derivatives", "quality_control", "figures", "task-rest_desc-qcFcCorrelationHistograms_figure.png"),
        os.path.join(outdir, "derivatives", "quality_control", "figures", "task-rest_desc-qcFcCorrelationHistograms_figure.json"),
        os.path.join(outdir, "derivatives", "quality_control", "figures", "task-rest_desc-qcFcDistanceCorrelation_figure.png"),
        os.path.join(outdir, "derivatives", "quality_control", "figures", "task-rest_desc-qcFcDistanceCorrelation_figure.json"),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-qcFc_log.txt"),
        os.path.join(outdir, "derivatives", "quality_control", "task-rest_desc-qcFc_log.json")
    conda:
        os.path.join(environmentdir, "environment.yaml")
    shell:
        "python {params.workflowdir}/scripts/quality_control/qc_fc.py --motion_summary {input[0]} --atlas_csv {input[1]} --atlas_img {input[2]} --network_labels {input[3]} --fc_dir {params.outdir}/derivatives/static/ --output_dir {params.outdir}/derivatives/quality_control > {params.outdir}/derivatives/quality_control/task-rest_desc-qcFc_log.txt"