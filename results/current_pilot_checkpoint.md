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

## Additional Result: sample_4x4 Local Search Parameter Sensitivity

A local QUBO search parameter sensitivity experiment was completed using the merged sample_4x4 sparse QUBO.

The experiment evaluated 72 parameter cases across restarts, iterations, temperature schedules, and random seeds.

The best observed case used 30 restarts, 20,000 iterations, initial_temperature = 5.0, final_temperature = 0.001, and seed = 789.

This case achieved best_energy = 48.20 with feasible_rate = 1.0.

Compared with the CP-SAT squared-target optimum of 47.70, the tuned local QUBO gap was 0.50, or approximately 1.05 percent.

This reduced the previous local-search gap from 3.55 to 0.50, showing that parameter tuning substantially improves the local QUBO heuristic while still not proving optimality.

## Additional Checkpoint: sample_4x4 Tuned Local QUBO Solution Component Analysis

The best tuned local QUBO solution from the parameter sensitivity experiment was decomposed into interpretable objective components.

The analysis compares the tuned local solution against the objective-equivalent CP-SAT squared-target optimum.

This identifies which components explain the remaining gap between the tuned local QUBO solution and the CP-SAT optimum.

## Additional Result: sample_4x4 Tuned Local QUBO Component Gap Explanation

The tuned local QUBO solution had adjusted_objective = 48.20, compared with the CP-SAT squared-target optimum of 47.70.

The remaining absolute gap was 0.50, or approximately 1.05 percent.

Component analysis showed that assignment cost, workload cost, ergonomic cost, human_count, reward term, and target penalty matched the CP-SAT optimum.

The entire gap was due to start-time cost: 9.90 for the tuned local QUBO solution versus 9.40 for the CP-SAT optimum.

This indicates that the tuned local QUBO heuristic matched the CP-SAT human-centered allocation pattern but was slightly worse in timing optimization.

## Additional Checkpoint: Technical Validation Report Updated with CP-SAT Equivalent Baseline and Tuned Local Search

The sample_4x4 technical validation report was updated with STEP 20–22 results.

The update includes the objective-equivalent CP-SAT squared-target baseline, local QUBO search parameter sensitivity, and tuned local QUBO solution component-gap explanation.

The CP-SAT squared-target optimum was 47.70.

The tuned local QUBO best energy was 48.20, reducing the local-search gap to 0.50 or approximately 1.05 percent.

Component analysis showed that the remaining gap was entirely due to start-time cost, while human_count, workload cost, ergonomic cost, reward term, and target penalty matched the CP-SAT optimum.

## Additional Checkpoint: sample_4x4 QUBO-to-Ising Metadata

QUBO-to-Ising conversion metadata was generated for the merged sample_4x4 sparse QUBO.

The analysis uses the transformation x_i = (1 + s_i) / 2 and computes Ising offset, linear fields h_i, couplers J_ij, coefficient ranges, density, and scaling recommendations.

This prepares the prototype for downstream Ising-based solver experiments, quantum annealing formats, and QAOA-oriented representations.

This step does not yet run quantum hardware or quantum simulation.

## Additional Result: sample_4x4 Ising Energy Validation PASS

The sample_4x4 QUBO-to-Ising energy validation passed.

The validation compared merged QUBO energy and Ising-transformed energy on six sampled assignments using the mapping s_i = 2 x_i - 1.

The maximum absolute error was 0.0 and the mean absolute error was 0.0.

This confirms exact energy consistency between the merged sparse QUBO representation and the corresponding Ising energy representation on the sampled assignments.

This step validates the transformation only; it does not yet run quantum hardware, quantum annealing, or QAOA.

## Additional Checkpoint: Technical Validation Report Updated with Ising Results

The sample_4x4 technical validation report was updated with QUBO-to-Ising conversion metadata and Ising energy validation results.

The report now documents the QUBO-to-Ising transformation using s_i = 2 x_i - 1 and the corresponding energy conventions.

The Ising energy validation passed on six sampled assignments with max_abs_error = 0.0 and mean_abs_error = 0.0.

This confirms energy consistency between the merged sparse QUBO representation and the Ising-transformed representation at prototype validation level.

## Additional Checkpoint: Project README Updated

The project-level README was updated to summarize the prototype purpose, current validation status, sample_4x4 scale, key QUBO/CP-SAT/Ising results, important scripts, large artifact handling, and recommended next steps.

The README explicitly states that the project remains in prototype and pilot validation stage and has not yet executed quantum hardware, quantum annealing hardware, or QAOA.

## Additional Checkpoint: Project README Updated

The project-level README was updated to summarize the prototype purpose, current validation status, sample_4x4 scale, key QUBO/CP-SAT/Ising results, important scripts, large artifact handling, and recommended next steps.

The README explicitly states that the project remains in prototype and pilot validation stage and has not yet executed quantum hardware, quantum annealing hardware, or QAOA.

## Additional Result: sample_4x4 Runtime and Artifact Profile Summary

A runtime and artifact-size profile summary was generated for the sample_4x4 QUBO/Ising prototype pipeline.

