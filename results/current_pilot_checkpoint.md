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

## Additional Result: sample_4x4 Streamed QUBO Energy Validation PASS

The sample_4x4 streamed sparse QUBO coefficient export was validated using chunked CSV-based energy evaluation.

Across six sampled assignments, the streamed QUBO energy matched the direct representative objective with maximum absolute error approximately 1.14e-13.

The validation status was PASS.

This confirms that the streaming sparse export path can represent the intended sample_4x4 QUBO objective without loading the full QUBO into memory.

## Additional Result: sample_4x4 Merged Sparse QUBO Validation PASS

The sample_4x4 streamed sparse QUBO coefficients were merged by grouping duplicate (i,j) pairs and summing their coefficients.

The unmerged streamed file contained 8,872,562 rows, while the merged compact sparse QUBO contained 8,218,171 unique nonzero pairs.

The merged QUBO energy validation passed across six sampled assignments, with maximum absolute error approximately 1.14e-13 relative to the direct representative objective.

This establishes a solver-ready compact sparse QUBO representation pathway for sample_4x4, while keeping large coefficient CSV files as local ignored artifacts.

## Additional Checkpoint: sample_4x4 Solver-Ready Sparse QUBO Metadata

Solver-ready metadata was generated for the merged sample_4x4 sparse QUBO.

The metadata includes number of variables, constant offset, linear and quadratic term counts, coefficient ranges, sparse density estimates, scaling recommendation, and file schema.

This prepares the compact sparse QUBO representation for downstream solver experiments while keeping the large merged coefficient CSV as a local ignored artifact.

## Additional Result: sample_4x4 Solver-Ready Sparse QUBO Metadata

The solver-ready metadata analysis showed that the merged sample_4x4 sparse QUBO contains 8,713 binary variables and 8,218,171 nonzero upper-triangular coefficient terms.

The model has 8,713 linear terms and 8,209,458 quadratic terms, with quadratic density approximately 0.2163.

The coefficient range is [-35.4, 62.0], with absolute maximum 62.0 and recommended unit-range scaling factor approximately 0.016129.

This establishes the sample_4x4 QUBO as a solver-ready sparse coefficient representation, although still relatively dense due to target-utilization and scheduling constraint couplings.

## Additional Result: sample_4x4 Merged QUBO Local Search Prototype

A local classical heuristic search was run directly on the merged sample_4x4 sparse QUBO.

The merged QUBO contained 8,713 variables and 8,218,171 coefficient rows and was loaded without dense matrix construction.

In the full prototype run with 20 restarts and 5,000 iterations per restart, the best energy found was 51.25.

The feasible rate was 19 out of 20 restarts, or 0.95.

The best solution satisfied one-start assignment, resource-overlap, and precedence diagnostics and achieved exactly four human assignments, matching the target_human_assignments value.

This demonstrates that the solver-ready sparse QUBO can be used for energy-based local search, while remaining a prototype heuristic result rather than a proof of optimality.

## Additional Checkpoint: sample_4x4 Local QUBO Solution Component Analysis

The best solution found by the merged sample_4x4 QUBO local search was decomposed into interpretable objective components.

The analysis reports assignment cost, workload cost, ergonomic cost, start-time cost, reward term, target penalty, feasibility penalties, and machine/human/robot assignment counts.

The analysis also compares the local QUBO best solution against the previously established CP-SAT baseline values, with the caveat that the QUBO local-search objective includes human reward and target penalty terms.

## Additional Checkpoint: sample_4x4 Technical Validation Report

A consolidated technical validation report was created for the sample_4x4 human-centered QUBO scheduling pilot.

The report summarizes formulation validation, squared target penalty analysis, sparse QUBO export, streamed and merged energy validation, solver-ready metadata, local search, and solution component analysis.

This report is intended as an internal prototype/pilot validation document, not as a final manuscript.

## Additional Result: sample_4x4 CP-SAT Squared-Target Baseline

An objective-equivalent CP-SAT baseline was solved for the representative sample_4x4 squared-target QUBO objective.

The CP-SAT model returned OPTIMAL status with unscaled adjusted objective 47.70.

The solution had total_cost_without_reward = 57.70, human_count = 4, reward_term = 10.0, target_penalty = 0.0, and adjusted_objective = 47.70.

The previous local QUBO search best energy was 51.25, giving an absolute gap of 3.55 and a relative gap of approximately 7.44 percent against the CP-SAT squared-target optimum.

This confirms that the local QUBO heuristic found a feasible target-consistent solution but did not reach the objective-equivalent CP-SAT optimum.
