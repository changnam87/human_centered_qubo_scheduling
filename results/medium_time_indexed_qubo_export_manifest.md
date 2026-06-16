# Medium Time-Indexed QUBO Export Manifest

## Purpose

This pilot scales the small time-indexed QUBO export to a medium time-indexed scheduling prototype.

The goal is to evaluate coefficient export, sampled energy validation, feasible schedule generation, and QUBO size growth.

## Medium Problem

operations = 3
resources = 3
horizon = 6

resource 0 = machine A
resource 1 = machine B
resource 2 = human

## Decision Variable

x[o,r,t] = 1 if operation o starts on resource r at time t
x[o,r,t] = 0 otherwise

## Objective Components

The exported QUBO includes assignment/start-time cost, workload and ergonomic cost, soft human reward, squared target human-utilization penalty, one-start assignment penalties, resource overlap penalties, and precedence penalties.

## Validation Strategy

Full brute-force validation becomes increasingly expensive as the variable count grows.

Therefore, this medium prototype uses sampled validation plus a generated greedy feasible schedule.

For each sampled binary assignment, the direct objective is compared against the exported QUBO energy.

The validation passes when the maximum absolute error is below numerical tolerance.

## Outputs

results/tables/medium_time_indexed_qubo_coefficients.csv
results/tables/medium_time_indexed_qubo_energy_validation_samples.csv
results/tables/medium_time_indexed_qubo_summary.json
results/tables/medium_time_indexed_qubo_greedy_feasible_solution.csv
results/tables/qubo_size_scaling_summary.csv

## Scripts

scripts/export_medium_time_indexed_qubo.py
scripts/summarize_qubo_size_scaling.py

## Pilot Status

This remains prototype-level validation. The next stage is to design scalable coefficient-export and validation strategies for benchmark-derived instances such as sample_4x4.
