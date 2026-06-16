# Small External Package Solver Benchmark Summary Manifest

## Purpose

This step consolidates solver results for the small external-solver-ready QUBO/Ising package.

The summary combines brute-force enumeration, the initial simulated annealing baseline, and the best simulated annealing parameter sensitivity result.

## Scope

This benchmark summary is only for the small 15-variable external solver package.

It is not a full sample_4x4 benchmark and not a quantum hardware result.

## Observed Result

The brute-force optimum was 5.30 with bitstring 100000000000100.

The initial simulated annealing baseline recovered the optimum in 14 out of 100 restarts, giving success_rate = 0.14.

The best simulated annealing sensitivity case recovered the optimum in 145 out of 200 restarts, giving success_rate = 0.725.

The success-rate improvement from initial SA to tuned SA was 0.585.

## Included Solver Results

- brute-force exhaustive enumeration
- initial simulated annealing baseline
- best simulated annealing parameter sensitivity case

## Script

scripts/summarize_small_external_package_solver_benchmarks.py

## Outputs

results/tables/small_external_package_solver_benchmark_summary.csv
results/tables/small_external_package_solver_benchmark_summary.json

## Interpretation Note

This compact benchmark confirms that the small package can support both exhaustive and heuristic solver workflows.
