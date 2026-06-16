# sample_4x4 Streaming Sparse QUBO Export Manifest

## Purpose

This pilot performs a streaming sparse QUBO coefficient export at sample_4x4 scale.

The previous feasibility study showed that dense matrix export and monolithic in-memory dictionary export are inappropriate for this scale.

This step writes sparse QUBO coefficient rows directly to CSV without storing the full QUBO dictionary in memory.

## sample_4x4 Representative Scale

jobs = 4
operations = 16
resources = 9
horizon = 63
nominal full-grid variables = 9072

## Exported QUBO Form

energy = constant + sum_i Q[i,i] x_i + sum_{i<j} Q[i,j] x_i x_j

## Streamed Term Groups

- linear_cost_and_reward
- human_target_penalty_linear
- human_target_penalty_quadratic
- assignment_penalty_linear
- assignment_penalty_quadratic
- resource_overlap_penalty
- precedence_penalty

## Scripts

scripts/export_sample_4x4_sparse_qubo_streaming.py
scripts/summarize_sample_4x4_sparse_qubo_streaming.py

## Outputs

results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv
results/tables/sample_4x4_sparse_qubo_streaming_summary.json
results/tables/sample_4x4_sparse_qubo_streaming_term_group_summary.csv
results/tables/sample_4x4_sparse_qubo_streaming_compact_summary.json

## Important Note

The streamed coefficient file is unmerged. Duplicate QUBO entries may appear across component term groups.

A later step should implement duplicate merging or component-wise energy evaluation.

## Pilot Status

This step validates streaming sparse coefficient export feasibility. It does not yet optimize the sample_4x4 QUBO.
