"""Validate dimod-style BQM export energy consistency for the small package.

This script reads the dimod-style BINARY and SPIN BQM JSON files generated for
the small external-solver-ready package and validates their energies against
the original QUBO/Ising package files.

No dimod installation is required.
No quantum hardware, quantum annealing, or QAOA is executed.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

import pandas as pd

def load_qubo_coeffs(path: Path):
    df = pd.read_csv(path)
    coeffs = []
    for row in df.itertuples(index=False):
        coeffs.append((int(row.i), int(row.j), float(row.coefficient)))
    return coeffs

def load_ising_fields(path: Path):
    df = pd.read_csv(path)
    h = {}
    for row in df.itertuples(index=False):
        h[int(row.i)] = float(row.h_i)
    return h

def load_ising_couplers(path: Path):
    df = pd.read_csv(path)
    couplers = []
    for row in df.itertuples(index=False):
        couplers.append((int(row.i), int(row.j), float(row.J_ij)))
    return couplers

def original_qubo_energy(bits, coeffs, offset):
    e = offset
    for i, j, q in coeffs:
        e += q * bits[i] * bits[j]
    return e

def original_ising_energy(bits, h, couplers, offset):
    spins = [2 * b - 1 for b in bits]
    e = offset
    for i, bias in h.items():
        e += bias * spins[i]
    for i, j, J in couplers:
        e += J * spins[i] * spins[j]
    return e

def dimod_binary_energy(bits, bqm):
    e = float(bqm["offset"])
    linear = bqm["linear"]
    quadratic = bqm["quadratic"]
    for key, bias in linear.items():
        i = int(key)
        e += float(bias) * bits[i]
    for key, bias in quadratic.items():
        u, v = [int(x) for x in key.split(",")]
        e += float(bias) * bits[u] * bits[v]
    return e

def dimod_spin_energy(bits, bqm):
    spins = [2 * b - 1 for b in bits]
    e = float(bqm["offset"])
    linear = bqm["linear"]
    quadratic = bqm["quadratic"]
    for key, bias in linear.items():
        i = int(key)
        e += float(bias) * spins[i]
    for key, bias in quadratic.items():
        u, v = [int(x) for x in key.split(",")]
        e += float(bias) * spins[u] * spins[v]
    return e

def bitstring(bits):
    return "".join(str(b) for b in bits)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/small_time_indexed_solver_package")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--num-random-samples", type=int, default=20)
    parser.add_argument("--out", type=str, default="results/tables/small_package_dimod_bqm_energy_validation.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/small_package_dimod_bqm_energy_validation_summary.json")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    metadata = json.loads((package_dir / "package_metadata.json").read_text())
    num_variables = int(metadata["num_variables"])
    qubo_offset = float(metadata["constant_offset"])
    ising_offset = float(metadata["ising_offset"])

    qubo_coeffs = load_qubo_coeffs(package_dir / "qubo_coefficients.csv")
    h = load_ising_fields(package_dir / "ising_linear_fields.csv")
    couplers = load_ising_couplers(package_dir / "ising_couplers.csv")

    binary_bqm = json.loads((package_dir / "small_time_indexed_dimod_binary_bqm.json").read_text())
    spin_bqm = json.loads((package_dir / "small_time_indexed_dimod_spin_bqm.json").read_text())

    rng = random.Random(args.seed)
    samples = []
    samples.append(("all_zero", [0 for _ in range(num_variables)]))
    samples.append(("all_one", [1 for _ in range(num_variables)]))
    samples.append(("bruteforce_best", [int(c) for c in "100000000000100"]))
    for k in range(args.num_random_samples):
        samples.append(("random_" + str(k), [rng.randint(0, 1) for _ in range(num_variables)]))

    rows = []
    for name, bits in samples:
        e_qubo = original_qubo_energy(bits, qubo_coeffs, qubo_offset)
        e_ising = original_ising_energy(bits, h, couplers, ising_offset)
        e_binary_bqm = dimod_binary_energy(bits, binary_bqm)
        e_spin_bqm = dimod_spin_energy(bits, spin_bqm)
        rows.append({
            "sample_name": name,
            "bitstring": bitstring(bits),
            "original_qubo_energy": e_qubo,
            "original_ising_energy": e_ising,
            "dimod_binary_bqm_energy": e_binary_bqm,
            "dimod_spin_bqm_energy": e_spin_bqm,
            "abs_error_qubo_vs_binary_bqm": abs(e_qubo - e_binary_bqm),
            "abs_error_ising_vs_spin_bqm": abs(e_ising - e_spin_bqm),
            "abs_error_binary_vs_spin_bqm": abs(e_binary_bqm - e_spin_bqm),
            "abs_error_qubo_vs_ising": abs(e_qubo - e_ising),
        })

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    max_abs_error = max(
        max(
            row["abs_error_qubo_vs_binary_bqm"],
            row["abs_error_ising_vs_spin_bqm"],
            row["abs_error_binary_vs_spin_bqm"],
            row["abs_error_qubo_vs_ising"],
        )
        for row in rows
    )
    mean_abs_error_binary_vs_spin = sum(row["abs_error_binary_vs_spin_bqm"] for row in rows) / len(rows)

    summary = {
        "experiment": "small_package_dimod_bqm_energy_validation",
        "package_dir": str(package_dir),
        "num_variables": num_variables,
        "num_samples": len(rows),
        "max_abs_error": max_abs_error,
        "mean_abs_error_binary_vs_spin_bqm": mean_abs_error_binary_vs_spin,
        "validation_status": "PASS" if max_abs_error < 1e-9 else "FAIL",
        "binary_bqm_json": str(package_dir / "small_time_indexed_dimod_binary_bqm.json"),
        "spin_bqm_json": str(package_dir / "small_time_indexed_dimod_spin_bqm.json"),
        "note": "Validates dimod-style BQM JSON energy consistency without requiring dimod.",
    }

    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=== dimod-style BQM energy validation complete ===")
    print("num_variables =", num_variables)
    print("num_samples =", len(rows))
    print("max_abs_error =", max_abs_error)
    print("validation_status =", summary["validation_status"])
    print("saved rows =", out_path)
    print("saved summary =", summary_path)

if __name__ == "__main__":
    main()
