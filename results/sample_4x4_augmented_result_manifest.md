# sample_4x4 Augmented Result Manifest

Generated at: 2026-06-15T22:09:07

## Purpose

This manifest summarizes the first larger benchmark-derived pilot instance. The purpose is to verify that the human-centered time-indexed scheduling pipeline remains executable when the problem grows from sample_3x3 to sample_4x4. This is still a prototype/pilot validation step, not a final paper-level computational study.

## Instance Summary

- Base format: JSPLib-style job-shop scheduling
- Jobs: 4
- Machines: 4
- Operations: 16
- Human workers: 3
- Robot resources: 2
- Total resources: 9
- Planning horizon: 63
- Time slots: 63
- Binary variables: 9072
- Decision variable: x[o, r, t] = 1 if operation o starts on resource r at time t

## Generated Files

### Input and augmented instance

| File | Status |
|---|---|
| `data/benchmarks/jsplib/sample_4x4.txt` | FOUND |
| `data/augmented/sample_4x4_hc_seed2026_time_indexed.json` | FOUND |

### CP-SAT baseline

| File | Status |
|---|---|
| `results/tables/sample_4x4_augmented_cpsat_result.csv` | FOUND |

### Structure-aware seeded search

| File | Status |
|---|---|
| `results/tables/sample_4x4_augmented_seeded_search_results.csv` | FOUND |
| `results/tables/sample_4x4_augmented_seeded_search_summary.csv` | FOUND |

### Human-utilization variant

| File | Status |
|---|---|
| `results/tables/sample_4x4_human_utilization_cpsat_result.csv` | FOUND |
| `results/tables/sample_4x4_human_utilization_comparison.csv` | FOUND |

### Human-utilization sensitivity

| File | Status |
|---|---|
| `results/tables/sample_4x4_human_utilization_sensitivity.csv` | FOUND |

### Soft human-reward sensitivity

| File | Status |
|---|---|
| `results/tables/sample_4x4_soft_human_reward_sensitivity.csv` | FOUND |

### Soft human-reward QUBO validation

| File | Status |
|---|---|
| `results/tables/sample_4x4_soft_human_reward_qubo_validation.csv` | FOUND |

### Human-utilization figures

| File | Status |
|---|---|
| `results/figures/sample_4x4_human_utilization_total_cost.png` | FOUND |
| `results/figures/sample_4x4_human_utilization_assignment_counts.png` | FOUND |
| `results/figures/sample_4x4_human_utilization_human_centered_costs.png` | FOUND |

### Sensitivity figures

| File | Status |
|---|---|
| `results/figures/sample_4x4_human_sensitivity_total_cost.png` | FOUND |
| `results/figures/sample_4x4_human_sensitivity_human_centered_costs.png` | FOUND |
| `results/figures/sample_4x4_human_sensitivity_assignment_counts.png` | FOUND |
| `results/figures/sample_4x4_human_sensitivity_cost_components.png` | FOUND |

### Soft human-reward figures

| File | Status |
|---|---|
| `results/figures/sample_4x4_soft_reward_human_assignments.png` | FOUND |
| `results/figures/sample_4x4_soft_reward_objective_tradeoff.png` | FOUND |
| `results/figures/sample_4x4_soft_reward_human_centered_costs.png` | FOUND |
| `results/figures/sample_4x4_soft_reward_assignment_counts.png` | FOUND |

### Solver summary

| File | Status |
|---|---|
| `results/tables/sample_4x4_augmented_solver_summary.csv` | FOUND |

## Solver Summary

| Solver / search | Status | Feasible | Total cost / best cost | Gap to baseline CP-SAT | Notes |
|---|---|---:|---:|---:|---|
| CP-SAT | OPTIMAL | True | 57.0 | 0.0 | CP-SAT baseline for sample_4x4. |
| structure_aware_cpsat_seed | FEASIBLE_READS_FOUND | True | 57.0 | 0.0 | reads=10; feasible_reads=7; feasibility_rate=0.7; mean_gap_to_cpsat=11.72857142857143 |
| structure_aware_random_seed | FEASIBLE_READS_FOUND | True | 78.4 | 21.40000000000001 | reads=20; feasible_reads=13; feasibility_rate=0.65; mean_gap_to_cpsat=38.14615384615384 |
| Human-utilization CP-SAT | OPTIMAL | True | 62.1 | 5.100000000000001 | min_human_assignments=2; human_assignment_count=2; robot_assignment_count=1 |

## CP-SAT Baseline Result

- Status: OPTIMAL
- Feasible: True
- Violations: 0
- Total penalty: 0.0
- Total cost: 57.0
- Processing cost: 42.0
- Start-time cost: 15.0
- Workload cost: 0.0
- Ergonomic cost: 0.0
- Safety cost: 0.0
- Wall time: 0.377612

## Structure-Aware Search Summary

| Search method | Reads | Feasible reads | Feasibility rate | Best feasible cost | Best gap to CP-SAT | Mean gap to CP-SAT |
|---|---:|---:|---:|---:|---:|---:|
| structure_aware_cpsat_seed | 10 | 7 | 0.7 | 57.0 | 0.0 | 11.72857142857143 |
| structure_aware_random_seed | 20 | 13 | 0.65 | 78.4 | 21.40000000000001 | 38.14615384615384 |

## Human-Utilization Variant Result

- Variant: hard minimum human assignment constraint
- Minimum human assignments: 2
- Status: OPTIMAL
- Feasible: True
- Violations: 0
- Human assignment count: 2
- Robot assignment count: 1
- Total penalty: 0.0
- Total cost: 62.1
- Processing cost: 43.0
- Start-time cost: 13.4
- Workload cost: 1.5
- Ergonomic cost: 4.2
- Safety cost: 0.0

