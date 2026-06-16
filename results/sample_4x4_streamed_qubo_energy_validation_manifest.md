# sample_4x4 Streamed QUBO Energy Validation Manifest

## Purpose

This pilot validates the streamed sparse sample_4x4 QUBO coefficient export by comparing streamed CSV-based QUBO energy against direct objective values on sampled assignments.

## Input

results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv

This coefficient file is large and intentionally ignored by Git.

## Validation Strategy

The streamed coefficient CSV is read in chunks.

For each sampled binary assignment, QUBO energy is computed as:

energy = constant + sum over streamed rows coefficient * x_i * x_j

The result is compared against the direct objective computed from the same representative sample_4x4 formulation.

## Sample Types

- all-zero vector
- greedy feasible schedule
- random one-start schedules
- random sparse binary schedules

## Scripts

scripts/validate_sample_4x4_streamed_qubo_energy.py

## Outputs

results/tables/sample_4x4_streamed_qubo_energy_validation.csv
results/tables/sample_4x4_streamed_qubo_energy_validation_summary.json

## Success Criterion

The validation passes when the maximum absolute error between streamed QUBO energy and direct objective is within numerical tolerance.

## Pilot Status

This validates coefficient-level consistency for the streamed sparse export. It does not solve the sample_4x4 QUBO.