The profile reports 8,713 variables, 8,218,171 merged terms, quadratic density approximately 0.2163, CP-SAT squared-target optimum 47.70, tuned local QUBO best 48.20, tuned gap 0.50, and Ising validation PASS with max_abs_error 0.0.

Runtime highlights include streaming sparse QUBO export approximately 21.39 seconds, streamed energy validation approximately 5.23 seconds, duplicate merge approximately 10.30 seconds, and merged energy validation approximately 3.58 seconds.

Large local artifact sizes include streamed QUBO coefficients approximately 800.64 MB, merged QUBO coefficients approximately 112.25 MB, and Ising couplers approximately 117.79 MB.

## Additional Checkpoint: README and Technical Report Updated with Runtime Profile

The README and sample_4x4 technical validation report were updated with runtime and artifact-size profile results.

The documentation now reports runtime highlights for streaming sparse QUBO export, streamed energy validation, duplicate merge, merged energy validation, and local QUBO search loading.

The documentation also reports large local artifact sizes, including approximately 800.64 MB for streamed QUBO coefficients, 112.25 MB for merged QUBO coefficients, and 117.79 MB for Ising couplers.

This improves the engineering transparency of the prototype/pilot validation workflow.

## Additional Checkpoint: Current Release-Style Summary Created

A release-style checkpoint summary was created for the current sample_4x4 QUBO/Ising prototype status.

The summary consolidates sample_4x4 scale, sparse QUBO size, CP-SAT squared-target optimum, tuned local QUBO result, QUBO-to-Ising validation, runtime/artifact profile, and recommended next steps.

The README was updated to point to this release-style checkpoint summary.

## Additional Checkpoint: sample_4x4 Reproducibility Workflow

A reproducibility workflow document and artifact-check script were added for the sample_4x4 QUBO/Ising prototype pipeline.

The workflow documents the recommended regeneration order for large ignored artifacts and downstream validation summaries.

The artifact-check script reports whether tracked summaries and large local ignored artifacts are present in the working tree.

## Additional Checkpoint: Small External-Solver-Ready Package

A compact external-solver-ready QUBO/Ising package was created for the small time-indexed scheduling instance.

The package includes raw QUBO coefficients, scaled QUBO coefficients, Ising linear fields, Ising couplers, package metadata, and QUBO/Ising energy validation.

This package is intended for lightweight external solver tests and does not represent the full sample_4x4 QUBO.

## Additional Checkpoint: Small External Solver Smoke Test

A minimal brute-force external solver smoke test was added for the small time-indexed QUBO/Ising package.

The test reads the exported QUBO and Ising files, enumerates all binary assignments, identifies the minimum-energy assignment, and validates QUBO/Ising energy consistency.

This confirms that the small package can be consumed as an external solver input.

## Additional Result: Small External Solver Smoke Test PASS

A minimal brute-force external solver smoke test was completed for the small time-indexed QUBO/Ising package.

The test enumerated all 32,768 assignments for the 15-variable package.

The best bitstring was 100000000000100 with best QUBO energy 5.30.

The corresponding Ising energy was 5.30, with maximum absolute QUBO-vs-Ising error approximately 1.14e-12.

The validation status was PASS, confirming that the small package can be consumed as a valid external QUBO/Ising solver input.

## Additional Checkpoint: README and Technical Report Updated with External Solver Package

The README and sample_4x4 technical validation report were updated with information about the small external-solver-ready QUBO/Ising package and brute-force smoke test.

The documentation now points to exports/small_time_indexed_solver_package/ and records the smoke-test result: 15 variables, 32,768 assignments enumerated, best bitstring 100000000000100, best QUBO energy 5.30, and validation status PASS.

This clarifies that the small package can be used as a lightweight external solver input, while remaining distinct from the full sample_4x4 QUBO.

## Additional Checkpoint: Small External Package Simulated Annealing Solver

A minimal simulated annealing solver was added for the small external-solver-ready QUBO package.

The solver reads the exported QUBO coefficients, performs bit-flip simulated annealing, and compares the best result against the brute-force optimum energy 5.30.

This provides the first heuristic solver baseline for the small external package.

## Additional Result: Small External Package Simulated Annealing Solver PASS

The minimal simulated annealing solver was run on the small 15-variable external QUBO package.

Using 100 restarts and 2,000 iterations per restart, the solver recovered the known brute-force optimum energy 5.30 and best bitstring 100000000000100.

The best gap to brute-force was approximately 8.88e-16, indicating numerical floating-point error only.

The optimum was reached in 14 out of 100 restarts, giving success_rate = 0.14.

This confirms that the small external-solver package can be consumed by a simple heuristic solver and that the known optimum can be recovered.

## Additional Checkpoint: Small External Solver Baselines Documented

The README, technical validation report, and release-style checkpoint summary were updated with the small external solver package baseline results.

The documentation now includes the brute-force smoke test result and the simulated annealing baseline result.

The simulated annealing solver recovered the brute-force optimum energy 5.30 and bitstring 100000000000100, with success_count = 14 out of 100 restarts.

This documents that the compact solver package can be consumed by both exhaustive and heuristic QUBO-style solvers.
