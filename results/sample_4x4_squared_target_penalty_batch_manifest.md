
## Observed Squared Target Penalty Pattern

The QUBO-compatible squared target penalty pilot showed that the squared penalty successfully controlled human utilization around the target level.

Across all tested human_reward values, an appropriate lambda_target achieved exactly four mean human assignments, with mean distance from target of 0.0 and mean squared deviation of 0.0.

The best lambda_target values were reward-dependent. For human_reward = 0.0, the best lambda_target was 3.0. For human_reward = 1.0, the best lambda_target was 2.0. For human_reward = 2.0, the best lambda_target was 1.0. For human_reward = 2.5, the best lambda_target was 0.25. For human_reward = 3.0, the best lambda_target was 1.0.

These results show that lower human_reward values require larger lambda_target values to induce human involvement, while higher reward values require lambda_target to suppress excessive human assignment.

When the target was achieved, the solutions converged to a consistent average cost structure, with mean total cost without reward of approximately 54.305.

The squared target penalty also reduced both mean distance from target and mean squared deviation as lambda_target increased. This supports the squared penalty as an effective target-oriented control mechanism.

Unlike the absolute target-deviation penalty, the squared target penalty expands directly into linear and quadratic binary terms. Therefore, it is more suitable for QUBO and Ising implementation.

Overall, this pilot supports the QUBO-compatible squared target penalty as the preferred target-based human-utilization formulation for the next stage of prototype validation.

## Full Squared-Target Energy Validation

An additional formulation-level energy validation was performed for the sample_4x4 squared target penalty batch result table.

For each solved row, the QUBO-compatible squared target energy was recomputed as:

energy = total_cost_without_reward - human_reward * human_assignments + lambda_target * (human_assignments - target_human_assignments)^2

The recomputed energy was compared against the stored adjusted_objective_manual value from the batch result table.

This validation checks whether the sample_4x4 pilot results are internally consistent with the squared target formulation.

The validation output files are:

- results/tables/sample_4x4_squared_target_energy_validation.csv
- results/tables/sample_4x4_squared_target_energy_validation_summary.csv

The validation passed when the maximum absolute error between recomputed energy and adjusted_objective_manual was within numerical tolerance.

This provides a sample_4x4-level formulation checkpoint beyond the toy QUBO expansion validation.
