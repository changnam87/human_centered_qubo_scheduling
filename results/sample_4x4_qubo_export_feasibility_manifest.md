# sample_4x4 QUBO Export Feasibility Manifest

## Purpose

This pilot estimates the feasibility of exporting a sparse time-indexed QUBO at sample_4x4 scale.

The goal is not to solve the QUBO, but to estimate variable count, sparse coefficient term count, memory requirements, and dominant QUBO components.

## sample_4x4 Scale

jobs = 4
operations = 16
resources = 9
horizon = 63
nominal full-grid binary variables = 16 * 9 * 63 = 9072

## QUBO Components Estimated

1. linear cost terms
2. one-start assignment penalty terms
3. squared target human-utilization penalty terms
4. resource overlap penalty terms
5. precedence forbidden-pair terms

## Scripts

scripts/estimate_sample_4x4_qubo_export_feasibility.py

## Outputs

results/tables/sample_4x4_qubo_export_feasibility_terms.csv
results/tables/sample_4x4_qubo_export_feasibility_summary.json
results/tables/sample_4x4_qubo_export_sample_coefficients.csv

## Interpretation Template

The feasibility estimate identifies which QUBO components dominate sparse term count.

If the estimated sparse term count is moderate, full sparse CSV export may be feasible.

If the estimated sparse term count is large, streaming export and component-wise validation will be preferable to building a dense matrix or a large in-memory dictionary.

This step informs whether sample_4x4 full QUBO export should be implemented as a streaming sparse writer.

## Pilot Status

This is a coefficient-export feasibility study. It does not claim that the full sample_4x4 QUBO has been optimized.
