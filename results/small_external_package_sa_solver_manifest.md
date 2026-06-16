# Small External Package Simulated Annealing Solver Manifest

## Purpose

This step runs a minimal simulated annealing solver on the small external-solver-ready QUBO package.

The purpose is to verify that a simple heuristic solver can consume the exported package and recover or approach the brute-force optimum.

## Scope

This solver test is only for the small 15-variable package.

It is not run on the full sample_4x4 QUBO.

## Reference Brute-Force Result

best QUBO energy = 5.30
best bitstring = 100000000000100

## Script

scripts/run_small_external_package_sa_solver.py

## Outputs

results/tables/small_external_package_sa_solver_runs.csv
results/tables/small_external_package_sa_solver_summary.json

## Success Criterion

The test passes if the simulated annealing solver reaches the brute-force optimum energy.
