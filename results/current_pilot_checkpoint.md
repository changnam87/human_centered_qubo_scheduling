# Current Pilot Checkpoint

## Git checkpoint

Latest local commit:

2775aba Add human-centered QUBO scheduling pilot validation

## Current project status

This project is currently in the prototype and pilot validation stage, not the final paper-writing stage.

Completed pipeline:

- Toy v1 QUBO validation
- Toy v2 time-indexed QUBO validation
- sample_3x3 single benchmark-derived pilot
- sample_3x3 batch pilot across 10 synthetic augmentation seeds
- sample_4x4 larger pilot
- CP-SAT baseline validation
- Structure-aware local search
- Hard human-utilization constraint variant
- Human-utilization sensitivity analysis
- Soft human-reward sensitivity analysis
- Soft human-reward QUBO validation
- Figures and manifests for pilot tracking

## Recommended next steps

1. Push this local repo to GitHub.
2. Extend soft human-reward sensitivity across multiple augmentation seeds.
3. Add another benchmark-derived instance beyond sample_4x4.
4. Decide which experiments remain pilot-only and which should become paper-scale experiments.
5. Formalize the multi-objective trade-off model more rigorously.
6. Later, after the pipeline is stable, begin actual manuscript writing.

## Additional Checkpoint: QUBO-Compatible Squared Target Penalty

The prototype was extended from absolute target-deviation control to a QUBO-compatible squared target human-utilization penalty.

The squared target formulation uses:

objective = total_cost_without_reward - human_reward * human_count + lambda_target * (human_count - target)^2

This formulation is directly expandable into linear and quadratic binary terms because human_count is a sum of binary human-assignment indicators.

A toy-level QUBO expansion validation confirmed exact agreement between the direct squared penalty and its expanded QUBO form.

The sample_4x4 squared target penalty batch showed that appropriate lambda_target values can achieve target_human_assignments = 4 across all tested human_reward settings.

A full sample_4x4 energy validation recomputed the squared-target objective for each solved row and compared it against the stored adjusted_objective_manual value.

This provides a formulation-level checkpoint for moving from CP-SAT prototype validation toward QUBO/Ising implementation.

## Additional Checkpoint: Toy QUBO Coefficient Export

A toy assignment-level QUBO was exported for the QUBO-compatible squared target human-utilization formulation.

The toy model used 4 operations and 3 resources, yielding 12 binary variables.

The exported QUBO included assignment cost, workload and ergonomic human-centered cost, soft human reward, squared target human-utilization penalty, and one-hot assignment penalties.

The QUBO coefficient dictionary was saved in explicit coefficient form as Q[i,j].

Brute-force validation over all 2^12 binary assignments confirmed that the exported QUBO energy matched the direct objective.

This provides the first explicit coefficient-export checkpoint for moving from CP-SAT equivalent validation to actual QUBO/Ising implementation.

## Additional Result: Small Time-Indexed QUBO Penalty Calibration

The small time-indexed QUBO parameter sensitivity identified a clear feasibility threshold for the constraint penalty.

With constraint_penalty = 1.0, the QUBO optimum was infeasible for all tested settings.

With constraint_penalty >= 5.0, the QUBO optimum was feasible for all tested settings, with assignment, overlap, and precedence violations reduced to zero.

The target-consistent rate remained 0.48 at stable constraint penalties, indicating that feasibility is controlled by constraint penalties, while human-utilization target consistency depends on human_reward and lambda_target calibration.

## Additional Checkpoint: Small Time-Indexed QUBO Reward-Lambda Target Map

After identifying a stable feasibility regime for the small time-indexed QUBO, a reward/lambda target-consistency map was generated.

The analysis filtered to constraint_penalty >= 5.0 and evaluated which human_reward and lambda_target combinations produced feasible and target-consistent QUBO optima.

This separates the role of constraint penalties from the role of human-utilization parameters: constraint_penalty stabilizes feasibility, while human_reward and lambda_target tune human target consistency.

The resulting map provides a small-scale calibration checkpoint before scaling toward larger time-indexed QUBO instances.

## Additional Result: Reward-Lambda Target-Consistency Map

In the small time-indexed QUBO, the stable feasible regime was defined by constraint_penalty >= 5.0.

Within this feasible regime, target consistency depended on the joint tuning of human_reward and lambda_target.

Low human_reward values required larger lambda_target values to induce human assignment, while excessive human_reward values required larger lambda_target values to suppress over-assignment.

The widest target-consistent tuning region occurred near human_reward = 3.0, where lambda_target >= 0.5 produced feasible target-consistent optima.

This result confirms the separation of roles among QUBO weights: constraint penalties enforce scheduling feasibility, while human_reward and lambda_target control human-utilization behavior.

## Additional Checkpoint: Medium Time-Indexed QUBO Export

A medium time-indexed QUBO export was added with 3 operations, 3 resources, and horizon 6.

The model uses x[operation, resource, start_time] variables and includes assignment/start-time cost, human-centered workload and ergonomic costs, soft human reward, squared target human-utilization penalty, one-start assignment penalties, resource overlap penalties, and precedence penalties.

Because brute-force validation becomes expensive as variable count grows, the medium prototype uses sampled energy validation plus a generated greedy feasible schedule.

A QUBO size scaling summary was also created to compare assignment-only toy, small time-indexed, medium time-indexed, and sample_4x4-scale formulations.

## Additional Checkpoint: sample_4x4 QUBO Export Feasibility

A sample_4x4 QUBO export feasibility study was added.

The study estimates variable count, sparse coefficient term count, memory requirements, and dominant QUBO components for the 16-operation, 9-resource, 63-horizon sample_4x4 scale.

The purpose is to determine whether full sparse QUBO coefficient export should be performed in memory or via streaming CSV export.

This prepares the project for a future full sample_4x4 sparse QUBO coefficient export without yet attempting QUBO optimization at that scale.

## Additional Result: sample_4x4 QUBO Export Feasibility Findings

The sample_4x4 QUBO export feasibility study estimated 8,713 representative valid-start variables and 8,860,966 sparse QUBO terms before coefficient merging.

The dominant source of quadratic terms was the squared target human-utilization penalty, with 4,154,403 pairwise terms among 2,883 human variables.

Assignment one-start penalties and precedence forbidden-pair penalties were also major contributors.

The memory estimates suggest that dense QUBO export is inappropriate and that full sparse export should use streaming CSV or component-wise writing rather than a monolithic in-memory dictionary.

This establishes the need for a streaming sample_4x4 sparse QUBO export strategy as the next prototype step.

## Additional Checkpoint: sample_4x4 Streaming Sparse QUBO Export

A streaming sparse QUBO coefficient export prototype was added for sample_4x4 scale.

The exporter writes coefficient rows directly to CSV without constructing a dense matrix or monolithic in-memory QUBO dictionary.

The exported term groups include linear cost/reward terms, squared target human-utilization terms, one-start assignment penalty terms, resource overlap penalty terms, and precedence penalty terms.

The streamed coefficient file is intentionally unmerged, preserving term_group labels for component-level analysis and validation.

This establishes a scalable export path before attempting sample_4x4 QUBO optimization.

## Additional Checkpoint: sample_4x4 Streamed QUBO Energy Validation

A component-wise energy validation was added for the sample_4x4 streamed sparse QUBO export.

The validation reads the large local coefficient CSV in chunks and compares streamed QUBO energy against direct objective values for sampled assignments.

This confirms whether the streaming sparse coefficient export is internally consistent without loading the full QUBO dictionary into memory.

The large coefficient CSV remains a local ignored artifact, while validation summaries are tracked in Git.
