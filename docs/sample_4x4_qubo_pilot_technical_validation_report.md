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
