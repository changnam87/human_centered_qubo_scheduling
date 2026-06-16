# Small External Package SA Parameter Sensitivity Manifest

## Purpose

This step evaluates simulated annealing parameter sensitivity on the small external-solver-ready QUBO package.

The purpose is to measure how restarts, iterations, temperature schedule, and random seed affect the probability of recovering the known brute-force optimum.

## Reference Optimum

brute_force_optimum = 5.30
brute_force_bitstring = 100000000000100

## Script

scripts/run_small_external_package_sa_parameter_sensitivity.py

## Outputs

results/tables/small_external_package_sa_parameter_sensitivity_summary.csv
results/tables/small_external_package_sa_parameter_sensitivity_best.json
results/tables/small_external_package_sa_sensitivity/

## Interpretation Note

This is a small-package heuristic sensitivity test. It is not a full sample_4x4 solver benchmark and not a quantum hardware result.
