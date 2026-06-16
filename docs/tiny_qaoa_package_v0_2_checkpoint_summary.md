# Tiny QAOA Package v0.2 Checkpoint Summary

## Purpose

This document summarizes the v0.2 tiny Qiskit/QAOA-oriented workflow for the Human-Centered QUBO Scheduling project.

This checkpoint focuses only on the tiny 6-variable QUBO package. It is not the full sample_4x4 QUBO and not a quantum hardware result.

## Package Directory

```text
exports/tiny_qaoa_ready_package/
```

## Package Scale

```text
num_variables = 6
num_assignments_enumerated = 64
constant_offset = 30.0
num_qubo_terms = 13
num_linear_terms = 6
num_quadratic_terms = 7
exactly_one_pairs = (0,1), (2,3), (4,5)
penalty = 10.0
```

## Known Brute-Force Optimum

```text
best_bitstring = 101001
best_energy = 4.0
best_is_feasible = true
```

The known optimum was obtained by exhaustive enumeration over all 64 binary assignments.

## Workflow Completed

The tiny QAOA-oriented workflow completed the following checks:

```text
1. tiny QAOA-ready QUBO package export
2. Qiskit Optimization QuadraticProgram objective validation
3. Qiskit classical optimizer validation
4. QAOA simulator smoke test
5. QAOA parameter sensitivity
```

## Qiskit Optimization QuadraticProgram Validation

The qiskit_qubo.json file was converted into a Qiskit Optimization QuadraticProgram.

Observed result:

```text
status = PASS
num_variables = 6
num_assignments_enumerated = 64
best_manual_bitstring = 101001
best_manual_energy = 4.0
best_qiskit_bitstring = 101001
best_qiskit_energy = 4.0
max_abs_error = 0.0
```

Interpretation: the QuadraticProgram objective exactly matched manual QUBO and brute-force energies across all assignments.

## Qiskit Classical Optimizer Validation

After installing qiskit-algorithms, the tiny package was solved through a classical Qiskit Optimization exact-solver path.

Observed result:

```text
status = PASS
solver_name = MinimumEigenOptimizer_NumPyMinimumEigensolver
solver_status = OptimizationResultStatus.SUCCESS
known_best_bitstring = 101001
known_best_energy = 4.0
solver_best_bitstring = 101001
solver_best_energy = 4.0
abs_error_solver_vs_known = 0.0
```

Interpretation: the classical Qiskit exact-solver path recovered the known brute-force optimum.

## QAOA Simulator Smoke Test

A first QAOA software/simulator smoke test was run on the tiny package.

Observed result:

```text
status = PASS
num_variables = 6
reps = 1
maxiter = 100
seed = 123
sampler_name = StatevectorSampler
qaoa_status = OptimizationResultStatus.SUCCESS
known_best_bitstring = 101001
known_best_energy = 4.0
qaoa_bitstring = 101001
qaoa_energy = 4.0
qaoa_gap_to_known = 0.0
qaoa_matches_known = true
```

Interpretation: the QAOA software path successfully ran on the tiny package and recovered the known optimum under the tested toy setting.

## QAOA Parameter Sensitivity

The QAOA toy simulator was evaluated across a small parameter grid:

```text
reps = 1, 2, 3
maxiter = 50, 100, 200
seed = 123, 456, 789, 1001, 2025
total cases = 45
```

Observed result:

```text
num_cases = 45
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
status = PASS
```

Interpretation: the tiny QAOA software/simulator path was robust across the tested toy parameter grid.

## Key Scripts

```text
scripts/export_tiny_qaoa_ready_qubo.py
scripts/run_tiny_qiskit_optimization_smoke_test.py
scripts/run_tiny_qiskit_classical_optimizer_smoke_test.py
scripts/run_tiny_qaoa_simulator_smoke_test.py
scripts/run_tiny_qaoa_parameter_sensitivity.py
```

## Key Result Files

```text
results/tables/tiny_qaoa_ready_package_summary.json
results/tables/tiny_qiskit_optimization_smoke_test_summary.json
results/tables/tiny_qiskit_classical_optimizer_smoke_test_summary.json
results/tables/tiny_qaoa_simulator_smoke_test_summary.json
results/tables/tiny_qaoa_parameter_sensitivity_best.json
results/tables/tiny_qaoa_parameter_sensitivity_summary.csv
```

## What This Checkpoint Demonstrates

This checkpoint demonstrates that the tiny QUBO package can move through a complete software path:

```text
tiny QUBO export
    -> Qiskit Optimization QuadraticProgram validation
    -> classical Qiskit exact-solver validation
    -> QAOA simulator smoke test
    -> QAOA toy parameter sensitivity
```

## What This Checkpoint Does Not Claim

This checkpoint does not claim:

```text
quantum hardware execution
quantum advantage
quantum speedup
sample_4x4 QAOA solution
large-scale QAOA feasibility
paper-level QAOA performance claims
```

## Conclusion

The v0.2 tiny QAOA package checkpoint validates the Qiskit/QAOA-oriented software path on a deliberately small 6-variable QUBO. The workflow is now ready for carefully labeled toy QAOA experiments, while larger sample_4x4 QAOA execution remains out of scope at this checkpoint.
