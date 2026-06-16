# Project Milestone v0.1 Summary

## Project

Human-Centered QUBO Scheduling

## Milestone Status

```text
v0.1 prototype/pilot validation milestone
```

This milestone summarizes the current validated state of the human-centered QUBO/Ising scheduling prototype.

This is not a final manuscript, not a production solver release, and not a quantum hardware result.

## Purpose of v0.1

The purpose of this milestone is to document that the project has successfully validated an end-to-end prototype path from human-centered scheduling formulation to sparse QUBO/Ising artifacts, classical baselines, local heuristic search, and small external solver package tests.

## Validated sample_4x4 Pipeline

The main representative instance is sample_4x4:

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

The validated sample_4x4 workflow is:

```text
human-centered scheduling formulation
    -> QUBO-compatible squared target human-utilization penalty
    -> time-indexed sparse QUBO export
    -> streamed QUBO energy validation
    -> duplicate-merged compact sparse QUBO
    -> merged QUBO energy validation
    -> solver-ready sparse QUBO metadata
    -> local QUBO heuristic search
    -> objective-equivalent CP-SAT comparison
    -> tuned local QUBO search gap analysis
    -> QUBO-to-Ising metadata
    -> Ising energy validation
    -> runtime and artifact profile
```

## sample_4x4 Headline Results

```text
num_variables = 8713
merged QUBO terms = 8218171
quadratic density approximately 0.2163
CP-SAT squared-target optimum = 47.70
initial local QUBO best = 51.25
tuned local QUBO best = 48.20
remaining gap = 0.50
relative gap approximately 1.05 percent
Ising validation max_abs_error = 0.0
```

The tuned local QUBO solution matched the CP-SAT squared-target optimum in human_count, workload cost, ergonomic cost, reward term, and target penalty.

The remaining 0.50 gap was entirely explained by start-time cost.

## sample_4x4 Engineering Profile

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

Large coefficient files are intentionally kept as local ignored artifacts.

## Small External Solver Package

v0.1 also includes a compact external-solver-ready package:

```text
exports/small_time_indexed_solver_package/
```

This package is intentionally small and separate from the full sample_4x4 QUBO.

It includes raw QUBO coefficients, scaled QUBO coefficients, Ising linear fields, Ising couplers, package metadata, and energy validation outputs.

## Small Package Solver Benchmark Results

The small package has been tested with brute-force enumeration and simulated annealing.

```text
num_variables = 15
brute-force assignments enumerated = 32768
brute-force optimum = 5.30
best bitstring = 100000000000100
QUBO-vs-Ising max_abs_error approximately 1.14e-12
```

Initial simulated annealing baseline:

```text
restarts = 100
iterations per restart = 2000
success_count = 14 / 100
success_rate = 0.14
```

Best simulated annealing sensitivity case:

```text
run_id = 214
tag = run214_r200_it10000_t20.0_tf0.01_s456
restarts = 200
iterations per restart = 10000
initial_temperature = 20.0
final_temperature = 0.01
seed = 456
success_count = 145 / 200
success_rate = 0.725
```

The simulated annealing success rate improved from 0.14 to 0.725 after parameter sensitivity.

## Key Documentation Files

```text
README.md
docs/sample_4x4_qubo_pilot_technical_validation_report.md
docs/sample_4x4_reproducibility_workflow.md
results/sample_4x4_current_release_checkpoint_summary.md
results/current_pilot_checkpoint.md
```

## Key Result Summary Files

```text
results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json
results/tables/sample_4x4_cpsat_squared_target_summary.json
results/tables/sample_4x4_local_search_parameter_sensitivity_best.json
results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json
results/tables/sample_4x4_qubo_to_ising_metadata_summary.json
results/tables/sample_4x4_ising_energy_validation_summary.json
results/tables/sample_4x4_runtime_memory_profile_summary.json
results/tables/small_external_package_solver_benchmark_summary.json
```

## What v0.1 Demonstrates

This milestone demonstrates:

1. Human-centered scheduling objectives can be expressed in a QUBO-compatible form using a squared target human-utilization penalty.
2. Time-indexed scheduling QUBOs can be exported as streamed and merged sparse coefficient files.
3. Sparse QUBO energy can be validated against direct representative objective calculations.
4. A solver-ready sparse QUBO can support local energy-based heuristic search.
5. Objective-equivalent CP-SAT provides a meaningful comparison point.
6. Local QUBO search can be tuned to produce near-optimal feasible target-consistent solutions on sample_4x4.
7. QUBO-to-Ising conversion can be validated for energy consistency.
8. A compact small package can support external solver tests, brute-force enumeration, and simulated annealing sensitivity.

## What v0.1 Does Not Claim

This milestone does not claim:

```text
quantum hardware execution
quantum annealing hardware execution
QAOA simulation or execution
global optimality of the local QUBO heuristic
full benchmark-level solver comparison across many instances
paper-level final empirical claims
```

## Recommended Next Milestone

Recommended v0.2 directions:

1. Add scaled QUBO/Ising export formats for external solvers.
2. Add dimod-compatible BQM export for the small package.
3. Add Qiskit Optimization or QAOA-oriented toy execution on the small package.
4. Add seed-specific sample_4x4 QUBO exports.
5. Improve local search neighborhood moves for timing optimization.
6. Add a formal experiment plan for manuscript-oriented benchmarking.

## v0.1 Conclusion

The v0.1 milestone establishes a strong prototype foundation for human-centered QUBO/Ising scheduling. The project now has validated formulation logic, sparse QUBO engineering, CP-SAT comparison, local heuristic search, Ising conversion validation, reproducibility documentation, and a small external-solver-ready package with solver baselines.

---

## Addendum: dimod-Style BQM Export and Validation

The small external-solver-ready package now includes dimod-compatible BQM-style exports for BINARY and SPIN formulations.

The exported BQM-style JSON files were validated without requiring dimod.

The validation compared original QUBO energy, original Ising energy, dimod-style BINARY BQM energy, and dimod-style SPIN BQM energy.

The validation used 23 sampled assignments and passed with max_abs_error approximately 9.09e-13.

This confirms solver-format energy consistency for the small package while still not representing D-Wave hardware, quantum annealing, or QAOA execution.

---

## Addendum: Scaled QUBO/Ising Export Validation

The small external-solver-ready package now includes validated scaled QUBO and Ising exports.

The validation used unit_abs_max scaling and enumerated all 32,768 assignments for the 15-variable package.

The unscaled, scaled QUBO, and scaled Ising formulations all preserved the same best bitstring 100000000000100.

The unscaled best energy was 5.30, while the scaled best energy was approximately 0.00552544.

The scaled QUBO-vs-Ising maximum absolute error was approximately 7.1e-15, with validation status PASS.

This strengthens solver-format readiness for the small package.
