# Project Milestone v0.2 Current Overall Checkpoint

## Project

Human-Centered QUBO Scheduling

## Status

```text
v0.2 current overall checkpoint
```

This document summarizes the current v0.2 progress across two solver-readiness tracks:

```text
1. small external-solver-ready package
2. tiny Qiskit/QAOA-oriented package
```

This checkpoint is not a final paper, not a production solver release, and not a quantum hardware result.

## Track 1: Small External-Solver-Ready Package

Package directory:

```text
exports/small_time_indexed_solver_package/
```

The small package supports external solver readiness testing with QUBO, Ising, scaled coefficients, dimod-style BQM exports, brute-force benchmarking, simulated annealing, and actual dimod import validation.

## Small Package Core Results

```text
num_variables = 15
brute-force optimum = 5.30
best bitstring = 100000000000100
initial simulated annealing success_rate = 0.14
best tuned simulated annealing success_rate = 0.725
success-rate improvement = 0.585
```

## Small Package Scaled Export Validation

```text
num_assignments_enumerated = 32768
scale_mode = unit_abs_max
abs_max_before_scaling = 959.2
scale_factor approximately 0.0010425354
best bitstring preserved = 100000000000100
unscaled best energy = 5.30
scaled best energy approximately 0.00552544
scaled QUBO-vs-Ising max_abs_error approximately 7.1e-15
validation_status = PASS
```

Interpretation: positive coefficient scaling preserved the optimum assignment and QUBO/Ising energy consistency.

## Small Package dimod Compatibility

The small package includes dimod-style BINARY and SPIN BQM exports.

Energy validation result:

```text
num_variables = 15
num_samples = 23
max_abs_error approximately 9.09e-13
validation_status = PASS
```

Actual dimod import result:

```text
status = PASS
dimod_version = 0.12.22
binary_num_variables = 15
spin_num_variables = 15
binary_num_interactions = 90
spin_num_interactions = 90
max_abs_error approximately 4.55e-13
```

Interpretation: the small package can be imported into actual dimod BinaryQuadraticModel objects and evaluated consistently.

## Track 2: Tiny Qiskit/QAOA-Oriented Package

Package directory:

```text
exports/tiny_qaoa_ready_package/
```

The tiny package is a deliberately small 6-variable QUBO for Qiskit Optimization and QAOA-oriented toy experiments.

## Tiny Package Core Results

```text
num_variables = 6
num_assignments_enumerated = 64
num_qubo_terms = 13
num_linear_terms = 6
num_quadratic_terms = 7
known_best_bitstring = 101001
known_best_energy = 4.0
best_is_feasible = true
```

## Qiskit Optimization Validation

The tiny package qiskit_qubo.json was converted into a Qiskit Optimization QuadraticProgram.

Observed result:

```text
status = PASS
num_assignments_enumerated = 64
best_manual_bitstring = 101001
best_qiskit_bitstring = 101001
best_manual_energy = 4.0
best_qiskit_energy = 4.0
max_abs_error = 0.0
```

## Qiskit Classical Optimizer Validation

After installing qiskit-algorithms, the tiny package was solved through a classical Qiskit Optimization exact-solver path.

Observed result:

```text
status = PASS
solver_name = MinimumEigenOptimizer_NumPyMinimumEigensolver
solver_status = OptimizationResultStatus.SUCCESS
solver_best_bitstring = 101001
solver_best_energy = 4.0
abs_error_solver_vs_known = 0.0
```

## Tiny QAOA Simulator Smoke Test

The tiny package was tested with a QAOA software/simulator path.

Observed result:

```text
status = PASS
reps = 1
maxiter = 100
seed = 123
sampler_name = StatevectorSampler
qaoa_status = OptimizationResultStatus.SUCCESS
qaoa_bitstring = 101001
qaoa_energy = 4.0
qaoa_gap_to_known = 0.0
qaoa_matches_known = true
```

## Tiny QAOA Parameter Sensitivity

The QAOA toy simulator was evaluated across a small parameter grid.

```text
reps = 1, 2, 3
maxiter = 50, 100, 200
seed = 123, 456, 789, 1001, 2025
total cases = 45
```

Observed result:

```text
pass_count = 44
partial_pass_count = 1
skipped_count = 0
fail_count = 0
success_rate approximately 0.9778
```

Best selected case:

```text
tag = run000_p1_it50_s123
reps = 1
maxiter = 50
seed = 123
sampler_name = StatevectorSampler
qaoa_bitstring = 101001
qaoa_energy = 4.0
qaoa_gap_to_known = 0.0
```

## What v0.2 Has Demonstrated So Far

The current v0.2 checkpoint demonstrates:

1. The small external package supports scaled QUBO/Ising exports.
2. The small package supports dimod-style BQM exports and actual dimod import.
3. The small package supports brute-force, simulated annealing, and parameter-sensitivity solver workflows.
4. The tiny package supports Qiskit Optimization QuadraticProgram validation.
5. The tiny package supports a classical Qiskit exact-solver path.
6. The tiny package supports a QAOA software/simulator path.
7. The tiny QAOA toy simulator recovered the known optimum robustly across the tested parameter grid.

## What This Checkpoint Does Not Claim

This checkpoint does not claim:

```text
quantum hardware execution
quantum annealing hardware execution
quantum advantage
quantum speedup
sample_4x4 QAOA solution
large-scale QAOA feasibility
production-ready solver performance
paper-level final empirical claims
```

## Remaining v0.2 Directions

Remaining possible v0.2 directions include:

```text
improved sample_4x4 local search neighborhoods for timing gap reduction
seed-specific sample_4x4 QUBO export summaries
external solver benchmark template
optional additional tiny QAOA diagnostics
v0.2 final release-style documentation checkpoint
```

## Conclusion

The current v0.2 checkpoint has substantially advanced solver-format readiness and toy quantum-algorithm readiness. The project now has a validated small external solver package and a validated tiny Qiskit/QAOA software path, while maintaining clear boundaries against overclaiming quantum hardware execution or quantum advantage.
