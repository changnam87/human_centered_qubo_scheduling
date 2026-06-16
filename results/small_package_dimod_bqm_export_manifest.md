# Small Package dimod-Compatible BQM Export Manifest

## Purpose

This step exports the small external-solver-ready QUBO/Ising package into dimod-compatible BQM-style files.

The purpose is to prepare the small package for D-Wave Ocean/dimod-style workflows without requiring dimod or running quantum hardware.

## Scope

This export is for the small 15-variable package only.

It is not the full sample_4x4 QUBO.

## Outputs

exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_bqm.json
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_bqm.json
exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_linear.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_binary_quadratic.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_linear.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_spin_quadratic.csv
exports/small_time_indexed_solver_package/small_time_indexed_dimod_bqm_export_summary.json

## Script

scripts/export_small_package_dimod_bqm.py

## Important Note

This is a solver-format readiness step. It does not execute D-Wave hardware, quantum annealing, or QAOA.
