# Project Roadmap v0.2

## Project

Human-Centered QUBO Scheduling

## Roadmap Status

```text
v0.2 planning roadmap
```

This document defines the recommended next milestone after the v0.1 prototype/pilot validation checkpoint.

The v0.1 milestone validated the core path from human-centered scheduling formulation to sparse QUBO export, CP-SAT comparison, local heuristic search, QUBO-to-Ising conversion, small external solver package, and dimod-style solver-format readiness.

The v0.2 milestone should focus on controlled external-solver readiness, reproducibility, scaled coefficient formats, and early quantum-oriented experiments on small instances only.

## v0.1 Baseline State

The current v0.1 checkpoint includes:

```text
sample_4x4 sparse QUBO/Ising prototype
objective-equivalent CP-SAT comparison
tuned local QUBO search
QUBO-to-Ising energy validation
runtime and artifact profile
reproducibility workflow
small external-solver-ready package
brute-force and simulated annealing solver baselines
dimod-style BQM export and energy validation
```

Representative sample_4x4 headline values:

```text
num_variables = 8713
merged QUBO terms = 8218171
CP-SAT squared-target optimum = 47.70
tuned local QUBO best = 48.20
gap = 0.50
Ising validation max_abs_error = 0.0
```

Small external package headline values:

```text
num_variables = 15
brute-force optimum = 5.30
best bitstring = 100000000000100
initial SA success_rate = 0.14
tuned SA success_rate = 0.725
dimod-style BQM validation max_abs_error approximately 9.09e-13
```

## v0.2 Main Goal

The main goal of v0.2 is to move from internal prototype validation to controlled solver-readiness experiments.

v0.2 should not yet attempt large-scale quantum hardware claims. Instead, it should prepare clean small-instance solver interfaces, reproducible benchmark scripts, scaled coefficient exports, and carefully labeled toy quantum/QAOA experiments if feasible.

## v0.2 Work Packages

## WP1: Scaled QUBO and Ising Export Formats

Purpose:

Create standardized scaled coefficient exports for external solvers with bounded coefficient ranges.

Planned outputs:

```text
exports/small_time_indexed_solver_package/scaled_qubo_unit_abs.csv
exports/small_time_indexed_solver_package/scaled_ising_unit_abs.csv
exports/small_time_indexed_solver_package/scaling_metadata.json
```

Validation:

```text
energy ordering preservation check
scaled-vs-unscaled argmin consistency on small package
coefficient range summary
```

## WP2: dimod Import Smoke Test

Purpose:

If dimod is installed, load the BINARY and SPIN BQM files into actual dimod BinaryQuadraticModel objects and verify energy consistency.

Important note:

This is still local software validation, not D-Wave hardware execution.

Planned outputs:

```text
scripts/run_small_package_dimod_import_smoke_test.py
results/tables/small_package_dimod_import_smoke_test_summary.json
```

Validation:

```text
BQM energies match existing package energies
best brute-force sample matches known optimum
```

## WP3: Qiskit Optimization / QAOA-Oriented Toy Path

Purpose:

Create a very small QUBO instance suitable for Qiskit Optimization and QAOA-oriented testing.

Important note:

This should be limited to tiny instances because QAOA simulation scales poorly.

Planned outputs:

```text
exports/tiny_qaoa_ready_package/
scripts/export_tiny_qaoa_ready_qubo.py
scripts/run_tiny_qiskit_optimization_smoke_test.py
```

Validation:

```text
brute-force optimum known
Qiskit QuadraticProgram objective matches QUBO energy
QAOA simulator result, if executed, clearly labeled as toy simulation
```

## WP4: Improved Local Search Neighborhoods for sample_4x4

Purpose:

Reduce the remaining 0.50 start-time cost gap between tuned local QUBO search and CP-SAT squared-target optimum.

Current gap explanation:

```text
CP-SAT start_time_cost = 9.40
tuned local QUBO start_time_cost = 9.90
remaining gap = 0.50
```

Candidate neighborhood moves:

```text
operation timing shift move
same-resource local timing repair
precedence-chain shift move
critical-path timing adjustment
resource-preserving reassignment plus timing repair
```

Validation:

```text
best energy compared against CP-SAT optimum 47.70
gap reduction from 0.50 toward 0.0
feasibility diagnostics retained
```

## WP5: Seed-Specific sample_4x4 QUBO Export

Purpose:

Move beyond one representative sample_4x4 QUBO export by generating seed-specific QUBO/Ising artifacts for multiple synthetic augmentation seeds.

Potential seed set:

```text
2001-2010
```

Important note:

This can generate large artifacts. The workflow should commit summaries and manifests, not large coefficient CSV files.

Planned outputs:

```text
results/tables/sample_4x4_seeded_qubo_export_summary.csv
results/tables/sample_4x4_seeded_qubo_validation_summary.csv
results/sample_4x4_seeded_qubo_export_manifest.md
```

Validation:

```text
energy validation PASS per seed
coefficient count and size summary per seed
optional local search summary per seed
```

## WP6: External Solver Benchmark Template

Purpose:

Create a clean benchmark template that can later be used for dimod, simulated annealing, tabu, classical QUBO solvers, or annealing-style samplers.

Planned outputs:

```text
scripts/benchmark_external_solver_template.py
docs/external_solver_benchmark_template.md
results/tables/external_solver_benchmark_schema.csv
```

Benchmark schema should include:

