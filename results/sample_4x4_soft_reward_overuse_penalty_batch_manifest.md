# sample_4x4 Soft Reward Plus Overuse Penalty Batch Pilot Manifest

## Purpose

This pilot extends the fine-grid soft human-reward experiment by adding an over-utilization penalty for human assignments.

The previous fine-grid pilot showed that a linear soft human reward can induce human involvement, but can also become too strong at high reward values.

This experiment tests whether an overuse penalty can encourage human involvement while reducing excessive assignment of operations to human resources.

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

objective = total_cost_without_reward - human_reward * human_assignment_count + overuse_penalty * max(0, human_assignment_count - target_human_assignments)

## Parameter Grid

target_human_assignments = 4

human_reward values:
- 2.5
- 3.0
- 3.5

overuse_penalty values:
- 0.0
- 0.5
- 1.0
- 2.0
- 3.0
- 4.0

## Scripts

scripts/run_sample_4x4_soft_reward_overuse_penalty_batch.py
scripts/analyze_sample_4x4_soft_reward_overuse_penalty_batch.py

## Result Tables

results/tables/sample_4x4_soft_reward_overuse_penalty_batch.csv
results/tables/sample_4x4_soft_reward_overuse_penalty_batch_metadata.json
results/tables/sample_4x4_soft_reward_overuse_penalty_summary.csv
results/tables/sample_4x4_soft_reward_overuse_penalty_best_by_reward.csv

## Figures

results/figures/sample_4x4_overuse_penalty_human_assignments.png
results/figures/sample_4x4_overuse_penalty_distance_from_target.png
results/figures/sample_4x4_overuse_penalty_cost_without_reward.png
results/figures/sample_4x4_overuse_penalty_adjusted_objective.png

## Main Pilot Question

Can an overuse penalty act as a control mechanism that reduces excessive human assignment while preserving the ability of soft human reward to induce human involvement?

## Interpretation Template

If human assignments decrease as overuse_penalty increases, then the penalty is functioning as an intended control knob.

If the mean distance from target_human_assignments decreases for some nonzero overuse_penalty value, then the overuse penalty improves target-oriented human utilization relative to the linear reward-only objective.

If overuse_penalty becomes too large and human assignments fall below the desired target, this suggests that the penalty must be calibrated jointly with the human_reward parameter.

These findings remain prototype-level validation results and should motivate additional target-based or workload-balancing variants.
