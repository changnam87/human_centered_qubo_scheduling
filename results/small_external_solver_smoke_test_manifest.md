# Small External Solver Smoke Test Manifest

## Purpose

This step runs a minimal brute-force smoke test on the small external-solver-ready QUBO/Ising package.

The goal is to verify that the exported package can be consumed as an external solver input.

## Scope

This smoke test is only for the small time-indexed solver package.

It is not run on the full sample_4x4 QUBO.

## Input Package

exports/small_time_indexed_solver_package/

## Observed Result

The brute-force smoke test enumerated all 32,768 assignments for the 15-variable small package.

The best bitstring was 100000000000100.

The best QUBO energy was 5.30.

The corresponding Ising energy was 5.30.

The maximum absolute QUBO-vs-Ising energy error was approximately 1.14e-12.

The validation status was PASS.

This confirms that the small external-solver package can be consumed as a valid QUBO/Ising solver input.

## Script

scripts/run_small_external_solver_smoke_test.py

## Outputs

results/tables/small_external_solver_smoke_test_result.csv
results/tables/small_external_solver_smoke_test_summary.json

## Success Criterion

The test passes when QUBO and Ising energies agree within numerical tolerance for all brute-force assignments.
