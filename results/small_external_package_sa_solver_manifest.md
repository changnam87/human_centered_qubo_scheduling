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

## Observed Result

The simulated annealing solver was run on the small 15-variable external QUBO package.

The run used 100 restarts, 2,000 iterations per restart, initial_temperature = 10.0, final_temperature = 0.001, and seed = 123.

The known brute-force optimum was 5.30 with bitstring 100000000000100.

The simulated annealing solver recovered the same best energy 5.30 and the same best bitstring 100000000000100.

The best gap to brute-force was approximately 8.88e-16, which is numerical floating-point error.

The solver reached the optimum in 14 out of 100 restarts, giving success_rate = 0.14.

The validation status was PASS.
