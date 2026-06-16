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

## Runtime and Artifact Profile

The sample_4x4 prototype includes a compact engineering profile summarizing runtime and artifact sizes.

Key runtime observations:

```text
streaming sparse QUBO export = approximately 21.39 seconds
streamed QUBO energy validation = approximately 5.23 seconds
duplicate merge = approximately 10.30 seconds
merged QUBO energy validation = approximately 3.58 seconds
local QUBO initial search load = approximately 3.15 seconds
```

Large local artifact sizes:

```text
streamed QUBO coefficients CSV = approximately 800.64 MB
merged QUBO coefficients CSV = approximately 112.25 MB
Ising couplers CSV = approximately 117.79 MB
Ising linear fields CSV = approximately 0.12 MB
```

These results show that the prototype can handle sample_4x4-scale sparse QUBO and Ising artifacts locally, but the largest coefficient files should remain ignored artifacts rather than tracked Git files.

The runtime and artifact profile is summarized in:

```text
results/tables/sample_4x4_runtime_memory_profile_summary.json
results/tables/sample_4x4_runtime_memory_profile_summary.csv
results/tables/sample_4x4_large_artifact_size_summary.csv
results/sample_4x4_runtime_memory_profile_manifest.md
```

## Reproducibility Workflow

A sample_4x4 reproducibility workflow is available at:

```text
docs/sample_4x4_reproducibility_workflow.md
```

An artifact presence checker is available at:

```bash
python scripts/check_sample_4x4_reproducibility_artifacts.py
```

## Small External Solver Package

A compact external-solver-ready QUBO/Ising package is available at:

```text
exports/small_time_indexed_solver_package/
```

This package is intentionally small and is not the full sample_4x4 QUBO.

It includes:

```text
qubo_coefficients.csv
qubo_coefficients_scaled_unit_abs.csv
ising_linear_fields.csv
ising_couplers.csv
package_metadata.json
energy_validation.csv
energy_validation_summary.json
README.md
```

This package can be used as a lightweight input for external QUBO, Ising, simulated annealing, quantum-annealing-style, or QAOA-oriented solver tests.

## Small External Solver Smoke Test

A minimal brute-force smoke test is available at:

```bash
python scripts/run_small_external_solver_smoke_test.py
```

The smoke test reads the exported small QUBO/Ising package, enumerates all binary assignments, identifies the minimum-energy assignment, and validates QUBO-vs-Ising energy consistency.

Observed smoke-test result:

```text
num_variables = 15
num_assignments_enumerated = 32768
best_bitstring = 100000000000100
best_qubo_energy = 5.30
best_ising_energy = 5.30
max_abs_error_qubo_vs_ising approximately 1.14e-12
validation_status = PASS
```

This confirms that the small exported package can be consumed as a valid external QUBO/Ising solver input.

Smoke-test outputs are stored in:

```text
results/tables/small_external_solver_smoke_test_result.csv
results/tables/small_external_solver_smoke_test_summary.json
results/small_external_solver_smoke_test_manifest.md
```

## Small External Solver Baselines

The small external-solver-ready package has two completed baseline checks.

### Brute-force smoke test

The brute-force smoke test enumerates all assignments for the 15-variable package.

```text
num_variables = 15
num_assignments_enumerated = 32768
best_bitstring = 100000000000100
best_qubo_energy = 5.30
best_ising_energy = 5.30
max_abs_error_qubo_vs_ising approximately 1.14e-12
validation_status = PASS
```

### Simulated annealing baseline

A minimal bit-flip simulated annealing solver was also tested on the same exported QUBO package.

```text
restarts = 100
iterations per restart = 2000
initial_temperature = 10.0
final_temperature = 0.001
brute_force_optimum = 5.30
SA best_energy = 5.30
best_bitstring = 100000000000100
best_gap_to_bruteforce approximately 8.88e-16
success_count = 14 / 100
success_rate = 0.14
validation_status = PASS
```

These results confirm that the compact package can be consumed by both exhaustive and heuristic QUBO-style solvers. The simulated annealing result also shows that solver performance is stochastic: the optimum was recovered in 14 percent of restarts under the tested settings.

Relevant scripts:

```text
scripts/run_small_external_solver_smoke_test.py
scripts/run_small_external_package_sa_solver.py
```

Relevant outputs:

```text
results/tables/small_external_solver_smoke_test_summary.json
results/tables/small_external_package_sa_solver_summary.json
```

## Small External Package SA Parameter Sensitivity

The small external-solver-ready QUBO package was also used for simulated annealing parameter sensitivity.

The experiment evaluated 216 parameter cases across restarts, iterations, temperature schedules, and random seeds.

Reference optimum:

```text
brute_force_optimum = 5.30
brute_force_bitstring = 100000000000100
```

Initial SA baseline:

```text
restarts = 100
iterations per restart = 2000
success_count = 14 / 100
success_rate = 0.14
```

Best sensitivity case:

```text
run_id = 214
tag = run214_r200_it10000_t20.0_tf0.01_s456
restarts = 200
iterations per restart = 10000
initial_temperature = 20.0
final_temperature = 0.01
seed = 456
best_energy = 5.30
best_bitstring = 100000000000100
success_count = 145 / 200
success_rate = 0.725
validation_status = PASS
```

This shows that the small external package supports heuristic solver sensitivity experiments. Parameter tuning improved the simulated annealing optimum-recovery rate from 0.14 to 0.725 under the tested settings.

Relevant outputs:

