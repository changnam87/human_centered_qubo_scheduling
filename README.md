# Human-Centered QUBO Scheduling

## Overview

This repository contains a prototype and pilot validation workflow for human-centered industrial scheduling using QUBO and Ising formulations.

The project is not yet a final research-paper implementation and has not yet executed quantum hardware, quantum annealing hardware, or QAOA.

The current goal is to validate whether a human-centered scheduling formulation can be represented, exported, validated, and searched as a sparse QUBO/Ising model.

## Current Project Stage

Current stage:

```text
prototype + pilot validation
```

The repository currently supports:

1. Toy QUBO formulation validation.
2. CP-SAT baseline modeling.
3. Human-utilization sensitivity analysis.
4. Soft human-reward and target-penalty modeling.
5. Sparse QUBO export for time-indexed scheduling.
6. Streamed and merged sparse QUBO validation.
7. Solver-ready sparse QUBO metadata generation.
8. Local heuristic search on merged sparse QUBO.
9. Objective-equivalent CP-SAT comparison.
10. QUBO-to-Ising metadata generation.
11. Ising energy validation.

## Representative sample_4x4 Instance

The main validated pilot instance is `sample_4x4`.

```text
jobs = 4
operations per job = 4
operations = 16
machines = 4
workers = 3
robots = 2
resources = 9
planning horizon = 63
nominal binary variables = 9072
representative valid-start variables = 8713
```

## Main Technical Result

The current validated pipeline is:

```text
human-centered scheduling formulation
    -> QUBO-compatible squared target human-utilization penalty
    -> time-indexed sparse QUBO export
    -> streamed coefficient validation
    -> duplicate-merged compact sparse QUBO
    -> solver-ready QUBO metadata
    -> local energy-based heuristic search
    -> objective-equivalent CP-SAT comparison
    -> tuned local search gap analysis
    -> QUBO-to-Ising metadata
    -> Ising energy validation
```

## Key sample_4x4 Results

### Original CP-SAT baseline

The original total-cost-only CP-SAT baseline produced:

```text
status = OPTIMAL
total cost = 57.0
human assignments = 0
workload = 0.0
ergonomic = 0.0
```

This baseline avoided human workers because assigning humans activates workload and ergonomic cost components.

### Objective-equivalent CP-SAT squared-target baseline

To compare fairly against the QUBO local search objective, an objective-equivalent CP-SAT model was solved using:

```text
objective = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target_human_assignments)^2
```

with:

```text
human_reward = 2.5
lambda_target = 1.0
target_human_assignments = 4
```

The CP-SAT squared-target result was:

```text
status = OPTIMAL
adjusted objective = 47.70
total_cost_without_reward = 57.70
human_count = 4
reward_term = 10.0
target_penalty = 0.0
```

### Local QUBO search

Initial local QUBO search found:

```text
best_energy = 51.25
feasible_rate = 0.95
```

After parameter sensitivity, the tuned local QUBO search found:

```text
best_energy = 48.20
absolute gap to CP-SAT optimum = 0.50
relative gap = approximately 1.05 percent
feasible_rate = 1.0
```

Component analysis showed that the remaining gap was entirely due to start-time cost.

```text
CP-SAT start_time_cost = 9.40
tuned local QUBO start_time_cost = 9.90
difference = 0.50
```

The tuned local QUBO solution matched the CP-SAT optimum in human_count, workload cost, ergonomic cost, reward term, and target penalty.

### QUBO-to-Ising validation

The QUBO-to-Ising conversion uses:

```text
s_i = 2 x_i - 1
x_i = (1 + s_i) / 2
```

The Ising energy validation passed:

```text
num_samples = 6
max_abs_error = 0.0
mean_abs_error = 0.0
validation_status = PASS
```

This validates QUBO-to-Ising energy consistency on sampled assignments.

## Sparse QUBO Export

The representative sample_4x4 sparse QUBO export produced:

```text
unmerged streamed coefficient rows = 8872562
merged unique nonzero coefficient pairs = 8218171
linear terms = 8713
quadratic terms = 8209458
constant offset = 496.0
quadratic density approximately 0.2163
```

The sparse QUBO is solver-ready as an upper-triangular coefficient list.

However, it is still relatively dense for a sparse QUBO because the squared target human-utilization penalty creates many pairwise human-variable couplings.

## Large Local Artifacts

Some generated coefficient files are large and intentionally ignored by Git.

Examples:

```text
results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv
results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv
results/tables/sample_4x4_ising_couplers.csv
```

These files should remain local artifacts unless using Git LFS, release assets, or external artifact storage.

## Important Scripts

Core scripts include:

```text
scripts/validate_sample_4x4_streamed_qubo_energy.py
scripts/merge_sample_4x4_streamed_qubo_coefficients.py
scripts/validate_sample_4x4_merged_qubo_energy.py
scripts/analyze_sample_4x4_solver_ready_qubo.py
scripts/run_sample_4x4_merged_qubo_local_search.py
scripts/run_sample_4x4_cpsat_squared_target_baseline.py
scripts/run_sample_4x4_local_search_parameter_sensitivity.py
scripts/analyze_sample_4x4_tuned_local_solution_components.py
scripts/analyze_sample_4x4_qubo_to_ising_metadata.py
scripts/validate_sample_4x4_ising_energy.py
```

## Important Reports and Manifests

Main technical report:

```text
docs/sample_4x4_qubo_pilot_technical_validation_report.md
```

Current checkpoint summary:

```text
results/current_pilot_checkpoint.md
```

## Reproducibility Notes

This repository currently emphasizes prototype reproducibility through tracked scripts, summaries, manifests, and validation outputs.

Because some coefficient files are large and ignored, full reproduction of later steps may require regenerating local sparse coefficient artifacts first.

Recommended high-level reproduction order:

```text
1. Generate or restore sample_4x4 sparse QUBO coefficients.
2. Validate streamed QUBO energy.
3. Merge duplicate QUBO coefficients.
4. Validate merged QUBO energy.
5. Generate solver-ready QUBO metadata.
6. Run local QUBO search.
7. Run objective-equivalent CP-SAT baseline.
8. Run local search parameter sensitivity.
9. Analyze tuned local solution components.
10. Generate QUBO-to-Ising metadata.
11. Validate Ising energy consistency.
```

## Current Interpretation

The current pilot results show that the sample_4x4 human-centered scheduling formulation can be represented as a sparse QUBO, validated against direct objectives, searched by local heuristics, compared against an objective-equivalent CP-SAT optimum, and transformed into an energy-consistent Ising representation.

These are prototype and pilot validation results. They should not be interpreted as final solver benchmarks or quantum-computing hardware results.

## Next Steps

Recommended next steps include:

1. Add runtime and memory profiling for sparse export, merge, validation, and local search.
2. Add seed-specific sample_4x4 QUBO exports.
3. Improve local search neighborhoods for timing optimization.
4. Add QUBO/Ising scaling exports for external solvers.
5. Test small instances with external QUBO or annealing-style samplers.
6. Develop a manuscript-oriented experimental design after prototype validation stabilizes.
