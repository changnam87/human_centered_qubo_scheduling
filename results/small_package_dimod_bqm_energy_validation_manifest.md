# Small Package dimod-Style BQM Energy Validation Manifest

## Purpose

This step validates energy consistency of the small package dimod-compatible BQM-style exports.

The validation compares original QUBO energy, original Ising energy, dimod-style BINARY BQM energy, and dimod-style SPIN BQM energy.

## Scope

This validation is for the small 15-variable external solver package only.

It does not run dimod, D-Wave hardware, quantum annealing, or QAOA.

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
