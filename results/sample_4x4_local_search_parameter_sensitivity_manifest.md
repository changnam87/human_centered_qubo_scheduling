# sample_4x4 Local Search Parameter Sensitivity Manifest

## Purpose

This step evaluates whether local QUBO search performance can be improved through parameter sensitivity.

The target comparison point is the objective-equivalent CP-SAT squared-target optimum.

## Reference Values

CP-SAT squared-target optimum = 47.70
Previous local QUBO best = 51.25
Previous absolute gap = 3.55
Previous relative gap approximately 7.44 percent

## Parameter Grid

The full sensitivity experiment evaluated combinations of:

- restarts = 30, 50
- iterations = 10000, 20000
- initial_temperature = 5.0, 10.0, 20.0
- final_temperature = 0.001, 0.01
- seeds = 123, 456, 789

Total cases = 72

## Best Observed Case

The best observed case was:

run_id = 20
tag = run020_r30_it20000_t5.0_tf0.001_s789
restarts = 30
iterations = 20000
initial_temperature = 5.0
final_temperature = 0.001
seed = 789
best_energy = 48.20
feasible_rate = 1.0
best_run = 23

## Gap to CP-SAT Optimum

absolute_gap = 48.20 - 47.70 = 0.50
relative_gap = 0.50 / 47.70 = approximately 1.05 percent

## Interpretation

Parameter tuning substantially improved the local QUBO heuristic.

The previous local best was 51.25, whereas the tuned best was 48.20.

The absolute gap to the CP-SAT squared-target optimum decreased from 3.55 to 0.50.

This shows that the merged sparse QUBO can support near-optimal local heuristic search in this representative sample_4x4 prototype.

This remains a heuristic result and does not prove optimality.

## Scripts

scripts/run_sample_4x4_local_search_parameter_sensitivity.py

## Outputs

results/tables/sample_4x4_local_search_parameter_sensitivity_summary.csv
results/tables/sample_4x4_local_search_parameter_sensitivity_best.json
results/tables/local_search_parameter_sensitivity/
