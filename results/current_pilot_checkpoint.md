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
