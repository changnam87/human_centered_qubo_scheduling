# Small External Package Solver Benchmark Summary Manifest

## Purpose

This step consolidates solver results for the small external-solver-ready QUBO/Ising package.

The summary combines brute-force enumeration, the initial simulated annealing baseline, and the best simulated annealing parameter sensitivity result.

## Scope

This benchmark summary is only for the small 15-variable external solver package.

It is not a full sample_4x4 benchmark and not a quantum hardware result.

## Included Solver Results

- brute-force exhaustive enumeration
- initial simulated annealing baseline
- best simulated annealing parameter sensitivity case

## Script

scripts/summarize_small_external_package_solver_benchmarks.py

## Outputs

results/tables/small_external_package_solver_benchmark_summary.csv
results/tables/small_external_package_solver_benchmark_summary.json

## Expected Headline Result

The best simulated annealing sensitivity setting improves optimum-recovery success rate over the initial SA baseline.
