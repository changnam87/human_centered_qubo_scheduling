# sample_4x4 Tuned Local QUBO Solution Component Analysis Manifest

## Purpose

This step decomposes the best tuned local QUBO solution from the parameter sensitivity experiment into interpretable objective components.

The tuned local solution is compared directly against the objective-equivalent CP-SAT squared-target optimum.

## Reference Values

CP-SAT squared-target optimum = 47.70
Previous local QUBO best = 51.25
Best tuned local QUBO = 48.20

## Best Tuned Local Search Case

run_id = 20
tag = run020_r30_it20000_t5.0_tf0.001_s789
restarts = 30
iterations = 20000
initial_temperature = 5.0
final_temperature = 0.001
seed = 789

## Outputs

results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.csv
results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json
results/tables/sample_4x4_tuned_local_qubo_solution_operation_components.csv
results/tables/sample_4x4_tuned_local_qubo_vs_cpsat_squared_target_comparison.csv

## Script

scripts/analyze_sample_4x4_tuned_local_solution_components.py

## Interpretation Note

This analysis identifies which objective components explain the remaining gap between the tuned local QUBO solution and the CP-SAT squared-target optimum.

The tuned local solution remains a heuristic result and does not prove optimality.
