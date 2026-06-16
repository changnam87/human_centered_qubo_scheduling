# Small Package dimod Import Smoke Test Manifest

## Purpose

This step attempts to import the small package dimod-style BQM JSON exports into actual dimod BinaryQuadraticModel objects.

## Scope

This test is for the small 15-variable package only.

It does not run D-Wave hardware, quantum annealing, or QAOA.

## Observed Result

The dimod import smoke test returned SKIPPED status.

The reason was that dimod is not installed in the current environment.

This is not a validation failure. The script handled the missing optional dependency gracefully.

To run actual dimod BinaryQuadraticModel import validation, install dimod in the active environment and rerun the script.

## Inputs

exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_bqm.json
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_bqm.json

## Script

scripts/run_small_package_dimod_import_smoke_test.py

## Outputs

results/tables/small_package_dimod_import_smoke_test.csv
results/tables/small_package_dimod_import_smoke_test_summary.json

## Status Meaning

PASS means dimod imported the BQM objects and sampled energies matched within tolerance.

SKIPPED means dimod was not installed in the current environment.
