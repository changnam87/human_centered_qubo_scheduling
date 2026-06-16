# Small Package dimod Import Smoke Test Manifest

## Purpose

This step attempts to import the small package dimod-style BQM JSON exports into actual dimod BinaryQuadraticModel objects.

## Scope

This test is for the small 15-variable package only.

It does not run D-Wave hardware, quantum annealing, or QAOA.

## Behavior

If dimod is installed, the script builds BINARY and SPIN BinaryQuadraticModel objects and validates sampled energies.

If dimod is not installed, the script records SKIPPED status rather than failing.

## Inputs

exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_bqm.json
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_bqm.json

## Script

scripts/run_small_package_dimod_import_smoke_test.py

## Outputs

results/tables/small_package_dimod_import_smoke_test.csv
results/tables/small_package_dimod_import_smoke_test_summary.json

## Success Criterion

PASS means dimod imported the BQM objects and sampled energies matched within tolerance.

SKIPPED means dimod was not installed in the current environment.
