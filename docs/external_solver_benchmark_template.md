# External Solver Benchmark Template

## Purpose

This document defines a standard schema for recording external solver benchmark results in the Human-Centered QUBO Scheduling project.

The goal is to make future solver results comparable across QUBO, Ising, BQM, Qiskit Optimization, QAOA simulator, simulated annealing, and possible hardware-oriented workflows.

## Scope

This is a benchmark reporting template only.

It does not run any solver and does not imply quantum hardware execution or quantum advantage.

## Core Schema Files

```text
results/tables/external_solver_benchmark_schema.csv
results/tables/external_solver_benchmark_schema.json
results/tables/external_solver_benchmark_template_example.csv
```

## Required Benchmark Columns

The benchmark schema includes the following fields:

```text
experiment_id
instance_id
package_dir
problem_family
formulation_type
vartype
solver_name
solver_backend
solver_version
run_type
num_variables
num_linear_terms
num_quadratic_terms
num_constraints_original
reference_solver
reference_energy
reference_bitstring
best_energy
best_bitstring
gap_to_reference
relative_gap_to_reference
feasible
constraint_violation_count
num_reads_or_restarts
iterations_or_maxiter
qaoa_reps
seed
runtime_seconds
success_count
success_rate
status
notes
```

## Recommended Status Values

```text
PASS
PARTIAL_PASS
FAIL
SKIPPED
FALLBACK_PASS
```

## Recommended Run Types

```text
bruteforce
classical_exact
simulated_annealing
qaoa_simulator
dimod_import
hardware
format_validation
```

## Example Rows

The example benchmark table includes representative rows for:

```text
tiny QUBO brute-force reference
tiny QAOA simulator sensitivity best case
small package simulated annealing sensitivity best case
```

## Interpretation Rules

Benchmark results should clearly separate:

```text
classical brute-force references
classical exact solver results
classical heuristic results
QAOA simulator results
format validation results
hardware results, if ever added
```

QAOA simulator results should not be described as quantum hardware execution.

Hardware results should not be claimed unless an actual hardware backend is used and clearly documented.

Quantum advantage or quantum speedup should not be claimed without rigorous comparative benchmarking.

## Recommended Usage

For each new solver experiment, create a row that includes:

```text
instance_id
solver_name
run_type
reference_energy
best_energy
gap_to_reference
success_rate
status
notes
```

The benchmark schema is intentionally broad so that both small toy experiments and future larger classical or quantum-oriented solver experiments can be recorded consistently.
