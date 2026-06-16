# sample_4x4 Merged QUBO Local Search Manifest

## Purpose

This pilot runs a local classical heuristic search directly on the merged sample_4x4 sparse QUBO.

The goal is to verify that the solver-ready sparse QUBO can be used for energy-based search without dense matrix construction.

This is not a proof of optimality and should not be treated as a final solver benchmark.

## Input

results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv

This large merged coefficient file is a local ignored artifact.

## Search Strategy

The heuristic uses operation-level moves.

For each move, one currently selected x[o,r,t] variable is turned off and another candidate x[o,r,t] for the same operation is turned on.

This preserves one-start-per-operation structure while allowing QUBO penalties to guide resource-overlap and precedence feasibility.

## Full Prototype Run

restarts = 20
iterations per restart = 5000
initial_temperature = 10.0
final_temperature = 0.01
seed = 123

## Observed Result

The merged QUBO contained 8,713 variables and 8,218,171 merged coefficient rows.

The QUBO loaded into the local search representation in approximately 3.15 seconds.

The best energy found was 51.25, from restart 15.

The feasible rate was 19 out of 20 restarts, or 0.95.

The best solution selected exactly 16 operations and achieved four human assignments, matching the target_human_assignments value of 4.

The best solution was feasible with respect to one-start assignment, resource overlap, and precedence diagnostics.

## Scripts

scripts/run_sample_4x4_merged_qubo_local_search.py

## Outputs

results/tables/sample_4x4_merged_qubo_local_search_runs.csv
results/tables/sample_4x4_merged_qubo_local_search_best_solution.csv
results/tables/sample_4x4_merged_qubo_local_search_summary.json

## Pilot Status

This is a prototype local search test on the merged sparse QUBO representation. It demonstrates usability of the solver-ready QUBO but does not establish global optimality.
