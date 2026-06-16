# sample_4x4 Reproducibility Workflow Manifest

## Purpose

This step adds a reproducibility workflow document and artifact-check script for the sample_4x4 QUBO/Ising prototype pipeline.

## Added Files

scripts/check_sample_4x4_reproducibility_artifacts.py
docs/sample_4x4_reproducibility_workflow.md
results/tables/sample_4x4_reproducibility_artifact_check_summary.json

## Scope

The workflow documents how to regenerate ignored large artifacts and downstream compact summaries.

This does not rerun the full pipeline automatically.

## Important Note

Large coefficient artifacts remain ignored by Git and may need regeneration before downstream validation steps.