## Baseline vs Human-Utilization Comparison

| Variant | Human assignments | Robot assignments | Machine assignments | Workload | Ergonomic | Safety | Total cost | Cost increase vs baseline | Percent increase |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline CP-SAT | 0 | 1 | 15 | 0.0 | 0.0 | 0.0 | 57.0 | 0.0 | 0.0 |
| Human-utilization CP-SAT | 2 | 1 | 13 | 1.5 | 4.2 | 0.0 | 62.1 | 5.100000000000001 | 8.947368421052634 |

## Human-Utilization Sensitivity

| Min human assignments | Actual human | Machine | Robot | Processing | Start time | Workload | Ergonomic | Safety | Total cost | Increase vs min0 | Percent increase |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 15 | 1 | 42.0 | 15.0 | 0.0 | 0.0 | 0.0 | 57.0 | 0.0 | 0.0 |
| 1 | 1 | 14 | 1 | 43.0 | 14.6 | 0.5 | 0.7 | 0.0 | 58.8 | 1.8000000000000045 | 3.157894736842113 |
| 2 | 2 | 13 | 1 | 43.0 | 13.4 | 1.5 | 4.2 | 0.0 | 62.1 | 5.100000000000001 | 8.947368421052634 |
| 3 | 3 | 12 | 1 | 44.0 | 13.4 | 4.0 | 4.9 | 0.0 | 66.3 | 9.299999999999995 | 16.315789473684205 |
| 4 | 4 | 11 | 1 | 45.0 | 13.4 | 8.0 | 5.6000000000000005 | 0.0 | 72.0 | 15.0 | 26.31578947368421 |

## Soft Human-Reward Sensitivity

| Human reward | Human assignments | Machine | Robot | Processing | Start time | Workload | Ergonomic | Safety | Cost without reward | Reward value | Reward-adjusted objective |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 15 | 1 | 42.0 | 15.0 | 0.0 | 0.0 | 0.0 | 57.0 | 0 | 57.0 |
| 1 | 0 | 15 | 1 | 42.0 | 15.0 | 0.0 | 0.0 | 0.0 | 57.0 | 0 | 57.0 |
| 2 | 1 | 14 | 1 | 43.0 | 14.6 | 0.5 | 0.7 | 0.0 | 58.8 | 2 | 56.8 |
| 3 | 1 | 14 | 1 | 43.0 | 14.6 | 0.5 | 0.7 | 0.0 | 58.8 | 3 | 55.8 |
| 4 | 2 | 13 | 1 | 43.0 | 13.4 | 1.5 | 4.2 | 0.0 | 62.1 | 8 | 54.1 |
| 5 | 3 | 12 | 1 | 44.0 | 13.4 | 4.0 | 4.9 | 0.0 | 66.3 | 15 | 51.3 |

## Soft Human-Reward QUBO Validation

| Human reward | Human assignments | Expected reward-adjusted objective | QUBO energy | Absolute error | Pass |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 0 | 57.0 | 57.0 | 0.0 | True |
| 1.0 | 0 | 57.0 | 57.0 | 0.0 | True |
| 2.0 | 1 | 56.8 | 56.80000000000007 | 7.105427357601003e-14 | True |
| 3.0 | 1 | 55.8 | 55.799999999999955 | 4.263256414560601e-14 | True |
| 4.0 | 2 | 54.1 | 54.10000000000002 | 2.131628207280301e-14 | True |
| 5.0 | 3 | 51.3 | 51.299999999999955 | 4.263256414560601e-14 | True |

Maximum absolute validation error: 7.105427357601003e-14

## Key Pilot Findings

- CP-SAT solved the 9072-variable time-indexed sample_4x4 instance to optimality.
- The baseline CP-SAT total cost was 57.0 with zero penalty.
- Structure-aware random-seed search found feasible solutions, but the best gap to CP-SAT remained large.
- Structure-aware CP-SAT-seeded search preserved the CP-SAT optimal solution in the best read, but this is a warm-start ablation.
- As the problem size increased from 1836 to 9072 binary variables, seed quality and local search design became more important.
- The baseline objective tends to avoid human workers, producing zero workload and ergonomic cost under CP-SAT.
- Adding a hard minimum human assignment constraint activated workload and ergonomic cost terms.
- The human-utilization variant increased total cost from 57.0 to 62.1, a 5.1-unit increase, approximately 8.95%.
- The sensitivity experiment showed a monotonic cost increase as minimum human assignments increased from 0 to 4.
- Human involvement increased workload and ergonomic costs, while start-time cost decreased modestly, suggesting a scheduling-flexibility trade-off.
- The soft human-reward variant showed threshold behavior: rewards of 0–1 selected no human assignments, reward 2 selected one human assignment, reward 4 selected two, and reward 5 selected three.
- Under the soft reward objective, total cost without reward increased as human involvement increased, but reward-adjusted objective decreased.
- The soft human-reward QUBO validation passed, confirming that QUBO energy matches the reward-adjusted objective across tested reward values.

## Current Status

Completed sample_4x4 pilot pipeline:

- Larger JSPLib-style instance generation
- Synthetic human-centered augmentation
- Time-indexed instance generation
- CP-SAT baseline
- Structure-aware seeded search
- Human-utilization constrained CP-SAT variant
- Baseline vs human-utilization comparison
- Human-utilization sensitivity analysis
- Human-utilization and sensitivity figures
- Soft human-reward sensitivity analysis
- Soft human-reward figures
- Soft human-reward QUBO validation
- Solver summary

## Recommended Next Step

The next recommended step is to formalize the human-involvement reward as a multi-objective trade-off model. The current soft-reward pilot shows that reward strength controls when human assignments become attractive, but future experiments should test this behavior across multiple instances and augmentation seeds.
