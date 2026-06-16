# sample_3x3 Batch Result Manifest

Generated at: 2026-06-15T20:56:35

## Purpose

This manifest summarizes a batch pilot experiment using 10 synthetic human-centered augmentations of the sample_3x3 JSPLib-style instance. The purpose is not to claim final paper-level results, but to verify that the benchmark augmentation, CP-SAT baseline, structure-aware search, statistical analysis, multiple-comparison correction, and visualization pipeline can be executed repeatedly across augmentation seeds.

## Batch Design

- Base instance: sample_3x3 JSPLib-style job-shop instance
- Augmentation seeds: 1001–1010
- Number of augmented instances: 10
- Machines: 3
- Human workers: 2
- Robot resources: 1
- Total resources: 6
- Main baseline: CP-SAT
- Heuristic search methods:
  - structure-aware random-seed local search
  - structure-aware CP-SAT-seeded warm-start search

## Generated Files

### Batch generated instances

| File | Status |
|---|---|
| `data/augmented/batch/sample_3x3_hc_seed1001_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1002_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1003_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1004_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1005_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1006_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1007_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1008_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1009_time_indexed.json` | FOUND |
| `data/augmented/batch/sample_3x3_hc_seed1010_time_indexed.json` | FOUND |

### Batch instance summary

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_batch_instance_summary.csv` | FOUND |

### Batch CP-SAT baseline

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_batch_cpsat_results.csv` | FOUND |
| `results/tables/sample_3x3_batch_cpsat_distribution_summary.csv` | FOUND |

### Batch seeded search

| File | Status |
|---|---|
| `results/tables/sample_3x3_augmented_batch_seeded_search_results.csv` | FOUND |
| `results/tables/sample_3x3_augmented_batch_seeded_search_summary.csv` | FOUND |

### Batch statistical analysis

| File | Status |
|---|---|
| `results/tables/sample_3x3_batch_search_statistical_summary.csv` | FOUND |
| `results/tables/sample_3x3_batch_search_effect_sizes.csv` | FOUND |
| `results/tables/sample_3x3_batch_search_hypothesis_tests.csv` | FOUND |

### Batch figures

| File | Status |
|---|---|
| `results/figures/sample_3x3_batch_feasibility_rate_ci.png` | FOUND |
| `results/figures/sample_3x3_batch_mean_gap_to_cpsat_ci.png` | FOUND |
| `results/figures/sample_3x3_batch_best_gap_to_cpsat_ci.png` | FOUND |

## Batch Instance Summary

| Seed | Horizon | Binary variables | Compatible assignments | Worker-compatible | Robot-compatible | Avg workload | Avg ergonomic | Avg safety |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1001 | 34 | 1836 | 27 | 12 | 6 | 5.666666666666667 | 5.777777777777778 | 1.1111111111111112 |
| 1002 | 34 | 1836 | 27 | 14 | 4 | 5.111111111111111 | 6.555555555555555 | 1.1111111111111112 |
| 1003 | 34 | 1836 | 27 | 13 | 5 | 4.444444444444445 | 7.111111111111111 | 1.5555555555555556 |
| 1004 | 34 | 1836 | 25 | 12 | 4 | 5.0 | 5.444444444444445 | 2.0 |
| 1005 | 34 | 1836 | 30 | 15 | 6 | 6.222222222222222 | 7.777777777777778 | 1.4444444444444444 |
| 1006 | 33 | 1782 | 27 | 12 | 6 | 4.333333333333333 | 4.444444444444445 | 1.5555555555555556 |
| 1007 | 33 | 1782 | 29 | 14 | 6 | 5.777777777777778 | 4.777777777777778 | 1.6666666666666667 |
| 1008 | 34 | 1836 | 28 | 14 | 5 | 5.111111111111111 | 5.111111111111111 | 1.4444444444444444 |
| 1009 | 34 | 1836 | 26 | 12 | 5 | 4.444444444444445 | 3.888888888888889 | 1.6666666666666667 |
| 1010 | 34 | 1836 | 27 | 13 | 5 | 5.555555555555555 | 6.666666666666667 | 1.4444444444444444 |

## CP-SAT Distribution Summary

- Number of instances: 10
- Number optimal: 10
- Number feasible: 10
- Mean total cost: 29.559999999999995
- 95% bootstrap CI for mean total cost: [29.24, 29.94]
- Min total cost: 29.0
- Max total cost: 30.8
- Mean wall time: 0.0469397

## CP-SAT Seed-Level Results

