# QUBO-Compatible Squared Target Human-Utilization Penalty

## Purpose

This document defines a QUBO-compatible target-based human-utilization penalty for the human-centered scheduling prototype.

The previous target-deviation pilot used an absolute deviation term:

objective = total_cost_without_reward - human_reward * human_count + lambda_abs * abs(human_count - target)

Absolute values can be modeled in CP-SAT, but they are less direct in a standard QUBO formulation.

For QUBO/Ising compatibility, a squared target penalty is more natural:

objective = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target)^2

## Human Count Definition

Let h_i be a binary indicator that operation i is assigned to a human resource.

h_i = 1 if operation i is assigned to a human worker
h_i = 0 otherwise

Then:

human_count = sum_i h_i

## Squared Target Penalty

The target penalty is:

lambda_target * (sum_i h_i - target)^2

Expanding:

lambda_target * [(sum_i h_i)^2 - 2 * target * sum_i h_i + target^2]

Because h_i is binary, h_i^2 = h_i.

Therefore:

(sum_i h_i)^2 = sum_i h_i + 2 * sum_{i<j} h_i h_j

So the QUBO expansion is:

lambda_target * [sum_i h_i + 2 * sum_{i<j} h_i h_j - 2 * target * sum_i h_i + target^2]

Collecting terms:

lambda_target * [(1 - 2 * target) * sum_i h_i + 2 * sum_{i<j} h_i h_j + target^2]

The constant lambda_target * target^2 does not affect the optimizer, but it is useful when validating exact energy values.

## Interpretation

If human_count is below target, the squared penalty encourages additional human assignments.

If human_count is above target, the squared penalty discourages excessive human assignments.

If human_count equals target, the penalty is zero.

## Prototype Objective

The sample_4x4 squared-target pilot uses:

objective = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target)^2

where:

total_cost_without_reward = start_time_cost + assignment_cost + workload_cost + ergonomic_cost

## Pilot Status

This formulation is still part of prototype / pilot validation. It is not yet a final paper-level empirical claim.
