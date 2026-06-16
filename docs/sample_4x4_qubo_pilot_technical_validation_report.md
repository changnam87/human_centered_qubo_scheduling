# sample_4x4 Human-Centered QUBO Scheduling Pilot Technical Validation Report

## Purpose

This document consolidates the prototype and pilot validation results for the `sample_4x4` human-centered QUBO scheduling workflow.

This is not a final research paper. It is an internal technical validation report documenting the current prototype state, formulation checks, scaling observations, sparse QUBO export pipeline, and local heuristic search results.

## Current Prototype Status

The project has advanced from toy QUBO formulation checks to a solver-ready sparse QUBO representation for a larger time-indexed scheduling instance.

Completed major checkpoints include:

1. CP-SAT baseline and human-centered sensitivity analysis.
2. QUBO-compatible squared target human-utilization penalty.
3. Toy, small, and medium QUBO coefficient export validation.
4. sample_4x4 sparse streaming QUBO export.
5. Streamed and merged QUBO energy validation.
6. Solver-ready sparse QUBO metadata.
7. Local heuristic search on the merged sparse QUBO.
8. Local QUBO solution component analysis.

## sample_4x4 Scale

```text
jobs = 4
operations per job = 4
operations = 16
machines = 4
workers = 3
robots = 2
resources = 9
planning horizon = 63
nominal binary variables = 16 * 9 * 63 = 9072
representative valid-start variables = 8713
```

## Baseline CP-SAT Result

The baseline CP-SAT model produced:

```text
status = OPTIMAL
total cost = 57.0
total penalty = 0.0
human assignments = 0
workload = 0.0
ergonomic = 0.0
```

The baseline avoided human workers because assigning humans activates workload and ergonomic cost components.

## QUBO-Compatible Human-Utilization Formulation

The preferred QUBO-compatible formulation is:

```text
objective =
    total_cost_without_reward
    - human_reward * human_count
    + lambda_target * (human_count - target)^2
```

The squared target penalty expands into linear and quadratic binary terms, making it directly compatible with QUBO and Ising formulations.

## sample_4x4 Sparse QUBO Export

The representative sample_4x4 sparse QUBO export produced:

```text
representative valid-start variables = 8713
unmerged streamed coefficient rows = 8872562
merged unique nonzero coefficient pairs = 8218171
linear terms = 8713
quadratic terms = 8209458
constant offset = 496.0
```

The large streamed and merged coefficient CSV files are local ignored artifacts and should not be committed directly to GitHub.

## Energy Validation

Both streamed and merged sparse QUBO energy validations passed.

```text
max_abs_error approximately 1.14e-13
mean_abs_error approximately 6.63e-14
validation_status = PASS
```

This confirms that the sparse coefficient exports are internally consistent with the representative direct objective.

## Solver-Ready Metadata

The merged sample_4x4 sparse QUBO has:

```text
num_variables = 8713
total_terms = 8218171
linear_terms = 8713
quadratic_terms = 8209458
quadratic_density approximately 0.2163
coefficient_min = -35.4
coefficient_max = 62.0
coefficient_abs_max = 62.0
scale_to_unit_abs_max approximately 0.016129
```

The formulation is stored sparsely, but it is relatively dense for a sparse QUBO because the squared target human-utilization penalty creates many pairwise human-variable couplings.

## Local QUBO Search Result

A prototype operation-level local search was run directly on the merged sparse QUBO.

```text
restarts = 20
iterations per restart = 5000
best_energy = 51.25
feasible_runs = 19 / 20
feasible_rate = 0.95
```

The best solution selected all 16 operations, satisfied assignment/resource/precedence diagnostics, and achieved exactly four human assignments.

## Local QUBO Solution Component Analysis

The best local QUBO solution was decomposed into interpretable objective components, including assignment cost, workload cost, ergonomic cost, start-time cost, reward term, squared target penalty, feasibility penalties, and machine/human/robot assignment counts.

This enables diagnostic comparison against the CP-SAT baseline. The comparison should be interpreted carefully because the local QUBO objective includes human reward and target penalty terms.

## Interpretation

The current prototype supports the following pilot-level findings:

1. The human-centered scheduling formulation can be represented as a QUBO-compatible objective.
2. The squared target human-utilization penalty controls human assignment around a target level.
3. sample_4x4-scale sparse QUBO export is feasible using streaming and merging.
4. Dense QUBO matrix construction is inappropriate at this scale.
5. The merged sparse QUBO can be validated and used for local energy-based search.
6. The best local-search solution was feasible and target-consistent.

These are prototype validation findings, not final paper-level empirical claims.

## Limitations

