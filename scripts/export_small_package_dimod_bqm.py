"""Export small external QUBO/Ising package to dimod-compatible BQM-style files.

This script does not require dimod to be installed.
It creates JSON and CSV files that follow the BinaryQuadraticModel structure:

  vartype = BINARY
  linear = {i: Q_ii}
  quadratic = {(i,j): Q_ij}
  offset = constant

It also writes an SPIN-form BQM using Ising h/J/offset.

This prepares the small package for D-Wave Ocean/dimod-style workflows without
executing quantum hardware.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/small_time_indexed_solver_package")
    parser.add_argument("--out-prefix", type=str, default="small_time_indexed")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    metadata_path = package_dir / "package_metadata.json"
    qubo_path = package_dir / "qubo_coefficients.csv"
    h_path = package_dir / "ising_linear_fields.csv"
    j_path = package_dir / "ising_couplers.csv"

    if not metadata_path.exists():
        raise FileNotFoundError(metadata_path)
    if not qubo_path.exists():
        raise FileNotFoundError(qubo_path)

    metadata = json.loads(metadata_path.read_text())
    num_variables = int(metadata["num_variables"])
    qubo_offset = float(metadata["constant_offset"])
    ising_offset = float(metadata["ising_offset"])

    qubo_df = pd.read_csv(qubo_path)
    linear = {}
    quadratic = {}

    for row in qubo_df.itertuples(index=False):
        i = int(row.i)
        j = int(row.j)
        q = float(row.coefficient)
        if i == j:
            linear[str(i)] = linear.get(str(i), 0.0) + q
        else:
            key = str(min(i, j)) + "," + str(max(i, j))
            quadratic[key] = quadratic.get(key, 0.0) + q

    h_fields = {}
    if h_path.exists():
        h_df = pd.read_csv(h_path)
        for row in h_df.itertuples(index=False):
            h_fields[str(int(row.i))] = float(row.h_i)

    couplers = {}
    if j_path.exists():
        j_df = pd.read_csv(j_path)
        for row in j_df.itertuples(index=False):
            i = int(row.i)
            j = int(row.j)
            key = str(min(i, j)) + "," + str(max(i, j))
            couplers[key] = couplers.get(key, 0.0) + float(row.J_ij)

    binary_bqm = {
        "format": "dimod_binary_quadratic_model_style",
        "vartype": "BINARY",
        "num_variables": num_variables,
        "variables": [str(i) for i in range(num_variables)],
        "linear": linear,
        "quadratic": quadratic,
        "offset": qubo_offset,
        "energy": "offset + sum_i linear[i] x_i + sum_{i<j} quadratic[i,j] x_i x_j",
        "source_package": str(package_dir),
        "note": "JSON uses string keys. Quadratic keys use 'i,j'.",
    }

    spin_bqm = {
        "format": "dimod_binary_quadratic_model_style",
        "vartype": "SPIN",
        "num_variables": num_variables,
        "variables": [str(i) for i in range(num_variables)],
        "linear": h_fields,
        "quadratic": couplers,
        "offset": ising_offset,
        "energy": "offset + sum_i linear[i] s_i + sum_{i<j} quadratic[i,j] s_i s_j",
        "source_package": str(package_dir),
        "note": "JSON uses string keys. Quadratic keys use 'i,j'.",
    }

    binary_json = package_dir / (args.out_prefix + "_dimod_binary_bqm.json")
    spin_json = package_dir / (args.out_prefix + "_dimod_spin_bqm.json")
    binary_linear_csv = package_dir / (args.out_prefix + "_dimod_binary_linear.csv")
    binary_quadratic_csv = package_dir / (args.out_prefix + "_dimod_binary_quadratic.csv")
    spin_linear_csv = package_dir / (args.out_prefix + "_dimod_spin_linear.csv")
    spin_quadratic_csv = package_dir / (args.out_prefix + "_dimod_spin_quadratic.csv")
    summary_json = package_dir / (args.out_prefix + "_dimod_bqm_export_summary.json")

    binary_json.write_text(json.dumps(binary_bqm, indent=2))
    spin_json.write_text(json.dumps(spin_bqm, indent=2))

    with binary_linear_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["variable", "linear_bias"])
        writer.writeheader()
        for k in sorted(linear, key=lambda x: int(x)):
            writer.writerow({"variable": k, "linear_bias": linear[k]})

    with binary_quadratic_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["u", "v", "quadratic_bias"])
        writer.writeheader()
        for key in sorted(quadratic, key=lambda x: tuple(int(v) for v in x.split(","))):
            u, v = key.split(",")
            writer.writerow({"u": u, "v": v, "quadratic_bias": quadratic[key]})

    with spin_linear_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["variable", "linear_bias"])
        writer.writeheader()
        for k in sorted(h_fields, key=lambda x: int(x)):
            writer.writerow({"variable": k, "linear_bias": h_fields[k]})

    with spin_quadratic_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["u", "v", "quadratic_bias"])
        writer.writeheader()
        for key in sorted(couplers, key=lambda x: tuple(int(v) for v in x.split(","))):
            u, v = key.split(",")
            writer.writerow({"u": u, "v": v, "quadratic_bias": couplers[key]})

    summary = {
        "experiment": "small_package_dimod_bqm_export",
        "package_dir": str(package_dir),
        "num_variables": num_variables,
        "binary_vartype": "BINARY",
        "binary_offset": qubo_offset,
        "binary_linear_terms": len(linear),
        "binary_quadratic_terms": len(quadratic),
        "spin_vartype": "SPIN",
        "spin_offset": ising_offset,
        "spin_linear_terms": len(h_fields),
        "spin_quadratic_terms": len(couplers),
        "binary_bqm_json": str(binary_json),
        "spin_bqm_json": str(spin_json),
        "binary_linear_csv": str(binary_linear_csv),
        "binary_quadratic_csv": str(binary_quadratic_csv),
        "spin_linear_csv": str(spin_linear_csv),
        "spin_quadratic_csv": str(spin_quadratic_csv),
        "note": "dimod-compatible style export. This does not require dimod and does not run D-Wave hardware.",
    }
    summary_json.write_text(json.dumps(summary, indent=2))

    print("=== dimod-compatible BQM-style export complete ===")
    print("package_dir =", package_dir)
    print("num_variables =", num_variables)
    print("binary_linear_terms =", len(linear))
    print("binary_quadratic_terms =", len(quadratic))
    print("spin_linear_terms =", len(h_fields))
    print("spin_quadratic_terms =", len(couplers))
    print("saved summary =", summary_json)

if __name__ == "__main__":
    main()
