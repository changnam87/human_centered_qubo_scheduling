# sample_4x4 Local QUBO Solution Component Analysis Manifest

## Purpose

This step analyzes the best solution found by the sample_4x4 merged QUBO local search.

The goal is to decompose the local QUBO best solution into interpretable cost components and compare it against the previously established CP-SAT baseline values.

## Inputs

results/tables/sample_4x4_merged_qubo_local_search_best_solution.csv
results/tables/sample_4x4_merged_qubo_local_search_summary.json
results/tables/sample_4x4_sparse_qubo_streaming_summary.json

## Outputs

results/tables/sample_4x4_local_qubo_solution_component_summary.csv
results/tables/sample_4x4_local_qubo_solution_component_summary.json
results/tables/sample_4x4_local_qubo_solution_operation_components.csv
results/tables/sample_4x4_local_qubo_vs_cpsat_baseline_comparison.csv

## Components

- assignment cost
- workload cost
- ergonomic cost
- start-time cost
- total cost without reward
- reward term
- squared target penalty
- assignment/resource-overlap/precedence penalties
- machine/human/robot assignment counts

## Interpretation Note

The CP-SAT baseline and local QUBO result are not always direct objective-equivalent comparisons because the local QUBO includes human reward and squared target penalty.

The comparison should therefore be interpreted as a prototype diagnostic rather than a final benchmark claim.

## Script

scripts/analyze_sample_4x4_local_qubo_solution_components.py
