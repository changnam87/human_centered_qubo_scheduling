# sample_4x4 Current Release-Style Checkpoint Summary

## Purpose

This document summarizes the current prototype checkpoint for the sample_4x4 human-centered QUBO/Ising scheduling workflow.

This is not a final paper, not a solver benchmark release, and not a quantum hardware result. It is a release-style checkpoint for the current prototype and pilot validation state.

## Current Status

The project is currently at:

```text
prototype + pilot validation
```

The current validated workflow includes:

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
    -> runtime and artifact profile summary
```

## Representative Instance

The main validated instance is sample_4x4:

```text
jobs = 4
operations per job = 4
operations = 16
machines = 4
workers = 3
robots = 2
resources = 9
planning horizon = 63
representative valid-start binary variables = 8713
```

## QUBO Scale

The merged solver-ready sparse QUBO has:

```text
num_variables = 8713
merged nonzero upper-triangular terms = 8218171
linear terms = 8713
quadratic terms = 8209458
quadratic density approximately 0.2163
constant offset = 496.0
```

## Objective-Equivalent CP-SAT Result

The objective-equivalent CP-SAT squared-target baseline used:

```text
objective = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target_human_assignments)^2
human_reward = 2.5
lambda_target = 1.0
target_human_assignments = 4
```

Result:

```text
status = OPTIMAL
adjusted objective = 47.70
total_cost_without_reward = 57.70
human_count = 4
reward_term = 10.0
target_penalty = 0.0
```

## Local QUBO Search Result

Initial local QUBO search result:

```text
best_energy = 51.25
feasible_rate = 0.95
```

After parameter sensitivity:

```text
best tuned local QUBO energy = 48.20
absolute gap to CP-SAT optimum = 0.50
relative gap approximately 1.05 percent
feasible_rate = 1.0
```

Component analysis showed that the remaining 0.50 gap was entirely due to start-time cost.

```text
CP-SAT start_time_cost = 9.40
tuned local QUBO start_time_cost = 9.90
difference = 0.50
```

The tuned local QUBO solution matched the CP-SAT optimum in human_count, workload cost, ergonomic cost, reward term, and target penalty.

## QUBO-to-Ising Validation

The QUBO-to-Ising conversion uses:

```text
s_i = 2 x_i - 1
x_i = (1 + s_i) / 2
```

Ising energy validation result:

```text
num_samples = 6
max_abs_error = 0.0
mean_abs_error = 0.0
validation_status = PASS
```

This confirms energy consistency between the merged sparse QUBO and the corresponding Ising representation on sampled assignments.

## Runtime and Artifact Profile

Runtime highlights:

```text
streaming sparse QUBO export approximately 21.39 seconds
streamed QUBO energy validation approximately 5.23 seconds
duplicate merge approximately 10.30 seconds
merged QUBO energy validation approximately 3.58 seconds
local QUBO initial search load approximately 3.15 seconds
```

Large local artifact sizes:

```text
streamed QUBO coefficients CSV approximately 800.64 MB
merged QUBO coefficients CSV approximately 112.25 MB
Ising couplers CSV approximately 117.79 MB
Ising linear fields CSV approximately 0.12 MB
```

Large coefficient files are intentionally ignored by Git and should remain local artifacts unless using Git LFS, release assets, or external artifact storage.

## Key Tracked Documentation

Important documentation files:

```text
README.md
docs/sample_4x4_qubo_pilot_technical_validation_report.md
results/current_pilot_checkpoint.md
results/sample_4x4_runtime_memory_profile_manifest.md
```

## Key Tracked Result Summaries

Important compact result summaries:

```text
results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json
results/tables/sample_4x4_cpsat_squared_target_summary.json
results/tables/sample_4x4_local_search_parameter_sensitivity_best.json
results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json
results/tables/sample_4x4_qubo_to_ising_metadata_summary.json
results/tables/sample_4x4_ising_energy_validation_summary.json
results/tables/sample_4x4_runtime_memory_profile_summary.json
```

## What Has Not Yet Been Done

The following have not yet been performed:

```text
quantum hardware execution
quantum annealing hardware execution
QAOA simulation or execution
formal solver benchmark across many benchmark instances
paper-level statistical claims for QUBO solver performance
```

## Recommended Next Steps

Recommended next prototype steps:

1. Add a small external-solver-ready export package for a smaller instance.
2. Add QUBO/Ising scaled coefficient export.
3. Improve local search neighborhoods to reduce timing cost gap.
4. Add seed-specific sample_4x4 QUBO exports.
5. Add reproducibility instructions for regenerating ignored large artifacts.
6. Prepare a paper-oriented experimental design only after the prototype workflow stabilizes.

## Current Checkpoint Conclusion

The sample_4x4 prototype now validates the full path from human-centered scheduling formulation to sparse QUBO, objective-equivalent CP-SAT comparison, near-optimal local QUBO search, QUBO-to-Ising metadata, Ising energy validation, and runtime/artifact profiling.

This is a strong prototype checkpoint, but it remains a pilot validation milestone rather than a final paper or quantum hardware result.

---

## Addendum: Small External Solver Baselines

The small external-solver-ready package now has two completed baseline checks.

Brute-force enumeration over all 32,768 assignments found best_bitstring = 100000000000100 with best QUBO energy = 5.30 and QUBO-vs-Ising max_abs_error approximately 1.14e-12.

A minimal simulated annealing solver recovered the same best energy 5.30 and best bitstring 100000000000100.

The simulated annealing run used 100 restarts and 2,000 iterations per restart, reaching the brute-force optimum in 14 out of 100 restarts.

This confirms that the small external package can be consumed by exhaustive and heuristic QUBO-style solvers.

---

## Addendum: Small External Package SA Sensitivity

The small external-solver-ready QUBO package was evaluated with a simulated annealing parameter sensitivity experiment.

The experiment evaluated 216 parameter cases.

The best case was run214_r200_it10000_t20.0_tf0.01_s456, using 200 restarts, 10,000 iterations per restart, initial_temperature = 20.0, final_temperature = 0.01, and seed = 456.

This case recovered the known brute-force optimum energy 5.30 and bitstring 100000000000100.

The optimum was reached in 145 out of 200 restarts, giving success_rate = 0.725.

This improved over the initial simulated annealing baseline success_rate of 0.14.

---

## Addendum: Small External Package Solver Benchmark Summary

A compact solver benchmark summary was created for the small external-solver-ready package.

The summary compares brute-force enumeration, the initial simulated annealing baseline, and the best tuned simulated annealing case.

The brute-force optimum was 5.30 with bitstring 100000000000100.

The initial simulated annealing baseline had success_rate = 0.14.

The best tuned simulated annealing case had success_rate = 0.725.

The success-rate improvement was 0.585.

This confirms that the small external package supports compact solver benchmarking for exhaustive and heuristic workflows.

---

## Addendum: dimod-Style BQM Export

The small external-solver-ready package now includes dimod-compatible BQM-style exports.

Both BINARY and SPIN BQM-style JSON files were generated and validated.

Energy validation across original QUBO, original Ising, dimod-style BINARY BQM, and dimod-style SPIN BQM representations passed with max_abs_error approximately 9.09e-13 across 23 sampled assignments.

This is a solver-format readiness result and does not execute dimod, D-Wave hardware, quantum annealing, or QAOA.
