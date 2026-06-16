# sample_4x4 Solver-Ready Sparse QUBO Metadata Manifest

## Purpose

This step analyzes the merged sample_4x4 sparse QUBO and creates solver-ready metadata.

The merged sparse QUBO has one row per unique (i,j) coefficient pair and is treated as a local artifact because of its size.

## Inputs

results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv
results/tables/sample_4x4_sparse_qubo_streaming_summary.json
results/tables/sample_4x4_sparse_qubo_merge_summary.json

## Outputs

results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json
results/tables/sample_4x4_sparse_qubo_solver_ready_summary.csv

## Script

scripts/analyze_sample_4x4_solver_ready_qubo.py

## QUBO Energy Convention

E(x) = constant_offset + sum_{i<=j} coefficient(i,j) * x_i * x_j

## Metadata Fields

- num_variables
- constant_offset
- total_terms
- linear_terms
- quadratic_terms
- coefficient_min
- coefficient_max
- coefficient_abs_max
- sparse density estimates
- scale recommendation
- file schema

## Pilot Status

This prepares the sample_4x4 compact sparse QUBO for downstream solver experiments. It does not yet solve the QUBO.

## Observed Solver-Ready QUBO Metadata

The merged sample_4x4 sparse QUBO metadata analysis completed successfully.

The solver-ready sparse QUBO contains 8,713 binary variables and 8,218,171 nonzero upper-triangular coefficient terms.

The model contains 8,713 linear terms and 8,209,458 quadratic terms.

The constant offset is 496.0.

The upper-triangular sparse density is approximately 0.2165, and the quadratic density is approximately 0.2163.

The coefficient range is from -35.4 to 62.0, with absolute maximum coefficient 62.0.

The recommended scale factor for mapping coefficients to approximately unit absolute range is 1 / 62.0 = 0.016129.

This confirms that the sample_4x4 QUBO is available in a solver-ready sparse coefficient-list format, while also showing that the formulation is relatively dense because of quadratic coupling terms.
