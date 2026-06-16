# sample_4x4 Ising Energy Validation Manifest

## Purpose

This step validates energy consistency between the merged sparse QUBO and the converted Ising representation.

## QUBO Energy Convention

E_QUBO(x) = constant + sum_{i<=j} Q_ij x_i x_j

## Ising Energy Convention

E_Ising(s) = offset + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j

## Variable Mapping

s_i = 2 x_i - 1

## Validation Samples

- tuned local best solution
- all-zero assignment
- random one-start assignments
- random sparse binary assignments

## Observed Result

The fast Ising energy validation passed.

The validation used six sampled assignments: tuned_local_best, all_zero, random_one_start_0, random_one_start_1, random_sparse_0, and random_sparse_1.

The maximum absolute error was 0.0 and the mean absolute error was 0.0.

This confirms exact energy consistency between the merged QUBO representation and the QUBO-to-Ising transformed energy on the sampled assignments.

## Scripts

scripts/validate_sample_4x4_ising_energy.py

## Outputs

results/tables/sample_4x4_ising_energy_validation.csv
results/tables/sample_4x4_ising_energy_validation_summary.json

## Success Criterion

Validation passes when QUBO energy and Ising energy match within numerical tolerance on sampled assignments.

## Pilot Status

This validates the QUBO-to-Ising transformation. It does not yet run quantum hardware, quantum annealing, or QAOA.
