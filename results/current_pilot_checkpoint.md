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
