"""Create and validate scaled QUBO/Ising exports for the small package.

This script scales QUBO and Ising coefficients by a common positive factor so
that the maximum absolute coefficient is near 1.0. It then validates that scaled
energies preserve the same argmin and energy ordering as the unscaled model.

This is a solver-readiness step. It does not run quantum hardware, quantum
annealing, dimod, or QAOA.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

import pandas as pd

def qubo_energy(bits, coeffs, offset):
    e = offset
    for i, j, q in coeffs:
        e += q * bits[i] * bits[j]
    return e

def ising_energy(bits, h_fields, couplers, offset):
    spins = [2 * b - 1 for b in bits]
    e = offset
    for i, h in h_fields.items():
        e += h * spins[i]
    for i, j, J in couplers:
        e += J * spins[i] * spins[j]
    return e

def load_qubo(path):
    df = pd.read_csv(path)
    return [(int(r.i), int(r.j), float(r.coefficient)) for r in df.itertuples(index=False)]

def load_h(path):
    df = pd.read_csv(path)
    return {int(r.i): float(r.h_i) for r in df.itertuples(index=False)}

def load_j(path):
    df = pd.read_csv(path)
    return [(int(r.i), int(r.j), float(r.J_ij)) for r in df.itertuples(index=False)]

def bitstring(bits):
    return "".join(str(int(b)) for b in bits)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/small_time_indexed_solver_package")
    parser.add_argument("--scale-mode", type=str, default="unit_abs_max")
    parser.add_argument("--out-prefix", type=str, default="small_time_indexed_scaled")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    metadata = json.loads((package_dir / "package_metadata.json").read_text())
    num_variables = int(metadata["num_variables"])
    qubo_offset = float(metadata["constant_offset"])
    ising_offset = float(metadata["ising_offset"])

    qubo_coeffs = load_qubo(package_dir / "qubo_coefficients.csv")
    h_fields = load_h(package_dir / "ising_linear_fields.csv")
    couplers = load_j(package_dir / "ising_couplers.csv")

    coeff_abs_values = []
    coeff_abs_values.extend(abs(q) for _, _, q in qubo_coeffs)
    coeff_abs_values.extend(abs(h) for h in h_fields.values())
    coeff_abs_values.extend(abs(J) for _, _, J in couplers)
    coeff_abs_values.append(abs(qubo_offset))
    coeff_abs_values.append(abs(ising_offset))
    abs_max = max(coeff_abs_values)
    scale_factor = 1.0 / abs_max if abs_max > 0 else 1.0

    scaled_qubo_coeffs = [(i, j, q * scale_factor) for i, j, q in qubo_coeffs]
    scaled_h_fields = {i: h * scale_factor for i, h in h_fields.items()}
    scaled_couplers = [(i, j, J * scale_factor) for i, j, J in couplers]
    scaled_qubo_offset = qubo_offset * scale_factor
    scaled_ising_offset = ising_offset * scale_factor

    scaled_qubo_csv = package_dir / (args.out_prefix + "_qubo_coefficients.csv")
    scaled_ising_h_csv = package_dir / (args.out_prefix + "_ising_linear_fields.csv")
    scaled_ising_j_csv = package_dir / (args.out_prefix + "_ising_couplers.csv")
    scaling_metadata_json = package_dir / (args.out_prefix + "_scaling_metadata.json")
    validation_csv = Path("results/tables/small_package_scaled_export_validation.csv")
    validation_summary_json = Path("results/tables/small_package_scaled_export_validation_summary.json")

    with scaled_qubo_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "j", "coefficient"])
        writer.writeheader()
        for i, j, q in scaled_qubo_coeffs:
            writer.writerow({"i": i, "j": j, "coefficient": q})

    with scaled_ising_h_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "h_i"])
        writer.writeheader()
        for i in sorted(scaled_h_fields):
            writer.writerow({"i": i, "h_i": scaled_h_fields[i]})

    with scaled_ising_j_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "j", "J_ij"])
        writer.writeheader()
        for i, j, J in scaled_couplers:
            writer.writerow({"i": i, "j": j, "J_ij": J})

    rows = []
    for bits_tuple in itertools.product([0, 1], repeat=num_variables):
        bits = list(bits_tuple)
        e_qubo = qubo_energy(bits, qubo_coeffs, qubo_offset)
        e_qubo_scaled = qubo_energy(bits, scaled_qubo_coeffs, scaled_qubo_offset)
        e_ising = ising_energy(bits, h_fields, couplers, ising_offset)
        e_ising_scaled = ising_energy(bits, scaled_h_fields, scaled_couplers, scaled_ising_offset)
        rows.append({
            "bitstring": bitstring(bits),
            "unscaled_qubo_energy": e_qubo,
            "scaled_qubo_energy": e_qubo_scaled,
            "unscaled_ising_energy": e_ising,
            "scaled_ising_energy": e_ising_scaled,
            "rescaled_qubo_energy": e_qubo_scaled / scale_factor,
            "rescaled_ising_energy": e_ising_scaled / scale_factor,
            "abs_error_qubo_rescaled": abs(e_qubo - (e_qubo_scaled / scale_factor)),
            "abs_error_ising_rescaled": abs(e_ising - (e_ising_scaled / scale_factor)),
            "abs_error_scaled_qubo_vs_scaled_ising": abs(e_qubo_scaled - e_ising_scaled),
        })

    validation_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(validation_csv, index=False)

    best_unscaled = min(rows, key=lambda r: r["unscaled_qubo_energy"])
    best_scaled = min(rows, key=lambda r: r["scaled_qubo_energy"])
    best_ising_scaled = min(rows, key=lambda r: r["scaled_ising_energy"])

    max_abs_error_qubo_rescaled = max(r["abs_error_qubo_rescaled"] for r in rows)
    max_abs_error_ising_rescaled = max(r["abs_error_ising_rescaled"] for r in rows)
    max_abs_error_scaled_qubo_vs_scaled_ising = max(r["abs_error_scaled_qubo_vs_scaled_ising"] for r in rows)
    argmin_consistent = (
        best_unscaled["bitstring"] == best_scaled["bitstring"] == best_ising_scaled["bitstring"]
    )

    scaling_metadata = {
        "package": "small_time_indexed_solver_package",
        "scale_mode": args.scale_mode,
        "abs_max_before_scaling": abs_max,
        "scale_factor": scale_factor,
        "scaled_qubo_offset": scaled_qubo_offset,
        "scaled_ising_offset": scaled_ising_offset,
        "scaled_qubo_csv": str(scaled_qubo_csv),
        "scaled_ising_h_csv": str(scaled_ising_h_csv),
        "scaled_ising_j_csv": str(scaled_ising_j_csv),
        "energy_relation": "scaled_energy = unscaled_energy * scale_factor",
        "note": "Positive scaling preserves argmin and energy ordering.",
    }
    scaling_metadata_json.write_text(json.dumps(scaling_metadata, indent=2))

    summary = {
        "experiment": "small_package_scaled_export_validation",
        "num_variables": num_variables,
        "num_assignments_enumerated": len(rows),
        "scale_mode": args.scale_mode,
        "abs_max_before_scaling": abs_max,
        "scale_factor": scale_factor,
        "best_unscaled_bitstring": best_unscaled["bitstring"],
        "best_unscaled_energy": best_unscaled["unscaled_qubo_energy"],
        "best_scaled_qubo_bitstring": best_scaled["bitstring"],
        "best_scaled_qubo_energy": best_scaled["scaled_qubo_energy"],
        "best_scaled_ising_bitstring": best_ising_scaled["bitstring"],
        "best_scaled_ising_energy": best_ising_scaled["scaled_ising_energy"],
        "argmin_consistent": argmin_consistent,
        "max_abs_error_qubo_rescaled": max_abs_error_qubo_rescaled,
        "max_abs_error_ising_rescaled": max_abs_error_ising_rescaled,
        "max_abs_error_scaled_qubo_vs_scaled_ising": max_abs_error_scaled_qubo_vs_scaled_ising,
        "validation_status": "PASS" if argmin_consistent and max_abs_error_qubo_rescaled < 1e-9 and max_abs_error_ising_rescaled < 1e-9 and max_abs_error_scaled_qubo_vs_scaled_ising < 1e-9 else "FAIL",
        "scaling_metadata_json": str(scaling_metadata_json),
        "validation_csv": str(validation_csv),
        "note": "Validates scaled QUBO/Ising exports on all assignments for the small package.",
    }
    validation_summary_json.write_text(json.dumps(summary, indent=2))

    print("=== small package scaled export validation complete ===")
    print("num_variables =", num_variables)
    print("num_assignments_enumerated =", len(rows))
    print("abs_max_before_scaling =", abs_max)
    print("scale_factor =", scale_factor)
    print("best_unscaled_bitstring =", best_unscaled["bitstring"])
    print("best_scaled_qubo_bitstring =", best_scaled["bitstring"])
    print("best_scaled_ising_bitstring =", best_ising_scaled["bitstring"])
    print("argmin_consistent =", argmin_consistent)
    print("validation_status =", summary["validation_status"])
    print("saved scaling metadata =", scaling_metadata_json)
    print("saved validation summary =", validation_summary_json)

if __name__ == "__main__":
    main()
