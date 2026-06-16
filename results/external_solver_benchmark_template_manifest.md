# External Solver Benchmark Template Manifest

## Purpose

This step creates a standard benchmark schema and example table for future external solver experiments.

## Scope

This is a reporting and documentation step only.

It does not run any solver, quantum simulator, quantum hardware, or quantum annealer.

## Files

docs/external_solver_benchmark_template.md
scripts/create_external_solver_benchmark_template.py
results/tables/external_solver_benchmark_schema.csv
results/tables/external_solver_benchmark_schema.json
results/tables/external_solver_benchmark_template_example.csv

## Intended Use

Future solver results should use this schema to record solver name, backend, formulation type, reference energy, best energy, gap, feasibility, runtime, success rate, and status.