```text
instance_id
solver_name
vartype
num_variables
num_terms
best_energy
gap_to_reference
feasible
runtime_seconds
num_reads_or_restarts
success_count
success_rate
notes
```

## WP7: Documentation and Release Hygiene

Purpose:

Prepare the repository for a stable v0.2 checkpoint.

Tasks:

```text
update README
update project milestone summary
update reproducibility workflow
create v0.2 checkpoint summary
verify .gitignore large artifact rules
check clean git status
```

## Recommended v0.2 Execution Order

Recommended order:

```text
1. Scaled QUBO/Ising export for the small package
2. Energy/order validation for scaled coefficients
3. dimod import smoke test, if dimod is available
4. Tiny Qiskit/QAOA-ready package export
5. Qiskit Optimization smoke test on tiny package
6. Improved local search neighborhoods for sample_4x4 timing gap
7. Seed-specific sample_4x4 QUBO export summaries
8. External solver benchmark template
9. v0.2 documentation checkpoint
```

## v0.2 Success Criteria

The v0.2 milestone should be considered successful if:

```text
scaled exports are generated and validated
dimod-style package can be imported or at least validated with a clear fallback
a tiny Qiskit/QAOA-oriented path is created and clearly labeled
local search timing gap is reduced or its limitation is clearly characterized
seed-specific sample_4x4 export summaries are available without committing large artifacts
external solver benchmark schema is defined
documentation clearly separates prototype validation, classical baselines, toy quantum simulation, and hardware execution
```

## Boundaries and Cautions

v0.2 should continue to avoid overclaiming.

Do not claim quantum advantage, quantum speedup, or hardware validation unless actual hardware experiments are performed and properly benchmarked.

QAOA simulation, if added, should be labeled as a tiny toy simulation.

Large sample_4x4 artifacts should remain local ignored files unless moved to Git LFS, release assets, or external archival storage.

## v0.2 Roadmap Conclusion

The v0.2 roadmap focuses on making the prototype more solver-ready, reproducible, and externally testable while preserving careful boundaries around what has and has not been demonstrated.

---

## v0.2 Progress Update: Scaled QUBO/Ising Export Validation Completed

The first v0.2 work package, scaled QUBO/Ising export validation for the small external package, has been completed.

The validation enumerated all 32,768 assignments for the 15-variable package.

Using unit_abs_max scaling, the maximum absolute coefficient before scaling was 959.2 and the scale factor was approximately 0.0010425354.

The unscaled QUBO, scaled QUBO, and scaled Ising formulations all selected the same best bitstring 100000000000100.

The unscaled best energy was 5.30 and the scaled best energy was approximately 0.00552544.

The scaled QUBO-vs-Ising maximum absolute error was approximately 7.1e-15, and validation status was PASS.

This completes the scaled coefficient-format validation objective for the small package.

---

## v0.2 Progress Update: dimod Import Smoke Test PASS

The dimod import smoke test was completed after installing dimod in the active environment.

The small package BINARY and SPIN BQM-style JSON files were imported into actual dimod BinaryQuadraticModel objects.

The result was PASS with dimod_version = 0.12.22, num_variables = 15, num_samples = 23, binary_num_interactions = 90, spin_num_interactions = 90, and max_abs_error approximately 4.55e-13.

This completes the dimod import smoke-test objective for the small package.

This remains local software validation and does not run D-Wave hardware, quantum annealing, or QAOA.

---

## v0.2 Progress Checkpoint Summary

A v0.2 progress checkpoint summary has been created at:

```text
docs/project_milestone_v0_2_progress_summary.md
```

This progress checkpoint summarizes completed scaled export validation, dimod-style BQM validation, and actual dimod BinaryQuadraticModel import compatibility for the small external package.

---

## v0.2 Progress Update: Tiny Qiskit Optimization Smoke Test PASS

The tiny QAOA-ready package was validated with Qiskit Optimization.

After installing qiskit-optimization, the smoke test built a QuadraticProgram from exports/tiny_qaoa_ready_package/qiskit_qubo.json and enumerated all 64 assignments.

The result was PASS: best_manual_bitstring = 101001, best_qiskit_bitstring = 101001, best energy = 4.0, and max_abs_error = 0.0.

This completes the Qiskit Optimization smoke-test objective for the tiny package.

This remains a software validation step and does not run QAOA, a quantum simulator, or quantum hardware.

---

## v0.2 Progress Update: Tiny Qiskit Classical Optimizer PASS

The tiny QAOA-ready package was solved through a classical Qiskit Optimization path after installing qiskit-algorithms.

The successful solver path was MinimumEigenOptimizer with NumPyMinimumEigensolver.

The result was PASS: the solver recovered known_best_bitstring = 101001 with energy = 4.0 and abs_error_solver_vs_known = 0.0.

This completes the classical Qiskit exact-solver validation objective for the tiny package.

This remains classical software validation and does not run QAOA, a quantum simulator, or quantum hardware.

---

## v0.2 Progress Update: Tiny QAOA Simulator Smoke Test PASS

The tiny QAOA-ready package was tested with a QAOA software/simulator path.

The test used reps = 1, maxiter = 100, seed = 123, and StatevectorSampler.

The result was PASS: QAOA recovered the known optimum bitstring 101001 with energy 4.0 and gap_to_known = 0.0.

This completes a first tiny QAOA-oriented software smoke test.

This is a toy simulator/software result only. It does not run quantum hardware and does not imply quantum advantage.
