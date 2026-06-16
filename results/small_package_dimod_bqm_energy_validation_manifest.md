# Small Package dimod-Style BQM Energy Validation Manifest

## Purpose

This step validates energy consistency of the small package dimod-compatible BQM-style exports.

The validation compares original QUBO energy, original Ising energy, dimod-style BINARY BQM energy, and dimod-style SPIN BQM energy.

## Scope

This validation is for the small 15-variable external solver package only.

It does not run dimod, D-Wave hardware, quantum annealing, or QAOA.

## Observed Result

The validation used 23 sampled assignments.

The maximum absolute error across compared energy representations was approximately 9.09e-13.

The mean absolute error between dimod-style BINARY and SPIN BQM energies was approximately 1.15e-13.

The validation status was PASS.

This confirms numerical energy consistency of the dimod-style BQM JSON exports.

## Inputs

exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_bqm.json
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_bqm.json
exports/small_time_indexed_solver_package/qubo_coefficients.csv
exports/small_time_indexed_solver_package/ising_linear_fields.csv
exports/small_time_indexed_solver_package/ising_couplers.csv

## Script

scripts/validate_small_package_dimod_bqm_energy.py

## Outputs

results/tables/small_package_dimod_bqm_energy_validation.csv
results/tables/small_package_dimod_bqm_energy_validation_summary.json

## Success Criterion

The validation passes when all energy representations agree within numerical tolerance.
