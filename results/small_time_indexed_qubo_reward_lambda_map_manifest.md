
## Observed Reward-Lambda Target-Consistency Pattern

The reward-lambda target-consistency map confirmed that, once feasibility is stabilized by sufficiently large constraint penalties, target consistency is governed by the joint tuning of human_reward and lambda_target.

The stable feasible regime used constraint_penalty >= 5.0.

Within this regime, target-consistent optima were observed for the following reward/lambda regions:

- human_reward = 0.0 required lambda_target = 3.0
- human_reward = 1.0 required lambda_target >= 2.0
- human_reward = 2.0 required lambda_target >= 1.0
- human_reward = 3.0 required lambda_target >= 0.5
- human_reward = 4.0 required lambda_target >= 2.0

These patterns show that low human_reward values require stronger lambda_target values to induce human assignment, while excessively high human_reward values also require stronger lambda_target values to suppress over-assignment.

The widest target-consistent region in this small prototype occurred around human_reward = 3.0, where lambda_target values of 0.5 and above produced target-consistent feasible optima.

Overall, the result separates the roles of the QUBO weights: constraint_penalty stabilizes scheduling feasibility, while human_reward and lambda_target tune target-oriented human utilization.
