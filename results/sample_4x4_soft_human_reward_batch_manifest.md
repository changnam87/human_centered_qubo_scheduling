
## Observed Batch Threshold Pattern

The batch threshold analysis across seeds 2001–2010 showed a consistent
activation pattern for soft human reward.

At `human_reward = 0`, all 10 seeds selected zero human assignments. This
confirms that, without an explicit human-involvement incentive, the baseline
objective avoids human workers because human assignments activate workload and
ergonomic costs.

The first human assignment appeared at `human_reward = 2` for 9 of 10 seeds and
at `human_reward = 3` for 1 of 10 seeds. The threshold for at least two human
assignments was split between `human_reward = 2` and `human_reward = 3`. The
threshold for at least three human assignments was exactly `human_reward = 3`
for all 10 seeds.

At `human_reward = 5`, the solver selected 15 or 16 human assignments across
all seeds, suggesting that this reward level strongly dominates the added
human-centered workload and ergonomic costs.

Overall, these pilot results suggest that the soft human-reward term behaves as
intended: human involvement is avoided when reward is low, begins near a
seed-dependent threshold around reward 2–3, and becomes dominant when the reward
is sufficiently large.

These findings remain prototype-level validation results and should not yet be
framed as final empirical or paper-level claims.