1. The sample_4x4 QUBO is a representative deterministic export, not yet seed-specific for every augmented instance.
2. Local search does not prove global optimality.
3. CP-SAT baseline and local QUBO objective variants are not always directly equivalent.
4. Hardware quantum or annealing solver execution has not yet been performed.
5. Runtime and memory benchmarking have not yet been systematically performed across instance sizes.

## Recommended Next Steps

1. Add a CP-SAT baseline under the same squared-target QUBO objective.
2. Compare local QUBO search against objective-equivalent CP-SAT.
3. Add local search parameter sensitivity.
4. Implement QUBO-to-Ising conversion.
5. Prepare scaled coefficient export for bounded-range solvers.
6. Expand from representative sample_4x4 to seed-specific sample_4x4 exports.

## Overall Conclusion

The prototype has advanced from conceptual human-centered QUBO formulation to a solver-ready sparse QUBO pipeline at sample_4x4 scale.

The current end-to-end path is:

```text
human-centered scheduling formulation
    -> QUBO-compatible squared target penalty
    -> time-indexed sparse QUBO export
    -> streamed coefficient validation
    -> duplicate-merged compact sparse QUBO
    -> solver-ready metadata
    -> local energy-based heuristic search
    -> interpretable component analysis
```

This establishes a strong prototype foundation for future solver experiments, QUBO-to-Ising conversion, and eventual research-paper development.

---

## Addendum: Objective-Equivalent CP-SAT Baseline and Tuned Local QUBO Search

This addendum updates the technical validation report with results from the objective-equivalent CP-SAT squared-target baseline, local QUBO search parameter sensitivity, and tuned local QUBO solution component analysis.

## CP-SAT Squared-Target Objective-Equivalent Baseline

The original CP-SAT baseline minimized total cost without human reward or squared target penalty. To create a fairer comparison against the representative QUBO local search objective, a new CP-SAT model was solved using the same squared-target objective:

```text
objective = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target_human_assignments)^2
```

The parameters were:

```text
human_reward = 2.5
lambda_target = 1.0
target_human_assignments = 4
scale = 100
```

The CP-SAT model returned OPTIMAL status.

```text
scaled objective = 4770.0
unscaled adjusted objective = 47.70
total_cost_without_reward = 57.70
human_count = 4
machine_count = 12
robot_count = 0
reward_term = 10.0
target_penalty = 0.0
```

The component recomputation matched the solver objective within numerical tolerance.

This objective-equivalent CP-SAT result provides a stronger comparison point for the local QUBO heuristic than the original total-cost-only CP-SAT baseline.

## Local QUBO Search Parameter Sensitivity

The previous local QUBO search best solution had:

```text
best_energy = 51.25
CP-SAT squared-target optimum = 47.70
absolute gap = 3.55
relative gap approximately 7.44 percent
```

A parameter sensitivity experiment was then run over local search settings.

The full sensitivity grid included:

```text
restarts = 30, 50
iterations = 10000, 20000
initial_temperature = 5.0, 10.0, 20.0
final_temperature = 0.001, 0.01
seeds = 123, 456, 789
total cases = 72
```

The best observed case was:

```text
run_id = 20
tag = run020_r30_it20000_t5.0_tf0.001_s789
restarts = 30
iterations = 20000
initial_temperature = 5.0
final_temperature = 0.001
seed = 789
best_energy = 48.20
feasible_rate = 1.0
```

This reduced the gap to the CP-SAT optimum:

```text
new absolute gap = 48.20 - 47.70 = 0.50
new relative gap approximately 1.05 percent
```

Interpretation: local QUBO heuristic performance improved substantially through parameter tuning, reducing the previous gap from 3.55 to 0.50 energy units.

## Tuned Local QUBO Solution Component Analysis

The best tuned local QUBO solution was decomposed into interpretable objective components and compared against the CP-SAT squared-target optimum.

The tuned local solution had:

```text
adjusted_objective = 48.20
total_cost_without_reward = 58.20
human_count = 4
machine_count = 12
robot_count = 0
reward_term = 10.0
target_penalty = 0.0
feasibility violations = 0
```

The CP-SAT squared-target optimum had:

```text
adjusted_objective = 47.70
total_cost_without_reward = 57.70
human_count = 4
machine_count = 12
robot_count = 0
reward_term = 10.0
target_penalty = 0.0
```

The component comparison showed that the tuned local solution matched the CP-SAT optimum in assignment cost, workload cost, ergonomic cost, human_count, reward term, and target penalty.

The remaining 0.50 objective gap was entirely explained by start-time cost:

```text
CP-SAT start_time_cost = 9.40
tuned local QUBO start_time_cost = 9.90
difference = 0.50
```

