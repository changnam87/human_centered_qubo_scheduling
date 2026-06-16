# sample_4x4 CP-SAT Squared-Target Baseline Manifest

## Purpose

This step solves a CP-SAT baseline using the same squared-target objective structure as the representative sample_4x4 QUBO local search.

The purpose is to create an objective-equivalent comparison point for the local QUBO heuristic result.

## Objective

objective = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target_human_assignments)^2

## Parameters

human_reward = 2.5
lambda_target = 1.0
target_human_assignments = 4
scale = 100

## Observed Result

The CP-SAT model returned OPTIMAL status.

The scaled solver objective was 4770.0.

The unscaled objective was 47.70.

The component recomputation matched the solver objective with numerical error approximately 7.1e-15.

The CP-SAT solution had total_cost_without_reward = 57.70, human_count = 4, reward_term = 10.0, target_penalty = 0.0, and adjusted_objective = 47.70.

The previous local QUBO search best energy was 51.25.

Therefore, the local QUBO heuristic gap relative to the CP-SAT squared-target optimum was 3.55, or approximately 7.44 percent.

This confirms that the local QUBO search found a feasible target-consistent solution, but not the objective-equivalent CP-SAT optimum.

## Script

scripts/run_sample_4x4_cpsat_squared_target_baseline.py

## Outputs

results/tables/sample_4x4_cpsat_squared_target_solution.csv
results/tables/sample_4x4_cpsat_squared_target_component_summary.csv
results/tables/sample_4x4_cpsat_squared_target_vs_local_qubo_comparison.csv
results/tables/sample_4x4_cpsat_squared_target_summary.json

## Interpretation Note

This CP-SAT result is a more objective-equivalent comparison for the local QUBO search than the original total-cost-only CP-SAT baseline.

This remains a prototype validation result.
