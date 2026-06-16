
## Observed Parameter Sensitivity Pattern

The small time-indexed QUBO parameter sensitivity showed a clear feasibility threshold for the constraint penalty.

When constraint_penalty = 1.0, the QUBO optimum was infeasible for all tested reward/lambda settings. The feasible rate was 0.0, and the mean assignment violation count was 1.56.

When constraint_penalty was increased to 5.0 or higher, the QUBO optimum was feasible for all tested settings. The feasible rate became 1.0, and assignment, overlap, and precedence violations all dropped to 0.0.

This suggests that, for this small time-indexed prototype, constraint_penalty = 5.0 is sufficient to stabilize feasibility.

The target-consistent rate was 0.48 for constraint_penalty values of 5.0, 10.0, and 30.0. This indicates that feasibility and target consistency are controlled by different parameter groups.

Constraint penalties primarily enforce scheduling feasibility, while human_reward and lambda_target determine whether the feasible optimum reaches the desired human-utilization target.

These results support the need for penalty-weight calibration before scaling QUBO export to larger time-indexed scheduling instances.
