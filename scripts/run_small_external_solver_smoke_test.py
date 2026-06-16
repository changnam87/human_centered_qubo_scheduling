"""Minimal external-solver smoke test for the small QUBO/Ising package.

This script reads the compact exported QUBO package and solves it by brute force.
It verifies that the exported package can be consumed as an external solver input.

This is only for the small package, not for the full sample_4x4 QUBO.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

import pandas as pd

def qubo_energy(bits, coeffs, constant):
    energy = constant
    for i, j, q in coeffs:
        energy += q * bits[i] * bits[j]
    return energy

def ising_energy(bits, h_fields, couplers, offset):
    energy = offset
    spins = [2 * b - 1 for b in bits]
    for i, h in h_fields.items():
        energy += h * spins[i]
    for i, j, J in couplers:
        energy += J * spins[i] * spins[j]
    return energy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/small_time_indexed_solver_package")
    parser.add_argument("--out", type=str, default="results/tables/small_external_solver_smoke_test_result.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/small_external_solver_smoke_test_summary.json")
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
    constant = float(metadata["constant_offset"])
    ising_offset = float(metadata["ising_offset"])

    if num_variables > 24:
        raise ValueError("Brute-force smoke test is only intended for small packages. num_variables=" + str(num_variables))

    qubo_df = pd.read_csv(qubo_path)
    coeffs = []
    for row in qubo_df.itertuples(index=False):
        coeffs.append((int(row.i), int(row.j), float(row.coefficient)))

    h_fields = {}
    if h_path.exists():
        h_df = pd.read_csv(h_path)
        for row in h_df.itertuples(index=False):
            h_fields[int(row.i)] = float(row.h_i)

    couplers = []
    if j_path.exists():
        j_df = pd.read_csv(j_path)
        for row in j_df.itertuples(index=False):
            couplers.append((int(row.i), int(row.j), float(row.J_ij)))

    rows = []
    best_bits = None
    best_qubo_energy = None
    best_ising_energy = None
    max_abs_error = 0.0

    for bits_tuple in itertools.product([0, 1], repeat=num_variables):
        bits = list(bits_tuple)
        e_qubo = qubo_energy(bits, coeffs, constant)
        e_ising = ising_energy(bits, h_fields, couplers, ising_offset)
        abs_error = abs(e_qubo - e_ising)
        max_abs_error = max(max_abs_error, abs_error)

        if best_qubo_energy is None or e_qubo < best_qubo_energy:
            best_qubo_energy = e_qubo
            best_ising_energy = e_ising
            best_bits = bits

        rows.append({
            "bitstring": "".join(str(b) for b in bits),
            "qubo_energy": e_qubo,
            "ising_energy": e_ising,
            "abs_error": abs_error,
        })

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "small_external_solver_smoke_test",
        "package_dir": str(package_dir),
        "num_variables": num_variables,
        "num_assignments_enumerated": len(rows),
        "best_bitstring": "".join(str(b) for b in best_bits),
        "best_qubo_energy": best_qubo_energy,
        "best_ising_energy": best_ising_energy,
        "max_abs_error_qubo_vs_ising": max_abs_error,
        "validation_status": "PASS" if max_abs_error < 1e-9 else "FAIL",
        "note": "Brute-force smoke test for small external-solver-ready package only.",
    }

    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=== small external solver smoke test complete ===")
    print("num_variables =", num_variables)
    print("num_assignments_enumerated =", len(rows))
    print("best_bitstring =", summary["best_bitstring"])
    print("best_qubo_energy =", best_qubo_energy)
    print("best_ising_energy =", best_ising_energy)
    print("max_abs_error_qubo_vs_ising =", max_abs_error)
    print("validation_status =", summary["validation_status"])
    print("saved result =", out_path)
    print("saved summary =", summary_path)

if __name__ == "__main__":
    main()
