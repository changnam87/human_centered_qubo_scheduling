# sample_4x4 Fine-Grid Soft Human-Reward Batch Pilot Manifest

## Purpose

This pilot refines the previous integer-grid soft human-reward sensitivity experiment for sample_4x4.

The previous integer-grid batch used human_reward = 0, 1, 2, 3, 4, 5 and showed that human involvement begins around reward 2 to 3.

This fine-grid pilot uses human_reward = 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, and 4.0 to estimate the human-involvement activation threshold more precisely.

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

## Reward Grid

human_reward = 0.0
human_reward = 0.5
human_reward = 1.0
human_reward = 1.5
human_reward = 2.0
human_reward = 2.5
human_reward = 3.0
human_reward = 3.5
human_reward = 4.0

## Objective

reward_adjusted_objective = total_cost_without_reward - human_reward * human_assignment_count

total_cost_without_reward = start_time_cost + assignment_cost + workload_cost + ergonomic_cost

## Main Pilot Questions

1. At what reward value does human_assignments >= 1 first occur?
2. At what reward value does human_assignments >= 2 first occur?
3. At what reward value does human_assignments >= 3 first occur?
4. At what reward value does human assignment become dominant?

Dominant human-assignment behavior is approximated by threshold_human_ge_8 and threshold_human_ge_16.

## Scripts

scripts/run_sample_4x4_soft_human_reward_fine_grid_batch.py
scripts/analyze_sample_4x4_soft_human_reward_fine_grid_batch.py

## Result Tables

results/tables/sample_4x4_soft_human_reward_fine_grid_batch_sensitivity.csv
results/tables/sample_4x4_soft_human_reward_fine_grid_batch_metadata.json
results/tables/sample_4x4_soft_human_reward_fine_grid_batch_thresholds.csv
results/tables/sample_4x4_soft_human_reward_fine_grid_batch_summary_by_reward.csv

## Figures

results/figures/sample_4x4_soft_reward_fine_grid_human_assignments.png
results/figures/sample_4x4_soft_reward_fine_grid_cost_without_reward.png
results/figures/sample_4x4_soft_reward_fine_grid_reward_adjusted_objective.png
results/figures/sample_4x4_soft_reward_fine_grid_threshold_distribution.png

## Observed Fine-Grid Threshold Pattern

The fine-grid batch pilot showed a clear threshold-like response to the soft human-reward parameter.

Across seeds 2001-2010, human assignments were absent for reward values from 0.0 through 1.5.

Initial human involvement began around reward 2.0, with most seeds first reaching at least one human assignment at reward 2.0 and the remaining seeds doing so at reward 2.5.

The threshold for at least three human assignments was consistently observed at reward 2.5 across all seeds.

Human assignment became increasingly dominant for rewards 3.0 and above. The threshold for at least eight human assignments occurred mostly at reward 3.0, with a small number of seeds reaching this level at reward 3.5. At reward 4.0, some seeds reached all 16 operations assigned to human resources.

The cost-before-reward curve increased as human assignments increased, confirming that human involvement activates additional workload and ergonomic costs.

At the same time, the reward-adjusted objective decreased as the reward became large enough to compensate for these added costs.

Overall, these results support the pilot-level validity of the soft human-reward term as a controllable mechanism for inducing human involvement.

However, they also show that a linear reward can become too strong at high reward values, motivating future variants such as over-utilization penalties, target-based human-utilization rewards, concave rewards, or workload-balancing constraints.

These findings remain prototype-level validation results and should not yet be framed as final empirical or paper-level claims.

## Pilot-Level Interpretation

Region 1: reward = 0.0-1.5. Human assignments are absent. The solver avoids human resources because human assignment activates workload and ergonomic costs.

Region 2: reward = 2.0-3.0. Human assignments begin and increase sharply. This is the human-involvement activation zone.

Region 3: reward = 3.5-4.0. Human assignments become dominant. The linear reward term strongly favors human resources.

## Concise Pilot-Level Conclusion

Across 10 synthetic sample_4x4 augmentation seeds, the fine-grid soft human-reward sensitivity showed a consistent threshold-like response.

Human assignments were absent for rewards up to 1.5, began to appear around reward 2.0, became consistently multi-operation around reward 2.5, and became dominant around reward 3.0-3.5.

This supports the pilot-level validity of the soft human-reward term as a controllable mechanism for inducing human involvement in the scheduling solution.

## Next Prototype Direction

The fine-grid pilot suggests that the linear human-reward term may become too strong at high reward values.

A natural next prototype is soft human reward plus over-utilization penalty.

objective = total_cost_without_reward - human_reward * human_assignment_count + overuse_penalty * max(0, human_assignment_count - target_human_assignments)

This would test whether human involvement can be encouraged without pushing the model toward excessive human assignment.
