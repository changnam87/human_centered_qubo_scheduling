# Tiny QAOA-Ready Package Export Manifest

## Purpose

This step creates a tiny QUBO package suitable for Qiskit Optimization and QAOA-oriented toy experiments.

The package is intentionally tiny to keep future QAOA simulation feasible.

## Scope

This is a toy package and not the full sample_4x4 QUBO.

This step does not run Qiskit, QAOA, quantum hardware, or a quantum simulator.

## Observed Result

The tiny package has 6 binary variables.

All 64 assignments were enumerated by brute force.

The QUBO has 13 total terms, including 6 linear terms and 7 quadratic terms.

The constant offset is 30.0.

The exactly-one penalty is 10.0.

The best bitstring is 101001.

The best energy is 4.0.

The best assignment is feasible under the exactly-one-per-pair constraints.

## Package Directory

exports/tiny_qaoa_ready_package/

## Outputs

exports/tiny_qaoa_ready_package/README.md
exports/tiny_qaoa_ready_package/package_metadata.json
exports/tiny_qaoa_ready_package/qiskit_qubo.json
exports/tiny_qaoa_ready_package/qubo_coefficients.csv
exports/tiny_qaoa_ready_package/bruteforce_energy_table.csv
results/tables/tiny_qaoa_ready_package_summary.json

## Script

scripts/export_tiny_qaoa_ready_qubo.py

## Success Criterion

The package is successfully created with a known brute-force optimum over all 64 assignments.
