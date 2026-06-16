# Toy Squared Target QUBO Export Manifest

## Purpose

This pilot exports an explicit toy QUBO coefficient dictionary for the squared target human-utilization formulation.

The goal is to move from CP-SAT equivalent objective validation toward actual QUBO coefficient construction.

## Toy Problem

operations = 4
resources = 3
variables = operations * resources = 12

resource 0 = machine
resource 1 = human
resource 2 = robot

## Decision Variable

x[i,r] = 1 if operation i is assigned to resource r
x[i,r] = 0 otherwise

## Objective

energy = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target)^2 + assignment_penalty * sum_i (sum_r x[i,r] - 1)^2

## QUBO Form

energy = constant + sum_i Q[i,i] x_i + sum_{i<j} Q[i,j] x_i x_j

## Parameters

human_reward = 2.5
target_human_assignments = 2
lambda_target = 1.0
assignment_penalty = 20.0

## Outputs

results/tables/toy_squared_target_qubo_coefficients.csv
results/tables/toy_squared_target_qubo_energy_validation.csv
results/tables/toy_squared_target_qubo_summary.json
results/tables/toy_squared_target_qubo_best_solution.csv

## Validation

The exported QUBO was validated by brute force over all 2^12 binary assignments.

For each assignment, direct_objective(x) was compared against the exported QUBO energy.

The validation passes when max_abs_error is below numerical tolerance.

This confirms that the exported coefficient dictionary exactly represents the intended toy objective.

## Pilot Status

This remains a toy-level QUBO export validation. The next step is to export a small time-indexed scheduling QUBO and then scale toward sample_4x4.