```text
results/tables/small_external_package_sa_parameter_sensitivity_summary.csv
results/tables/small_external_package_sa_parameter_sensitivity_best.json
results/small_external_package_sa_parameter_sensitivity_manifest.md
```

## Small External Package Solver Benchmark Summary

A compact solver benchmark summary is available for the small external-solver-ready QUBO/Ising package.

The summary consolidates three solver results:

```text
1. brute-force exhaustive enumeration
2. initial simulated annealing baseline
3. best simulated annealing parameter sensitivity case
```

Benchmark headline results:

```text
num_variables = 15
brute_force_optimum = 5.30
brute_force_bitstring = 100000000000100
initial_sa_success_rate = 0.14
best_tuned_sa_success_rate = 0.725
success_rate_improvement = 0.585
```

Interpretation: the small external package supports both exhaustive and heuristic solver workflows. Parameter tuning improved simulated annealing optimum-recovery rate from 0.14 to 0.725 under the tested settings.

Relevant benchmark outputs:

```text
results/tables/small_external_package_solver_benchmark_summary.csv
results/tables/small_external_package_solver_benchmark_summary.json
results/small_external_package_solver_benchmark_summary_manifest.md
```

## Project Milestone v0.1

A v0.1-style milestone summary is available at:

```text
docs/project_milestone_v0_1_summary.md
```

This summary consolidates the current sample_4x4 prototype pipeline, small external solver package, solver benchmark results, known limitations, and recommended v0.2 directions.

## dimod-Style BQM Export and Validation

The small external-solver-ready package now includes dimod-compatible BQM-style exports for both BINARY and SPIN formulations.

These exports are designed for D-Wave Ocean/dimod-style workflows, but they do not require dimod to be installed and do not execute quantum hardware.

Exported files include:

```text
exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_bqm.json
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_bqm.json
exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_linear.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_quadratic.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_linear.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_quadratic.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_bqm_export_summary.json
```

The dimod-style BQM energy validation compared:

```text
1. original QUBO energy
2. original Ising energy
3. dimod-style BINARY BQM energy
4. dimod-style SPIN BQM energy
```

Observed validation result:

```text
num_variables = 15
num_samples = 23
max_abs_error approximately 9.09e-13
mean_abs_error_binary_vs_spin_bqm approximately 1.15e-13
validation_status = PASS
```

This confirms numerical energy consistency of the dimod-style BQM JSON exports.

Relevant validation outputs:

```text
results/tables/small_package_dimod_bqm_energy_validation.csv
results/tables/small_package_dimod_bqm_energy_validation_summary.json
results/small_package_dimod_bqm_energy_validation_manifest.md
```

## Project Roadmap v0.2

A v0.2 roadmap is available at:

```text
docs/project_roadmap_v0_2.md
```

The roadmap defines the next planned milestone: scaled exports, dimod import smoke tests, tiny Qiskit/QAOA-oriented experiments, improved local search neighborhoods, seed-specific sample_4x4 summaries, and external solver benchmark templates.

## Project Milestone v0.2 Progress

A v0.2 progress checkpoint summary is available at:

```text
docs/project_milestone_v0_2_progress_summary.md
```

This document summarizes completed v0.2 progress, including scaled QUBO/Ising export validation and actual dimod BinaryQuadraticModel import compatibility for the small external package.

## Tiny Qiskit Optimization Smoke Test

The tiny QAOA-ready package was validated with Qiskit Optimization after installing qiskit-optimization in the active environment.

The test built a Qiskit Optimization QuadraticProgram from:

```text
exports/tiny_qaoa_ready_package/qiskit_qubo.json
```

Observed result:

```text
status = PASS
num_variables = 6
num_assignments_enumerated = 64
best_manual_bitstring = 101001
best_manual_energy = 4.0
best_qiskit_bitstring = 101001
best_qiskit_energy = 4.0
known_metadata_best_bitstring = 101001
known_metadata_best_energy = 4.0
max_abs_error = 0.0
num_qp_variables = 6
```

This confirms that the tiny QUBO package is compatible with Qiskit Optimization QuadraticProgram objective evaluation.

This is not a QAOA run and does not execute a quantum simulator or quantum hardware.

Relevant outputs:

```text
results/tables/tiny_qiskit_optimization_smoke_test_summary.json
results/tables/tiny_qiskit_optimization_smoke_test.csv
results/tiny_qiskit_optimization_smoke_test_manifest.md
```

## Tiny Qiskit Classical Optimizer Smoke Test

The tiny QAOA-ready package was also tested with a classical Qiskit Optimization solver path after installing qiskit-algorithms.

The successful solver path was:

```text
MinimumEigenOptimizer + NumPyMinimumEigensolver
```

Observed result:

```text
status = PASS
solver_name = MinimumEigenOptimizer_NumPyMinimumEigensolver
solver_status = OptimizationResultStatus.SUCCESS
num_variables = 6
known_best_bitstring = 101001
known_best_energy = 4.0
solver_best_bitstring = 101001
solver_best_energy = 4.0
abs_error_solver_vs_known = 0.0
```

CplexOptimizer remained unavailable because the CPLEX optional dependency was not installed, but the NumPyMinimumEigensolver path successfully recovered the known optimum.

This is a classical Qiskit Optimization validation step. It does not run QAOA, a quantum simulator, or quantum hardware.

Relevant outputs:

```text
results/tables/tiny_qiskit_classical_optimizer_smoke_test_summary.json
results/tables/tiny_qiskit_classical_optimizer_smoke_test.csv
results/tiny_qiskit_classical_optimizer_smoke_test_manifest.md
```