Interpretation: the tuned local QUBO heuristic matched the CP-SAT human-centered allocation pattern but remained slightly worse in timing optimization.

## Updated Pilot-Level Interpretation

The updated results strengthen the prototype validation in several ways:

1. An objective-equivalent CP-SAT optimum is now available for the squared-target QUBO objective.
2. The local QUBO heuristic can be evaluated against this objective-equivalent optimum.
3. Parameter tuning reduced the local-search gap from approximately 7.44 percent to approximately 1.05 percent.
4. The remaining gap is not due to human-centered allocation failure; it is due to a small start-time cost difference.
5. The tuned local QUBO solution is feasible and target-consistent.

These findings remain prototype/pilot validation results. They do not prove global optimality of the local QUBO heuristic, but they show that the merged sparse QUBO representation supports meaningful near-optimal energy-based search on the representative sample_4x4 instance.

---

## Addendum: QUBO-to-Ising Conversion and Energy Validation

This addendum updates the technical validation report with the QUBO-to-Ising conversion metadata and energy validation results.

## QUBO-to-Ising Conversion

The merged sample_4x4 sparse QUBO was converted conceptually into an Ising representation using the standard binary-to-spin transformation:

```text
s_i = 2 x_i - 1
x_i = (1 + s_i) / 2
```

The QUBO energy convention is:

```text
E_QUBO(x) = constant + sum_i Q_ii x_i + sum_{i<j} Q_ij x_i x_j
```

The Ising energy convention is:

```text
E_Ising(s) = offset + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j
```

The conversion rules are:

```text
Q_ii x_i = Q_ii / 2 + Q_ii / 2 * s_i
Q_ij x_i x_j = Q_ij / 4 * (1 + s_i + s_j + s_i s_j)
J_ij = Q_ij / 4
```

The QUBO-to-Ising metadata analysis generated Ising linear fields, coupler metadata, coefficient ranges, density information, and scaling recommendations.

This step prepares the prototype for downstream Ising-based solvers, quantum annealing formats, and QAOA-oriented representations.

## Ising Energy Validation

The QUBO-to-Ising energy validation compared merged QUBO energy and Ising-transformed energy on sampled assignments.

Validation samples included:

```text
tuned_local_best
all_zero
random_one_start_0
random_one_start_1
random_sparse_0
random_sparse_1
```

Observed result:

```text
num_samples = 6
max_abs_error = 0.0
mean_abs_error = 0.0
validation_status = PASS
```

Interpretation: the sample_4x4 QUBO-to-Ising transformation is energy-consistent on the sampled assignments.

This validates the mathematical transformation from QUBO to Ising energy representation. It does not yet indicate quantum hardware execution, quantum annealing execution, or QAOA simulation.

## Updated Prototype Status

With this update, the prototype now supports the following validated path:

```text
human-centered scheduling formulation
    -> QUBO-compatible squared target penalty
    -> time-indexed sparse QUBO export
    -> streamed coefficient validation
    -> duplicate-merged compact sparse QUBO
    -> solver-ready QUBO metadata
    -> local energy-based heuristic search
    -> objective-equivalent CP-SAT comparison
    -> tuned local search gap analysis
    -> QUBO-to-Ising metadata
    -> Ising energy validation
```

The project remains in prototype and pilot validation stage. The current work validates formulation, sparse representation, local heuristic search, and QUBO-to-Ising energy consistency, but it has not yet performed quantum hardware execution.

---

## Addendum: Runtime and Artifact Profile

This addendum summarizes runtime and artifact-size observations for the sample_4x4 QUBO/Ising prototype pipeline.

The profile was generated from existing result artifacts and did not rerun heavy experiments.

## Key Engineering Results

```text
num_variables = 8713
merged_terms = 8218171
quadratic_density approximately 0.2163
CP-SAT squared-target optimum = 47.70
tuned local QUBO best = 48.20
tuned gap to CP-SAT = 0.50
Ising validation status = PASS
Ising validation max_abs_error = 0.0
```

## Runtime Highlights

```text
streaming sparse QUBO export = approximately 21.39 seconds
streamed QUBO energy validation = approximately 5.23 seconds
duplicate merge = approximately 10.30 seconds
merged QUBO energy validation = approximately 3.58 seconds
local QUBO initial search load = approximately 3.15 seconds
```

## Large Local Artifact Sizes

```text
streamed QUBO coefficients CSV = approximately 800.64 MB
merged QUBO coefficients CSV = approximately 112.25 MB
Ising couplers CSV = approximately 117.79 MB
Ising linear fields CSV = approximately 0.12 MB
```

## Interpretation

