# Small Time-Indexed Solver Package\n\nThis folder contains a compact QUBO/Ising package for external solver tests.\n\nThis package is intentionally small. It is not the full sample_4x4 QUBO.\n\n## Files\n\n- qubo_coefficients.csv: raw upper-triangular QUBO coefficients.\n- qubo_coefficients_scaled_unit_abs.csv: QUBO coefficients scaled by abs max.\n- ising_linear_fields.csv: Ising h_i fields.\n- ising_couplers.csv: Ising J_ij couplers.\n- package_metadata.json: package metadata and coefficient ranges.\n- energy_validation.csv: sampled QUBO/Ising energy comparison.\n- energy_validation_summary.json: validation summary.\n\n## Energy conventions\n\nQUBO: E(x) = constant + sum_{i<=j} Q_ij x_i x_j\n\nIsing: E(s) = offset + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j\n\nMapping: s_i = 2*x_i - 1.\n\n## Validation\n\nQUBO and Ising energies are validated on sampled assignments.\n\nValidation status: PASS\nMax abs error: 9.094947017729282e-13\n
## dimod-compatible BQM-style exports

This package also includes dimod-compatible BQM-style exports.

These files do not require dimod to be installed, but they follow the BinaryQuadraticModel structure:

```text
BINARY BQM:
energy = offset + sum_i linear[i] x_i + sum_{i<j} quadratic[i,j] x_i x_j

SPIN BQM:
energy = offset + sum_i linear[i] s_i + sum_{i<j} quadratic[i,j] s_i s_j
```

Files:

```text
small_time_indexed_dimod_binary_bqm.json
small_time_indexed_dimod_spin_bqm.json
small_time_indexed_dimod_binary_linear.csv
small_time_indexed_dimod_binary_quadratic.csv
small_time_indexed_dimod_spin_linear.csv
small_time_indexed_dimod_spin_quadratic.csv
small_time_indexed_dimod_bqm_export_summary.json
```

These exports prepare the small package for D-Wave Ocean/dimod-style workflows, but they do not execute D-Wave hardware or quantum annealing.

## dimod-compatible BQM-style exports

This package also includes dimod-compatible BQM-style exports.

These files do not require dimod to be installed, but they follow the BinaryQuadraticModel structure:

```text
BINARY BQM:
energy = offset + sum_i linear[i] x_i + sum_{i<j} quadratic[i,j] x_i x_j

SPIN BQM:
energy = offset + sum_i linear[i] s_i + sum_{i<j} quadratic[i,j] s_i s_j
```

Files:

```text
small_time_indexed_dimod_binary_bqm.json
small_time_indexed_dimod_spin_bqm.json
small_time_indexed_dimod_binary_linear.csv
small_time_indexed_dimod_binary_quadratic.csv
small_time_indexed_dimod_spin_linear.csv
small_time_indexed_dimod_spin_quadratic.csv
small_time_indexed_dimod_bqm_export_summary.json
```

These exports prepare the small package for D-Wave Ocean/dimod-style workflows, but they do not execute D-Wave hardware or quantum annealing.

## Scaled QUBO/Ising Exports

The package includes scaled QUBO and Ising coefficient exports for solver-readiness testing.

The scaling uses a positive factor, so the energy ordering and argmin are preserved.

Energy relation:

```text
scaled_energy = unscaled_energy * scale_factor
```

Files:

```text
small_time_indexed_scaled_qubo_coefficients.csv
small_time_indexed_scaled_ising_linear_fields.csv
small_time_indexed_scaled_ising_couplers.csv
small_time_indexed_scaled_scaling_metadata.json
```

Validation output:

```text
results/tables/small_package_scaled_export_validation.csv
results/tables/small_package_scaled_export_validation_summary.json
```

This is a coefficient-format validation step and does not execute quantum hardware, quantum annealing, dimod, or QAOA.
