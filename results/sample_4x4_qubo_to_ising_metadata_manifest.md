# sample_4x4 QUBO-to-Ising Metadata Manifest

## Purpose

This step analyzes the QUBO-to-Ising conversion metadata for the merged sample_4x4 sparse QUBO.

The purpose is to prepare the solver-ready QUBO for downstream Ising-based solvers, quantum annealing formats, or QAOA-oriented representations.

## QUBO Energy Convention

E_QUBO(x) = constant + sum_i Q_ii x_i + sum_{i<j} Q_ij x_i x_j

## Ising Energy Convention

E_Ising(s) = offset + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j

## Variable Transformation

x_i = (1 + s_i) / 2

## Inputs

results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv
results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json

## Outputs

results/tables/sample_4x4_qubo_to_ising_metadata_summary.json
results/tables/sample_4x4_qubo_to_ising_metadata_summary.csv
results/tables/sample_4x4_ising_linear_fields.csv
results/tables/sample_4x4_ising_couplers.csv

## Important Note

The Ising coupler CSV may be large and should usually remain a local ignored artifact.

This step creates Ising metadata and format readiness, but it does not yet run quantum annealing or QAOA.
