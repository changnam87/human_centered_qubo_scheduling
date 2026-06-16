# sample_4x4 Runtime and Memory Profile Manifest

## Purpose

This step summarizes runtime, size, and engineering metadata for the sample_4x4 QUBO/Ising prototype pipeline.

The summary is generated from existing JSON and CSV result artifacts without rerunning heavy experiments.

## Key Engineering Results

num_variables = 8713
merged_terms = 8218171
quadratic_density = approximately 0.2163
CP-SAT squared-target optimum = 47.70
initial local QUBO best = 51.25
tuned local QUBO best = 48.20
tuned gap to CP-SAT = 0.50
Ising validation status = PASS
Ising validation max_abs_error = 0.0

## Runtime Highlights

streaming sparse QUBO export = approximately 21.39 seconds
streamed QUBO energy validation = approximately 5.23 seconds
duplicate merge = approximately 10.30 seconds
merged QUBO energy validation = approximately 3.58 seconds
local QUBO initial search load = approximately 3.15 seconds

## Large Local Artifact Sizes

streamed QUBO coefficients CSV = approximately 800.64 MB
merged QUBO coefficients CSV = approximately 112.25 MB
Ising couplers CSV = approximately 117.79 MB
Ising linear fields CSV = approximately 0.12 MB

## Scope

The profile covers:

- QUBO export feasibility estimate
- streaming sparse QUBO export
- streamed QUBO energy validation
- duplicate merge
- merged QUBO energy validation
- solver-ready QUBO metadata
- local QUBO search
- objective-equivalent CP-SAT baseline
- local search parameter sensitivity
- tuned local solution component analysis
- QUBO-to-Ising metadata
- Ising energy validation

## Outputs

results/tables/sample_4x4_runtime_memory_profile_summary.csv
results/tables/sample_4x4_runtime_memory_profile_summary.json
results/tables/sample_4x4_large_artifact_size_summary.csv

## Script

scripts/summarize_sample_4x4_runtime_memory_profile.py

## Interpretation Note

This is an engineering profile for prototype validation. It consolidates existing metadata and does not rerun heavy experiments.
