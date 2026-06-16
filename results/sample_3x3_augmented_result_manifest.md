# sample_3x3 Augmented Result Manifest

Generated at: 2026-06-15T20:20:37

## Purpose

This manifest summarizes the first benchmark-derived human-centered time-indexed scheduling experiment. The base instance is a small JSPLib-style 3-job, 3-machine sample instance. Synthetic human-centered attributes were added to support computational benchmarking of a human-centered QUBO/Ising scheduling formulation.

## Instance Summary

- Base format: JSPLib-style job-shop scheduling
- Jobs: 3
- Machines: 3
- Operations: 9
- Human workers: 2
- Robot resources: 1
- Total resources: 6
- Planning horizon: 34
- Time slots: 34
- Binary variables: 1836
- Decision variable: x[o, r, t] = 1 if operation o starts on resource r at time t

## Generated Files

### Input and augmented instance

| File | Status |
|---|---|
| `data/benchmarks/jsplib/sample_3x3.txt` | FOUND |
| `data/augmented/sample_3x3_hc_seed2026.json` | FOUND |
| `data/augmented/sample_3x3_hc_seed2026_time_indexed.json` | FOUND |

### QUBO validation

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_qubo_validation.csv` | FOUND |

### CP-SAT baseline

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_cpsat_result.csv` | FOUND |

### Random-bit simulated annealing

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_sa_results.csv` | FOUND |

### Structure-aware seeded search

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_seeded_search_results.csv` | FOUND |
| `results/tables/sample_3x3_augmented_seeded_search_summary.csv` | FOUND |

### Solver comparison summaries

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_solver_summary.csv` | FOUND |
| `results/tables/sample_3x3_augmented_search_method_comparison.csv` | FOUND |

### Statistical analysis

| File | Status |
|---|---|
| `results/tables/sample_3x3_search_statistical_analysis.csv` | FOUND |
| `results/tables/sample_3x3_search_cost_summary_with_ci.csv` | FOUND |
| `results/tables/sample_3x3_search_continuous_effect_sizes.csv` | FOUND |

### Figures

| File | Status |
|---|---|
| `results/figures/sample_3x3_search_feasibility_rate.png` | FOUND |
| `results/figures/sample_3x3_search_best_feasible_cost.png` | FOUND |
| `results/figures/sample_3x3_search_best_gap_to_cpsat.png` | FOUND |
| `results/figures/sample_3x3_search_feasibility_rate_ci.png` | FOUND |
| `results/figures/sample_3x3_search_mean_feasible_cost_ci.png` | FOUND |
| `results/figures/sample_3x3_search_mean_gap_to_cpsat_ci.png` | FOUND |

## Solver Summary

| Solver / solution | Feasible | Violations | Total cost | Gap to CP-SAT | Improvement over handcrafted |
|---|---:|---:|---:|---:|---:|
| Handcrafted feasible schedule | True | 0 | 34.2 | 2.400000000000002 | 0.0 |
| CP-SAT | True | 0 | 31.8 | 0.0 | 2.400000000000002 |
| Seeded structure-aware search from handcrafted | True | 0 | 33.4 | 1.599999999999998 | 0.8000000000000043 |
| Seeded structure-aware search from CP-SAT | True | 0 | 31.8 | 0.0 | 2.400000000000002 |

## Search Method Comparison

| Method | Reads | Feasible reads | Feasibility rate | Best feasible cost | Best gap to CP-SAT |
|---|---:|---:|---:|---:|---:|
| Random-bit simulated annealing | 200 | 0 | 0.0 | nan | nan |
| Structure-aware seeded search from CP-SAT | 10 | 8 | 0.8 | 31.8 | 0.0 |
| Structure-aware seeded search from handcrafted | 30 | 30 | 1.0 | 33.4 | 1.599999999999998 |

## Feasibility Rate with 95% Wilson CI

| Method | n | Feasible | Rate | CI lower | CI upper |
|---|---:|---:|---:|---:|---:|
| Random-bit SA | 200.0 | 0.0 | 0.0 | 0.0 | 0.0188460059183208 |
| Seeded search from CP-SAT | 10.0 | 8.0 | 0.8 | 0.4901568467207233 | 0.9433190520193068 |
| Seeded search from handcrafted | 30.0 | 30.0 | 1.0 | 0.8864829086095221 | 1.0 |

## Feasibility Effect Sizes

| Comparison | Risk difference | Cohen's h | Odds ratio | Comparison type |
|---|---:|---:|---:|---|
| Seeded search from handcrafted vs Random-bit SA | 1.0 | 3.141592653589793 | 24461.0 | main |
| Seeded search from CP-SAT vs Random-bit SA | 0.8 | 2.214297435588181 | 1363.4 | warm-start_ablation |

## Feasible Cost and Gap with Bootstrap 95% CI

| Method | n feasible | Best cost | Mean cost | Cost CI lower | Cost CI upper | Mean gap | Gap CI lower | Gap CI upper |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Random-bit SA | 0 | nan | nan | nan | nan | nan | nan | nan |
| Seeded search from CP-SAT | 8 | 31.8 | 35.8 | 33.874375 | 38.27499999999999 | 3.9999999999999982 | 2.074374999999999 | 6.474999999999997 |
| Seeded search from handcrafted | 30 | 33.4 | 36.10666666666667 | 35.28 | 37.0 | 4.306666666666667 | 3.480000000000001 | 5.199999999999999 |

## Key Findings

- CP-SAT found an optimal feasible solution with total cost 31.8.
- The handcrafted feasible schedule had total cost 34.2.
- CP-SAT improved the handcrafted schedule by 2.4 cost units, approximately 7.02%.
- Random-bit simulated annealing found no feasible solutions across 200 reads.
- Structure-aware seeded search from the handcrafted schedule achieved 100% feasibility and improved the handcrafted solution to best cost 33.4.
- Structure-aware seeded search from the CP-SAT solution achieved best cost 31.8, but should be interpreted as a warm-start ablation rather than a fair main comparison.
- The main methodological finding is that operation-level structure-aware moves are far more suitable than arbitrary bit flips for large time-indexed QUBO scheduling models.

## Current Status

Completed benchmark-derived sample_3x3 pipeline:

- JSPLib-style parser
- Synthetic human-centered augmentation
- Time-indexed adapter
- Generalized time-indexed evaluator
- Generalized QUBO validation
- CP-SAT classical baseline
- Random-bit simulated annealing baseline
- Structure-aware seeded local search
- Solver comparison table
- Statistical analysis with confidence intervals and effect sizes
- CI/error-bar figures

## Recommended Next Step

The next recommended step is to repeat this benchmark-derived pipeline on additional small instances with different sizes, resource mixes, and human-centered augmentation seeds. This will allow analysis of robustness across instance structure, constraint density, and human-centered attribute distributions.