The runtime profile indicates that streaming export, duplicate merge, and energy validation are practical at the representative sample_4x4 scale on a local development machine.

The artifact-size profile confirms that large coefficient files should remain local ignored artifacts. The streamed QUBO coefficient file is especially large, while the merged sparse QUBO and Ising coupler files are smaller but still unsuitable for ordinary Git tracking.

This supports the current engineering strategy: commit scripts, metadata, summaries, manifests, and compact validation outputs, while keeping large coefficient artifacts local or storing them externally if needed.

---

## Addendum: Small External Solver Package and Smoke Test

A compact external-solver-ready QUBO/Ising package was created for a small time-indexed scheduling instance.

This package is intentionally small and is separate from the full sample_4x4 QUBO.

## Package Directory

```text
exports/small_time_indexed_solver_package/
```

The package includes raw QUBO coefficients, scaled QUBO coefficients, Ising linear fields, Ising couplers, package metadata, and QUBO/Ising energy validation outputs.

## Smoke Test

A minimal brute-force smoke test was run on the package.

The smoke test enumerated all binary assignments and checked QUBO-vs-Ising energy consistency.

Observed result:

```text
num_variables = 15
num_assignments_enumerated = 32768
best_bitstring = 100000000000100
best_qubo_energy = 5.30
best_ising_energy = 5.30
max_abs_error_qubo_vs_ising approximately 1.14e-12
validation_status = PASS
```

Interpretation: the small external-solver package can be consumed as a valid QUBO/Ising solver input.

This smoke test is not a full sample_4x4 solve and is not a quantum hardware result. It is a lightweight package-level validation step for external solver readiness.

---

## Addendum: Small External Solver Baselines

The small external-solver-ready QUBO/Ising package was evaluated with two baseline solver checks: exhaustive brute-force enumeration and a minimal simulated annealing heuristic.

## Brute-Force Smoke Test

The brute-force smoke test enumerated all binary assignments for the 15-variable small package.

Observed result:

```text
num_variables = 15
num_assignments_enumerated = 32768
best_bitstring = 100000000000100
best_qubo_energy = 5.30
best_ising_energy = 5.30
max_abs_error_qubo_vs_ising approximately 1.14e-12
validation_status = PASS
```

This confirms that the exported small package can be consumed as a valid QUBO/Ising input and that QUBO and Ising energies are numerically consistent across the exhaustive assignment set.

## Simulated Annealing Baseline

A minimal bit-flip simulated annealing solver was run on the same 15-variable QUBO package.

Observed result:

```text
restarts = 100
iterations per restart = 2000
initial_temperature = 10.0
final_temperature = 0.001
brute_force_optimum = 5.30
SA best_energy = 5.30
best_bitstring = 100000000000100
best_gap_to_bruteforce approximately 8.88e-16
success_count = 14 / 100
success_rate = 0.14
validation_status = PASS
```

The simulated annealing solver recovered the known brute-force optimum and the same best bitstring. The optimum was reached in 14 out of 100 restarts under the tested settings.

Interpretation: the small external-solver package is usable by both exhaustive and heuristic solvers. The simulated annealing result confirms solver-readiness while also showing stochastic sensitivity to initialization and annealing trajectory.

This remains a small-package solver baseline. It is not a full sample_4x4 solve and is not a quantum hardware or QAOA result.

---

## Addendum: Small External Package SA Parameter Sensitivity

The small external-solver-ready QUBO package was used for simulated annealing parameter sensitivity.

The experiment evaluated 216 parameter cases across restarts, iterations, temperature schedules, and random seeds.

## Reference Optimum

```text
brute_force_optimum = 5.30
brute_force_bitstring = 100000000000100
```

## Initial SA Baseline

The initial simulated annealing baseline used 100 restarts and 2,000 iterations per restart.

```text
success_count = 14 / 100
success_rate = 0.14
```

## Best Sensitivity Case

The best observed parameter setting was:

```text
run_id = 214
tag = run214_r200_it10000_t20.0_tf0.01_s456
restarts = 200
iterations per restart = 10000
initial_temperature = 20.0
final_temperature = 0.01
seed = 456
best_energy = 5.30
best_bitstring = 100000000000100
success_count = 145 / 200
success_rate = 0.725
validation_status = PASS
```

## Interpretation

Parameter tuning substantially improved the simulated annealing optimum-recovery rate for the small external package.

The success rate improved from 0.14 in the initial baseline to 0.725 in the best tested sensitivity setting.

This confirms that the small package can support heuristic solver experiments and parameter-sensitivity studies.

This remains a small-package solver-readiness result. It is not a full sample_4x4 solve and not a quantum hardware or QAOA result.