| Seed | Status | Feasible | Total cost | Processing | Start time | Workload | Ergonomic | Safety | Penalty | Wall time |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1001 | OPTIMAL | True | 29.2 | 23.0 | 6.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.048554 |
| 1002 | OPTIMAL | True | 29.2 | 23.0 | 6.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.044116 |
| 1003 | OPTIMAL | True | 29.8 | 23.0 | 6.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.052034 |
| 1004 | OPTIMAL | True | 29.0 | 23.0 | 6.000000000000001 | 0.0 | 0.0 | 0.0 | 0.0 | 0.038667 |
| 1005 | OPTIMAL | True | 29.2 | 23.0 | 6.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.056311 |
| 1006 | OPTIMAL | True | 29.8 | 23.0 | 6.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.046542 |
| 1007 | OPTIMAL | True | 29.4 | 22.0 | 6.400000000000001 | 0.0 | 0.0 | 1.0 | 0.0 | 0.050161 |
| 1008 | OPTIMAL | True | 30.8 | 23.0 | 6.8 | 0.0 | 0.0 | 1.0 | 0.0 | 0.047275 |
| 1009 | OPTIMAL | True | 30.2 | 23.0 | 6.2 | 0.0 | 0.0 | 1.0 | 0.0 | 0.04269 |
| 1010 | OPTIMAL | True | 29.0 | 23.0 | 6.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.043047 |

## Batch Search Statistical Summary

| Search method | Reads | Feasible reads | Feasibility rate | 95% CI lower | 95% CI upper | Mean gap | Mean best gap |
|---|---:|---:|---:|---:|---:|---:|---:|
| structure_aware_cpsat_seed | 100 | 97 | 0.97 | 0.915479219195973 | 0.9897456617765852 | 4.60618556701031 | 3.552713678800501e-16 |
| structure_aware_random_seed | 200 | 198 | 0.99 | 0.9642775148038204 | 0.9972533993962251 | 6.063636363636364 | 2.400000000000001 |

## Effect Sizes

| Comparison | Metric | Group 1 value | Group 2 value | Difference | Effect size details |
|---|---|---:|---:|---:|---|
| structure_aware_random_seed vs structure_aware_cpsat_seed | feasibility_rate | 0.99 | 0.97 | 0.02 | Cohen's h=0.1478311789498412; OR=2.85025641025641 |
| structure_aware_random_seed vs structure_aware_cpsat_seed | gap_to_cpsat_feasible_reads | 6.063636363636364 | 4.60618556701031 | 1.4574507966260546 | Cohen's d=0.5164807082440125; Cliff's delta=0.2877746537540352 |
| structure_aware_random_seed vs structure_aware_cpsat_seed | best_gap_to_cpsat_instance_level | 2.400000000000001 | 3.552713678800501e-16 | 2.4000000000000004 | Cohen's d=7.348469228349531; Cliff's delta=1.0 |

## Hypothesis Tests with Multiple-Comparison Correction

P-values were adjusted using the Holm-Bonferroni procedure across the batch search-method test family.

| Metric | Test | Statistic | Raw p | Holm-adjusted p | Significant after Holm 0.05 |
|---|---|---:|---:|---:|---:|
| feasibility_rate | two_proportion_z_test | 1.2755856082865606 | 0.2021020441893728 | 0.2021020441893728 | False |
| gap_to_cpsat_feasible_reads | welch_t_test | 3.714211290684782 | 0.0002904489392009 | 0.0005808978784018 | True |
| gap_to_cpsat_feasible_reads | mann_whitney_u_test | 12366.5 | 5.951109023518084e-05 | 0.0002380443609407 | True |
| best_gap_to_cpsat_instance_level | welch_t_test | 16.431676725154976 | 5.098754915046487e-08 | 2.5493774575232434e-07 | True |
| best_gap_to_cpsat_instance_level | mann_whitney_u_test | 100.0 | 8.454414426286908e-05 | 0.0002536324327886 | True |

## Key Pilot Findings

- CP-SAT solved all 10 augmented instances to optimality and feasibility.
- Both structure-aware search methods achieved high feasibility rates.
- Feasibility differences between structure-aware random-seed and CP-SAT-seed search were not statistically significant after Holm-Bonferroni correction.
- Gap-to-CP-SAT differences were statistically significant after correction, indicating that seed quality affects solution quality even when feasibility is high.
- The CP-SAT-seeded search should be interpreted as a warm-start ablation, not as a fair main comparison against random-seed search.
- The batch pilot supports the methodological idea that operation-level structure-aware moves are more appropriate than arbitrary bit flips for large time-indexed QUBO scheduling search.

## Current Status

Completed batch pilot pipeline:

- Batch synthetic human-centered augmentation
- Batch time-indexed instance generation
- Batch CP-SAT baseline
- Batch structure-aware seeded search
- Batch statistical summary
- Effect size analysis
- Holm-Bonferroni multiple-comparison correction
- Batch CI/error-bar figures

## Recommended Next Step

The next recommended step is to introduce at least one larger or structurally different benchmark-derived instance. This will test whether the same pipeline remains robust as the number of operations, resources, planning horizon, and constraint density increase.
