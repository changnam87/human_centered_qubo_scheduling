# Small Time-Indexed External Solver Package Manifest

## Purpose

This step creates a compact external-solver-ready QUBO/Ising package for a small time-indexed scheduling instance.

The purpose is to provide a lightweight package for testing external QUBO, Ising, simulated annealing, quantum annealing style, or QAOA-oriented solvers.

## Important Note

This package is intentionally small. It is not the full sample_4x4 QUBO.

## Package Directory

exports/small_time_indexed_solver_package/

## Included Files

exports/small_time_indexed_solver_package/README.md
exports/small_time_indexed_solver_package/package_metadata.json
exports/small_time_indexed_solver_package/qubo_coefficients.csv
exports/small_time_indexed_solver_package/qubo_coefficients_scaled_unit_abs.csv
exports/small_time_indexed_solver_package/ising_linear_fields.csv
exports/small_time_indexed_solver_package/ising_couplers.csv
exports/small_time_indexed_solver_package/energy_validation.csv
exports/small_time_indexed_solver_package/energy_validation_summary.json

## Script

scripts/package_small_time_indexed_solver_ready_export.py

## Validation

The package validates QUBO and Ising energy consistency on sampled assignments.

This enables external solver testing without requiring the full sample_4x4 large coefficient artifacts.
