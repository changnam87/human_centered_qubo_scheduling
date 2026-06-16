# Small External Package SA Parameter Sensitivity Manifest

## Purpose

This step evaluates simulated annealing parameter sensitivity on the small external-solver-ready QUBO package.

The purpose is to measure how restarts, iterations, temperature schedule, and random seed affect the probability of recovering the known brute-force optimum.

## Reference Optimum

brute_force_optimum = 5.30
brute_force_bitstring = 100000000000100

## Script

scripts/run_small_external_package_sa_parameter_sensitivity.py

## Outputs

results/tables/small_external_package_sa_parameter_sensitivity_summary.csv
results/tables/small_external_package_sa_parameter_sensitivity_best.json
results/tables/small_external_package_sa_sensitivity/

## Interpretation Note

This is a small-package heuristic sensitivity test. It is not a full sample_4x4 solver benchmark and not a quantum hardware result.

## Observed Result

The full simulated annealing parameter sensitivity experiment evaluated 216 parameter cases.

The known brute-force optimum was 5.30 with bitstring 100000000000100.

The best observed case was run214_r200_it10000_t20.0_tf0.01_s456.

This case used 200 restarts, 10,000 iterations per restart, initial_temperature = 20.0, final_temperature = 0.01, and seed = 456.

The best energy was 5.30 with best bitstring 100000000000100.

The best gap to brute-force was approximately 8.88e-16, corresponding to numerical floating-point error.

The best case recovered the optimum in 145 out of 200 restarts, giving success_rate = 0.725.

Compared with the initial SA baseline success_rate of 0.14, parameter tuning substantially improved solver success rate.
