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

## Observed Overuse-Penalty Pattern

The overuse-penalty batch pilot showed that the penalty term successfully controlled excessive human assignment induced by the linear soft human-reward term.

For human_reward = 2.5, the unpenalized model was already close to the target level of four human assignments. A small overuse penalty of 0.5 produced the best average target proximity, with mean human assignments of 3.6 and mean distance from target of 0.4.

For human_reward = 3.0, the unpenalized model over-assigned operations to human resources, with mean human assignments around 8.4. Increasing the overuse penalty sharply reduced human assignments, and overuse_penalty = 1.0 achieved the target exactly, with mean human assignments of 4.0, mean distance from target of 0.0, and mean overuse count of 0.0.

For human_reward = 3.5, the unpenalized model produced strong over-assignment, with mean human assignments around 12.3. A larger overuse penalty was required. At overuse_penalty = 2.0 and above, the model stabilized at the target level, with mean human assignments of 4.0, mean distance from target of 0.0, and mean overuse count of 0.0.

These results suggest that human_reward and overuse_penalty operate as a coupled tuning pair. Stronger human rewards require stronger overuse penalties to maintain target-oriented human utilization.

The adjusted objective increased when overuse penalties were introduced for stronger reward settings, but this is expected because the goal of the penalty term is not to minimize the reward-adjusted objective alone. Instead, the goal is to prevent excessive human assignment while preserving controlled human involvement.

Overall, this pilot supports the use of an over-utilization penalty as a prototype-level control mechanism for balancing human involvement against workload and ergonomic cost.
