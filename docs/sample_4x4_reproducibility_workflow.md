# sample_4x4 Reproducibility Workflow

## Purpose

This document explains how to reproduce or regenerate the major sample_4x4 QUBO/Ising prototype artifacts.

The repository tracks scripts, compact summaries, manifests, and validation outputs. Large coefficient artifacts are intentionally ignored by Git.

## Project Stage

Current stage:

```text
prototype + pilot validation
```

This workflow does not represent a final manuscript pipeline and does not execute quantum hardware, quantum annealing hardware, or QAOA.

## Large Local Artifacts

The following large files are usually local ignored artifacts:

```text
results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv
results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv
results/tables/sample_4x4_ising_couplers.csv
```

These files may need to be regenerated before rerunning downstream validation or solver steps.

## Artifact Check

Before reproducing the pipeline, check which artifacts are present:

```bash
python scripts/check_sample_4x4_reproducibility_artifacts.py
```

This creates:

```text
results/tables/sample_4x4_reproducibility_artifact_check_summary.json
```

## Recommended Regeneration Order

Recommended high-level order:

```text
1. Generate sample_4x4 sparse QUBO stream.
2. Validate streamed QUBO energy.
3. Merge duplicate QUBO coefficients.
4. Validate merged QUBO energy.
5. Generate solver-ready QUBO metadata.
6. Run local QUBO search.
7. Run CP-SAT squared-target baseline.
8. Run local search parameter sensitivity.
9. Analyze tuned local solution components.
10. Generate QUBO-to-Ising metadata.
11. Validate Ising energy consistency.
12. Summarize runtime and artifact profile.
```

## Key Commands

### 1. Streamed sparse QUBO export

```bash
python scripts/export_sample_4x4_sparse_qubo_streaming.py
```

### 2. Streamed QUBO energy validation

```bash
python scripts/validate_sample_4x4_streamed_qubo_energy.py --chunksize 250000
```

### 3. Merge duplicate sparse QUBO coefficients

```bash
python scripts/merge_sample_4x4_streamed_qubo_coefficients.py --chunksize 500000
```

### 4. Merged QUBO energy validation

```bash
python scripts/validate_sample_4x4_merged_qubo_energy.py --chunksize 250000
```

### 5. Solver-ready QUBO metadata

```bash
python scripts/analyze_sample_4x4_solver_ready_qubo.py --chunksize 500000
```

### 6. Local QUBO search

```bash
python scripts/run_sample_4x4_merged_qubo_local_search.py --restarts 20 --iterations 5000 --chunksize 500000 --seed 123 --initial-temperature 10.0 --final-temperature 0.01
```

### 7. CP-SAT squared-target baseline

```bash
python scripts/run_sample_4x4_cpsat_squared_target_baseline.py --human-reward 2.5 --lambda-target 1.0 --target-human-assignments 4 --time-limit-seconds 60 --num-workers 8
```

### 8. Local search parameter sensitivity

```bash
python scripts/run_sample_4x4_local_search_parameter_sensitivity.py --chunksize 500000
```

### 9. Tuned local solution component analysis

```bash
python scripts/analyze_sample_4x4_tuned_local_solution_components.py
```

### 10. QUBO-to-Ising metadata

```bash
python scripts/analyze_sample_4x4_qubo_to_ising_metadata.py --chunksize 500000
```

### 11. Ising energy validation

```bash
python scripts/validate_sample_4x4_ising_energy.py --chunksize 500000
```

### 12. Runtime and artifact profile

```bash
python scripts/summarize_sample_4x4_runtime_memory_profile.py
```

## Expected Current Checkpoint Values

At the current checkpoint, expected headline values are:

```text
num_variables = 8713
merged QUBO terms = 8218171
CP-SAT squared-target optimum = 47.70
tuned local QUBO best = 48.20
gap to CP-SAT = 0.50
Ising validation max_abs_error = 0.0
```

## Notes

Some scripts depend on large ignored artifacts. If a required CSV is missing, rerun the upstream generation step first.

The preferred strategy is to commit compact summaries and manifests, while keeping large coefficient files local or storing them externally.
