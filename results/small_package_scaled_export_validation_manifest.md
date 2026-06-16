# Small Package Scaled QUBO/Ising Export Validation Manifest

## Purpose

This step creates and validates scaled QUBO/Ising exports for the small external-solver-ready package.

The purpose is to prepare coefficient files with bounded ranges for external solvers while preserving energy ordering and argmin.

## Scope

This validation is for the small 15-variable package only.

It does not run quantum hardware, quantum annealing, dimod, or QAOA.

## Observed Result

The validation enumerated all 32,768 assignments for the 15-variable package.

The scaling mode was unit_abs_max.

The maximum absolute coefficient before scaling was 959.2.

The scale factor was approximately 0.0010425354.

The unscaled, scaled QUBO, and scaled Ising formulations all selected the same best bitstring: 100000000000100.

The unscaled best energy was 5.30.

The scaled QUBO best energy was approximately 0.00552544.

The scaled Ising best energy was approximately 0.00552544.

The scaled QUBO-vs-Ising maximum absolute error was approximately 7.1e-15.

The validation status was PASS.

## Outputs

exports/small_time_indexed_solver_package/small_time_indexed_scaled_qubo_coefficients.csv
exports/small_time_indexed_solver_package/small_time_indexed_scaled_ising_linear_fields.csv
exports/small_time_indexed_solver_package/small_time_indexed_scaled_ising_couplers.csv
exports/small_time_indexed_solver_package/small_time_indexed_scaled_scaling_metadata.json
results/tables/small_package_scaled_export_validation.csv
results/tables/small_package_scaled_export_validation_summary.json

## Script

scripts/validate_small_package_scaled_exports.py

## Success Criterion

The validation passes when scaled and unscaled formulations have the same argmin and scaled energies recover unscaled energies after rescaling.
