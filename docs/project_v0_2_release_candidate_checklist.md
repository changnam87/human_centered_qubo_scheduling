# Project v0.2 Release Candidate Checklist

## Project

Human-Centered QUBO Scheduling

## Checklist Status

```text
v0.2 release candidate preparation checklist
```

This checklist summarizes what should be verified before declaring a v0.2 release-style checkpoint.

The v0.2 release candidate should represent a clean, reproducible, solver-ready prototype checkpoint.

It should not be described as a production solver, final manuscript, quantum hardware result, or quantum advantage demonstration.

## 1. Repository Cleanliness

Required checks:

```bash
git status --short
git log --oneline -8
```

Expected result:

```text
git status --short should return no output before tagging or archiving.
origin/main should match local HEAD.
```

## 2. Core Documentation Present

Required files:

```text
README.md
docs/project_milestone_v0_1_summary.md
docs/project_roadmap_v0_2.md
docs/project_milestone_v0_2_progress_summary.md
docs/project_milestone_v0_2_current_overall_checkpoint.md
docs/tiny_qaoa_package_v0_2_checkpoint_summary.md
docs/external_solver_benchmark_template.md
docs/sample_4x4_qubo_pilot_technical_validation_report.md
docs/sample_4x4_reproducibility_workflow.md
```

Verification command:

```bash
ls -lh README.md docs/project_milestone_v0_1_summary.md docs/project_roadmap_v0_2.md docs/project_milestone_v0_2_progress_summary.md docs/project_milestone_v0_2_current_overall_checkpoint.md docs/tiny_qaoa_package_v0_2_checkpoint_summary.md docs/external_solver_benchmark_template.md docs/sample_4x4_qubo_pilot_technical_validation_report.md docs/sample_4x4_reproducibility_workflow.md
```

## 3. sample_4x4 Prototype Status

The v0.2 release candidate should preserve the v0.1 sample_4x4 validation baseline:

```text
num_variables = 8713
merged QUBO terms = 8218171
CP-SAT squared-target optimum = 47.70
tuned local QUBO best = 48.20
remaining gap = 0.50
Ising validation max_abs_error = 0.0
```

Key summary files:

```text
results/tables/sample_4x4_sparse_qubo_solver_ready_metadata.json
results/tables/sample_4x4_cpsat_squared_target_summary.json
results/tables/sample_4x4_local_search_parameter_sensitivity_best.json
results/tables/sample_4x4_tuned_local_qubo_solution_component_summary.json
results/tables/sample_4x4_qubo_to_ising_metadata_summary.json
results/tables/sample_4x4_ising_energy_validation_summary.json
results/tables/sample_4x4_runtime_memory_profile_summary.json
```

## 4. Small External-Solver Package Status

Package directory:

```text
exports/small_time_indexed_solver_package/
```

Expected capabilities:

```text
raw QUBO coefficients
scaled QUBO/Ising coefficients
Ising h/J exports
dimod-style BINARY and SPIN BQM JSON exports
actual dimod BinaryQuadraticModel import PASS
brute-force benchmark
simulated annealing benchmark
simulated annealing parameter sensitivity
solver benchmark summary
```

Headline values:

```text
num_variables = 15
brute-force optimum = 5.30
best bitstring = 100000000000100
best tuned SA success_rate = 0.725
dimod import status = PASS
dimod max_abs_error approximately 4.55e-13
```

Key summary files:

```text
results/tables/small_external_package_solver_benchmark_summary.json
results/tables/small_package_scaled_export_validation_summary.json
results/tables/small_package_dimod_bqm_energy_validation_summary.json
results/tables/small_package_dimod_import_smoke_test_summary.json
```

## 5. Tiny Qiskit/QAOA Package Status

Package directory:

```text
exports/tiny_qaoa_ready_package/
```

Expected capabilities:

```text
tiny QUBO package export
brute-force optimum table
Qiskit Optimization QuadraticProgram validation PASS
Qiskit classical optimizer PASS
QAOA simulator smoke test PASS
QAOA parameter sensitivity complete
```

Headline values:

```text
num_variables = 6
known_best_bitstring = 101001
known_best_energy = 4.0
Qiskit Optimization max_abs_error = 0.0
Qiskit classical optimizer solver = MinimumEigenOptimizer_NumPyMinimumEigensolver
QAOA smoke test qaoa_gap_to_known = 0.0
QAOA sensitivity success_rate approximately 0.9778
```

Key summary files:

```text
results/tables/tiny_qaoa_ready_package_summary.json
results/tables/tiny_qiskit_optimization_smoke_test_summary.json
results/tables/tiny_qiskit_classical_optimizer_smoke_test_summary.json
results/tables/tiny_qaoa_simulator_smoke_test_summary.json
results/tables/tiny_qaoa_parameter_sensitivity_best.json
```

## 6. Benchmark Template Status

Required files:

```text
docs/external_solver_benchmark_template.md
results/tables/external_solver_benchmark_schema.csv
results/tables/external_solver_benchmark_schema.json
results/tables/external_solver_benchmark_template_example.csv
```

The benchmark template should clearly separate:

```text
classical exact results
classical heuristic results
format validation results
QAOA simulator results
hardware results, if ever added
```

## 7. Large Artifact Policy

Large coefficient artifacts should remain local ignored files unless intentionally moved to release assets, Git LFS, or external archival storage.

Expected large local artifacts include:

```text
sample_4x4 streamed sparse QUBO coefficient CSV
sample_4x4 merged sparse QUBO coefficient CSV
sample_4x4 Ising coupler CSV
```

Before release candidate, verify .gitignore protects large artifacts.

## 8. Claims Boundary

The v0.2 release candidate may claim:

```text
prototype formulation validation
solver-format readiness
classical benchmark baselines
dimod import compatibility
Qiskit Optimization compatibility
tiny QAOA simulator toy validation
```

The v0.2 release candidate must not claim:

```text
quantum hardware execution
quantum advantage
quantum speedup
production-ready solver performance
sample_4x4 QAOA solution
large-scale QAOA feasibility
paper-level final empirical conclusions
```

## 9. Suggested Final Verification Commands

```bash
git status --short
git log --oneline -8
python -m py_compile scripts/create_external_solver_benchmark_template.py
python -m py_compile scripts/run_tiny_qaoa_simulator_smoke_test.py
python -m py_compile scripts/run_tiny_qaoa_parameter_sensitivity.py
python -m py_compile scripts/run_tiny_qiskit_optimization_smoke_test.py
python -m py_compile scripts/run_tiny_qiskit_classical_optimizer_smoke_test.py
python -m py_compile scripts/run_small_package_dimod_import_smoke_test.py
```

## 10. Recommended Next Action

After this checklist is complete, the next step should be to create a release-style v0.2 summary document and optionally tag a v0.2 checkpoint.

## Conclusion

This checklist defines the minimum verification state for a clean v0.2 release candidate. The current project already satisfies most technical and documentation criteria, but final release-style verification should confirm clean git status, file presence, large artifact handling, and careful claims boundaries.

---

## Verification Result

The v0.2 release candidate verification script was executed and passed.

```text
overall_status = PASS
num_checks = 49
pass_count = 48
fail_count = 0
warn_count = 1
```

The release candidate readiness criterion is satisfied because fail_count = 0 and overall_status = PASS.
