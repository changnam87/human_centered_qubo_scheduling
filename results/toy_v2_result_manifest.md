# Toy v2 Result Manifest

Generated at: 2026-06-15T17:00:14

## Purpose

This manifest summarizes the Toy v2 time-indexed human-centered scheduling experiment. Toy v2 extends the assignment-only Toy v1 model by adding start times, precedence constraints, resource-overlap constraints, horizon checks, and time-indexed QUBO/Ising representations.

## Toy v2 Model

- Operations: 4
- Resources: 3
- Time slots: 6
- Binary variables: 72
- Decision variable: x[o, r, t] = 1 if operation o starts on resource r at time t

## Generated Files

### Instance

| File | Status |
|---|---|
| `data/toy/toy_v2_time_indexed.json` | FOUND |

### QUBO validation

| File | Status |
|---|---|
| `results/tables/toy_v2_Q_matrix.csv` | FOUND |
| `results/tables/toy_v2_qubo_validation.csv` | FOUND |

### Ising validation

| File | Status |
|---|---|
| `results/tables/toy_v2_ising_h.csv` | FOUND |
| `results/tables/toy_v2_ising_J.csv` | FOUND |
| `results/tables/toy_v2_ising_validation.csv` | FOUND |

### Simulated annealing

| File | Status |
|---|---|
| `results/tables/toy_v2_simulated_annealing_results.csv` | FOUND |
| `results/tables/toy_v2_sa_sensitivity_summary.csv` | FOUND |
| `results/tables/toy_v2_sa_sensitivity_reads.csv` | FOUND |

### Benchmark summary

| File | Status |
|---|---|
| `results/tables/toy_v2_solver_benchmark_summary.csv` | FOUND |

### CP-SAT baseline

| File | Status |
|---|---|
| `results/tables/toy_v2_cpsat_result.csv` | FOUND |

### Figures

| File | Status |
|---|---|
| `results/figures/toy_v2_sa_feasibility_rate.png` | FOUND |
| `results/figures/toy_v2_sa_zero_penalty_rate.png` | FOUND |
| `results/figures/toy_v2_sa_mean_energy.png` | FOUND |

## Solver Benchmark Summary

| Component | Best energy/cost | Reference cost | Feasibility rate | Zero-penalty rate | Max validation error |
|---|---:|---:|---:|---:|---:|
| Toy v2 instance | nan | 18.8 | nan | nan | nan |
| Handcrafted feasible schedule | 18.8 | 18.8 | 1.0 | 1.0 | nan |
| QUBO matrix validation | 18.80000000000001 | 18.8 | nan | nan | 1.0658141036401504e-14 |
| Ising conversion validation | 18.80000002533052 | 18.8 | nan | nan | 2.5330507469334407e-08 |
| Infeasible schedule check | 118.6 | 18.8 | 0.0 | 0.0 | nan |
| CP-SAT baseline | 18.8 | 18.8 | 1.0 | 1.0 | nan |
| Simulated annealing | 18.8 | 18.8 | 0.99 | 0.7666666666666667 | nan |
| SA sensitivity best stability setting | 18.8 | 18.8 | 1.0 | 0.86 | nan |
| SA sensitivity best quality setting | 18.8 | 18.8 | 0.9666666666666668 | 0.6966666666666667 | nan |

## SA Sensitivity Summary

| Config | Steps | Initial T | Final T | Best cost | Feasibility rate | Zero-penalty rate | Mean energy |
|---|---:|---:|---:|---:|---:|---:|---:|
| steps_1000_T50_to_001 | 1000 | 50.0 | 0.01 | 19.0 | 0.6733333333333333 | 0.3833333333333333 | 44.41033333333335 |
| steps_3000_T50_to_001 | 3000 | 50.0 | 0.01 | 18.8 | 0.94 | 0.66 | 31.30733333333333 |
| steps_5000_T50_to_001 | 5000 | 50.0 | 0.01 | 18.8 | 0.97 | 0.7266666666666667 | 28.164 |
| steps_10000_T50_to_001 | 10000 | 50.0 | 0.01 | 18.8 | 1.0 | 0.86 | 23.821 |
| steps_5000_T20_to_001 | 5000 | 20.0 | 0.01 | 18.8 | 0.96 | 0.6833333333333333 | 31.50933333333332 |
| steps_5000_T100_to_001 | 5000 | 100.0 | 0.01 | 18.8 | 0.99 | 0.7666666666666667 | 27.048666666666666 |
| steps_5000_T50_to_01 | 5000 | 50.0 | 0.1 | 18.8 | 0.9966666666666668 | 0.8133333333333334 | 25.49866666666668 |
| steps_5000_T50_to_0001 | 5000 | 50.0 | 0.001 | 18.8 | 0.9666666666666668 | 0.6966666666666667 | 29.798666666666673 |

## Current Status

Completed Toy v2 pipeline:

- Time-indexed variable mapping
- Feasibility checker
- Infeasible case validation
- Function-based cost and penalty evaluator
- Time-indexed QUBO matrix construction
- QUBO energy validation
- Ising Hamiltonian conversion
- Ising energy validation
- CP-SAT classical baseline
- Simulated annealing baseline
- SA sensitivity analysis
- Solver benchmark summary
- SA sensitivity figures

## Recommended Next Step

The next recommended step is to move from toy instances to benchmark-derived instances. A practical next target is to implement a parser and augmentation pipeline for a small public job-shop or flexible job-shop benchmark instance, then add synthetic human-centered attributes such as workload, ergonomic risk, skill compatibility, safety risk, and robot utilization targets.
