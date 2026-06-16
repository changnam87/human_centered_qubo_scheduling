# Project Milestone v0.2 Progress Summary

## Project

Human-Centered QUBO Scheduling

## Status

```text
v0.2 progress checkpoint
```

This document summarizes the current progress toward the v0.2 milestone.

The v0.2 roadmap focuses on solver-readiness, scaled coefficient exports, dimod compatibility, tiny quantum-oriented workflows, improved local search neighborhoods, seed-specific summaries, and benchmark templates.

## Completed v0.2 Items So Far

Completed items:

```text
1. Scaled QUBO/Ising export validation for the small package
2. dimod-compatible BQM-style export for the small package
3. dimod-style BQM energy validation
4. actual dimod BinaryQuadraticModel import smoke test
5. documentation updates for scaled exports and dimod import validation
```

## Small Package Current Status

The small external-solver-ready package is located at:

```text
exports/small_time_indexed_solver_package/
```

It currently includes:

```text
raw QUBO coefficients
scaled QUBO coefficients
Ising linear fields and couplers
scaled Ising linear fields and couplers
dimod-style BINARY BQM JSON
dimod-style SPIN BQM JSON
dimod-style linear/quadratic CSV exports
energy validation outputs
brute-force solver benchmark
simulated annealing solver benchmark
simulated annealing parameter sensitivity benchmark
actual dimod import smoke-test result
```

## Scaled QUBO/Ising Export Validation

Scaled export validation result:

```text
num_variables = 15
num_assignments_enumerated = 32768
scale_mode = unit_abs_max
abs_max_before_scaling = 959.2
scale_factor approximately 0.0010425354
best_unscaled_bitstring = 100000000000100
best_scaled_qubo_bitstring = 100000000000100
best_scaled_ising_bitstring = 100000000000100
unscaled best energy = 5.30
scaled QUBO best energy approximately 0.00552544
scaled Ising best energy approximately 0.00552544
scaled QUBO-vs-Ising max_abs_error approximately 7.1e-15
validation_status = PASS
```

Interpretation: positive coefficient scaling preserved the optimum assignment and QUBO/Ising energy consistency for the small package.

## dimod-Style BQM Export and Validation

The small package includes dimod-style BQM exports:

```text
small_time_indexed_dimod_binary_bqm.json
small_time_indexed_dimod_spin_bqm.json
small_time_indexed_dimod_binary_linear.csv
small_time_indexed_dimod_binary_quadratic.csv
small_time_indexed_dimod_spin_linear.csv
small_time_indexed_dimod_spin_quadratic.csv
```

Energy validation result:

```text
num_variables = 15
num_samples = 23
max_abs_error approximately 9.09e-13
mean_abs_error_binary_vs_spin_bqm approximately 1.15e-13
validation_status = PASS
```

Interpretation: original QUBO, original Ising, dimod-style BINARY BQM, and dimod-style SPIN BQM energy representations are numerically consistent on sampled assignments.

## Actual dimod Import Smoke Test

After installing dimod, the dimod import smoke test passed.

Observed result:

```text
status = PASS
dimod_version = 0.12.22
num_variables = 15
num_samples = 23
binary_num_variables = 15
spin_num_variables = 15
binary_num_interactions = 90
spin_num_interactions = 90
max_abs_error approximately 4.55e-13
```

Interpretation: the BINARY and SPIN BQM-style JSON files can be imported into actual dimod BinaryQuadraticModel objects and evaluated consistently.

This is local software validation only. It does not run D-Wave hardware, quantum annealing, or QAOA.

## Existing Solver Benchmark Context

The small package solver benchmark summary remains:

```text
brute-force optimum = 5.30
best bitstring = 100000000000100
initial simulated annealing success_rate = 0.14
best tuned simulated annealing success_rate = 0.725
success-rate improvement = 0.585
```

## Remaining v0.2 Items

Remaining roadmap items include:

```text
tiny Qiskit/QAOA-oriented package export
Qiskit Optimization smoke test on a tiny package
optional QAOA simulator toy experiment
improved sample_4x4 local search neighborhoods for timing gap reduction
seed-specific sample_4x4 QUBO export summaries
external solver benchmark template
v0.2 final documentation checkpoint
```

## What This Checkpoint Demonstrates

This v0.2 progress checkpoint demonstrates that the small external package is now more than a static coefficient export.

It supports scaled coefficients, BINARY and SPIN BQM-style formats, manual energy validation, actual dimod import, brute-force benchmarking, and simulated annealing benchmarking.

## What This Checkpoint Does Not Claim

This checkpoint does not claim:

```text
D-Wave hardware execution
quantum annealing hardware execution
QAOA execution
quantum advantage
large-scale solver benchmark conclusions
```

## v0.2 Progress Conclusion

The v0.2 milestone has made strong progress on solver-format readiness. The small package now has validated scaled exports and actual dimod import compatibility, providing a clean bridge from internal QUBO/Ising validation toward external solver workflows.

---

## Addendum: Tiny Qiskit Optimization Smoke Test PASS

The tiny QAOA-ready package was validated with Qiskit Optimization after installing qiskit-optimization.

The smoke test built a QuadraticProgram from the tiny qiskit_qubo.json file and enumerated all 64 assignments.

The result was PASS.

```text
num_variables = 6
num_assignments_enumerated = 64
best_manual_bitstring = 101001
best_qiskit_bitstring = 101001
best_energy = 4.0
max_abs_error = 0.0
```

This confirms Qiskit Optimization compatibility for the tiny package while still not executing QAOA, a quantum simulator, or quantum hardware.

---

## Addendum: Tiny Qiskit Classical Optimizer PASS

After installing qiskit-algorithms, the tiny QAOA-ready package was solved through MinimumEigenOptimizer with NumPyMinimumEigensolver.

The result was PASS.

```text
solver_name = MinimumEigenOptimizer_NumPyMinimumEigensolver
solver_status = OptimizationResultStatus.SUCCESS
known_best_bitstring = 101001
known_best_energy = 4.0
solver_best_bitstring = 101001
solver_best_energy = 4.0
abs_error_solver_vs_known = 0.0
```

This confirms that the tiny package can be solved through a classical Qiskit Optimization exact-solver path before attempting any QAOA-oriented experiment.

This does not run QAOA, a quantum simulator, or quantum hardware.
