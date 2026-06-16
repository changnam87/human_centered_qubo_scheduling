# sample_4x4 Target-Deviation Penalty Batch Pilot Manifest

## Purpose

This pilot extends the overuse-penalty experiment by testing a target-deviation penalty for human utilization.

The overuse-penalty formulation penalized only human assignments above the target. In contrast, the target-deviation formulation penalizes both under-use and over-use of human resources.

## Experiment Type

Prototype / pilot validation. These results should not yet be framed as final paper-level empirical claims.

## Instance Family

sample_4x4 human-centered augmented time-indexed scheduling instances.

## Seeds

2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010

## Model Scale

jobs = 4
machines = 4
operations = 16
workers = 3
robots = 2
resources = 9
planning horizon = 63
binary variables = 16 * 9 * 63 = 9072

## Objective

objective = total_cost_without_reward - human_reward * human_assignment_count + target_deviation_penalty * abs(human_assignment_count - target_human_assignments)

## Parameter Grid

target_human_assignments = 4

human_reward values:
- 0.0
- 1.0
- 2.0
- 2.5
- 3.0

target_deviation_penalty values:
- 0.0
- 0.5
- 1.0
- 2.0
- 3.0
- 4.0

## Scripts

scripts/run_sample_4x4_target_deviation_penalty_batch.py
scripts/analyze_sample_4x4_target_deviation_penalty_batch.py

## Result Tables

results/tables/sample_4x4_target_deviation_penalty_batch.csv
results/tables/sample_4x4_target_deviation_penalty_batch_metadata.json
results/tables/sample_4x4_target_deviation_penalty_summary.csv
results/tables/sample_4x4_target_deviation_penalty_best_by_reward.csv

## Figures

results/figures/sample_4x4_target_deviation_human_assignments.png
results/figures/sample_4x4_target_deviation_distance_from_target.png
results/figures/sample_4x4_target_deviation_cost_without_reward.png
results/figures/sample_4x4_target_deviation_adjusted_objective.png

## Main Pilot Question

Can a target-deviation penalty act as a symmetric control mechanism that pulls human assignments toward a desired target, penalizing both under-use and over-use?

## Interpretation Template

If mean human assignments move toward target_human_assignments as target_deviation_penalty increases, the penalty is functioning as intended.

If distance_from_target decreases to zero for some penalty values, the formulation can exactly enforce target-oriented human utilization through the objective rather than a hard constraint.

If low human_reward values still reach the target when target_deviation_penalty is large, the target-deviation term is strong enough to induce human involvement even without a large positive reward.

These findings remain prototype-level validation results and should motivate future QUBO-compatible target-based formulations.

## Observed Target-Deviation Penalty Pattern

The target-deviation penalty pilot showed that the penalty term successfully acted as a symmetric control mechanism for human utilization.

Unlike the overuse-only penalty, which penalizes only human assignments above the target, the target-deviation penalty penalizes both under-use and over-use relative to the target human assignment count.

Across all tested human_reward values, an appropriate target_deviation_penalty achieved exactly the target level of four human assignments, with mean human assignments of 4.0 and mean distance from target of 0.0.

The best target_deviation_penalty values were reward-dependent. For human_reward = 0.0, the best penalty was 3.0. For human_reward = 1.0, the best penalty was 2.0. For human_reward = 2.0, the best penalty was 1.0. For human_reward = 2.5, the best penalty was 0.5. For human_reward = 3.0, the best penalty was 1.0.

These results show that lower human_reward values require stronger target-deviation penalties to induce human involvement, while higher human_reward values require the penalty to suppress excessive human assignment.

When the target was achieved, the solutions converged to a consistent average cost structure, with mean total cost without reward of approximately 54.305, mean workload cost of 4.5, and mean ergonomic cost of 2.82.

The adjusted objective sometimes increased as the target-deviation penalty increased. This is expected because the goal of this formulation is not simply to lower the reward-adjusted objective, but to control human utilization around a desired target.

Overall, this pilot supports the target-deviation penalty as a prototype-level formulation for target-oriented human utilization in human-centered scheduling.
