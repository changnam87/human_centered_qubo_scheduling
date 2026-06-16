"""Create a small external-solver-ready QUBO/Ising package.

This script packages the existing small time-indexed QUBO into a compact
external-solver-ready folder. It creates:

  - raw QUBO coefficients
  - scaled QUBO coefficients
  - Ising linear fields
  - Ising couplers
  - package metadata
  - QUBO/Ising energy validation
  - package README

This is intended for small external solver tests, not for the full sample_4x4 model.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
from pathlib import Path

import pandas as pd

def read_json_if_exists(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}

def detect_columns(df: pd.DataFrame):
    cols = set(df.columns)
    if {"i", "j", "coefficient"}.issubset(cols):
        return "i", "j", "coefficient"
    if {"row", "col", "coefficient"}.issubset(cols):
        return "row", "col", "coefficient"
    if {"var_i", "var_j", "coefficient"}.issubset(cols):
        return "var_i", "var_j", "coefficient"
    if {"i", "j", "value"}.issubset(cols):
        return "i", "j", "value"
    raise ValueError("Could not detect QUBO coefficient columns. Found columns: " + str(list(df.columns)))

def qubo_energy(selected: set[int], coeffs, constant: float) -> float:
    energy = constant
    for i, j, q in coeffs:
        if i in selected and j in selected:
            energy += q
    return energy

def ising_energy(selected: set[int], h_fields: dict[int, float], couplers, offset: float) -> float:
    energy = offset
    for i, h in h_fields.items():
        s_i = 1.0 if i in selected else -1.0
        energy += h * s_i
    for i, j, J in couplers:
        s_i = 1.0 if i in selected else -1.0
        s_j = 1.0 if j in selected else -1.0
        energy += J * s_i * s_j
    return energy

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qubo-csv", type=str, default="results/tables/small_time_indexed_qubo_coefficients.csv")
    parser.add_argument("--summary-json", type=str, default="results/tables/small_time_indexed_qubo_summary.json")
    parser.add_argument("--out-dir", type=str, default="exports/small_time_indexed_solver_package")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--num-random-samples", type=int, default=10)
    args = parser.parse_args()

    qubo_csv = Path(args.qubo_csv)
    summary_json = Path(args.summary_json)
    out_dir = Path(args.out_dir)

    if not qubo_csv.exists():
        raise FileNotFoundError("QUBO coefficient CSV not found: " + str(qubo_csv))

    out_dir.mkdir(parents=True, exist_ok=True)

    summary = read_json_if_exists(summary_json)
    df = pd.read_csv(qubo_csv)
    i_col, j_col, q_col = detect_columns(df)

    coeffs = []
    for row in df.itertuples(index=False):
        i = int(getattr(row, i_col))
        j = int(getattr(row, j_col))
        q = float(getattr(row, q_col))
        if i <= j:
            coeffs.append((i, j, q))
        else:
            coeffs.append((j, i, q))

    coeffs.sort(key=lambda item: (item[0], item[1]))
    max_index = max(max(i, j) for i, j, q in coeffs)
    num_variables = int(summary.get("num_variables", max_index + 1))
    constant = float(summary.get("constant", summary.get("constant_offset", 0.0)))

    q_values = [q for _, _, q in coeffs]
    q_abs_max = max(abs(q) for q in q_values) if q_values else 0.0
    scale_to_unit_abs_max = 1.0 / q_abs_max if q_abs_max > 0 else 1.0

    raw_qubo_out = out_dir / "qubo_coefficients.csv"
    scaled_qubo_out = out_dir / "qubo_coefficients_scaled_unit_abs.csv"
    ising_h_out = out_dir / "ising_linear_fields.csv"
    ising_j_out = out_dir / "ising_couplers.csv"
    validation_out = out_dir / "energy_validation.csv"
    validation_summary_out = out_dir / "energy_validation_summary.json"
    metadata_out = out_dir / "package_metadata.json"
    readme_out = out_dir / "README.md"

    with raw_qubo_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "j", "coefficient"])
        writer.writeheader()
        for i, j, q in coeffs:
            writer.writerow({"i": i, "j": j, "coefficient": q})

    with scaled_qubo_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "j", "coefficient"])
        writer.writeheader()
        for i, j, q in coeffs:
            writer.writerow({"i": i, "j": j, "coefficient": q * scale_to_unit_abs_max})

    h_fields = {i: 0.0 for i in range(num_variables)}
    couplers = []
    ising_offset = constant

    for i, j, q in coeffs:
        if i == j:
            ising_offset += q / 2.0
            h_fields[i] += q / 2.0
        else:
            J = q / 4.0
            ising_offset += q / 4.0
            h_fields[i] += q / 4.0
            h_fields[j] += q / 4.0
            couplers.append((i, j, J))

    with ising_h_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "h_i"])
        writer.writeheader()
        for i in range(num_variables):
            if abs(h_fields[i]) > 1e-12:
                writer.writerow({"i": i, "h_i": h_fields[i]})

    with ising_j_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["i", "j", "J_ij"])
        writer.writeheader()
        for i, j, J in couplers:
            writer.writerow({"i": i, "j": j, "J_ij": J})

    rng = random.Random(args.seed)
    samples = []
    samples.append(("all_zero", set()))
    samples.append(("all_one", set(range(num_variables))))
    for k in range(args.num_random_samples):
        selected = set(i for i in range(num_variables) if rng.random() < 0.5)
        samples.append(("random_" + str(k), selected))

    validation_rows = []
    for name, selected in samples:
        e_qubo = qubo_energy(selected, coeffs, constant)
        e_ising = ising_energy(selected, h_fields, couplers, ising_offset)
        validation_rows.append({
            "sample_name": name,
            "num_selected_variables": len(selected),
            "qubo_energy": e_qubo,
            "ising_energy": e_ising,
            "abs_error": abs(e_qubo - e_ising),
        })

    with validation_out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(validation_rows[0].keys()))
        writer.writeheader()
        writer.writerows(validation_rows)

    max_abs_error = max(row["abs_error"] for row in validation_rows)
    mean_abs_error = sum(row["abs_error"] for row in validation_rows) / len(validation_rows)

    metadata = {
        "package": "small_time_indexed_solver_package",
        "source_qubo_csv": str(qubo_csv),
        "source_summary_json": str(summary_json),
        "num_variables": num_variables,
        "constant_offset": constant,
        "num_qubo_terms": len(coeffs),
        "num_linear_terms": sum(1 for i, j, q in coeffs if i == j),
        "num_quadratic_terms": sum(1 for i, j, q in coeffs if i != j),
        "qubo_coefficient_min": min(q_values),
        "qubo_coefficient_max": max(q_values),
        "qubo_coefficient_abs_max": q_abs_max,
        "scale_to_unit_abs_max": scale_to_unit_abs_max,
        "ising_offset": ising_offset,
        "num_ising_linear_fields": sum(1 for v in h_fields.values() if abs(v) > 1e-12),
        "num_ising_couplers": len(couplers),
        "energy_validation_max_abs_error": max_abs_error,
        "energy_validation_mean_abs_error": mean_abs_error,
        "energy_validation_status": "PASS" if max_abs_error < 1e-9 else "FAIL",
        "energy_convention": {
            "qubo": "E_QUBO(x) = constant + sum_{i<=j} Q_ij x_i x_j",
            "ising": "E_Ising(s) = offset + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j",
            "mapping": "s_i = 2*x_i - 1",
        },
        "files": {
            "raw_qubo": "qubo_coefficients.csv",
            "scaled_qubo": "qubo_coefficients_scaled_unit_abs.csv",
            "ising_linear_fields": "ising_linear_fields.csv",
            "ising_couplers": "ising_couplers.csv",
            "energy_validation": "energy_validation.csv",
            "energy_validation_summary": "energy_validation_summary.json",
        },
        "note": "Small package for external solver tests; not the full sample_4x4 QUBO.",
    }

    metadata_out.write_text(json.dumps(metadata, indent=2))
    validation_summary_out.write_text(json.dumps({
        "num_samples": len(validation_rows),
        "max_abs_error": max_abs_error,
        "mean_abs_error": mean_abs_error,
        "validation_status": metadata["energy_validation_status"],
    }, indent=2))

    readme_lines = [
        "# Small Time-Indexed Solver Package",
        "",
        "This folder contains a compact QUBO/Ising package for external solver tests.",
        "",
        "This package is intentionally small. It is not the full sample_4x4 QUBO.",
        "",
        "## Files",
        "",
        "- qubo_coefficients.csv: raw upper-triangular QUBO coefficients.",
        "- qubo_coefficients_scaled_unit_abs.csv: QUBO coefficients scaled by abs max.",
        "- ising_linear_fields.csv: Ising h_i fields.",
        "- ising_couplers.csv: Ising J_ij couplers.",
        "- package_metadata.json: package metadata and coefficient ranges.",
        "- energy_validation.csv: sampled QUBO/Ising energy comparison.",
        "- energy_validation_summary.json: validation summary.",
        "",
        "## Energy conventions",
        "",
        "QUBO: E(x) = constant + sum_{i<=j} Q_ij x_i x_j",
        "",
        "Ising: E(s) = offset + sum_i h_i s_i + sum_{i<j} J_ij s_i s_j",
        "",
        "Mapping: s_i = 2*x_i - 1.",
        "",
        "## Validation",
        "",
        "QUBO and Ising energies are validated on sampled assignments.",
        "",
        "Validation status: " + metadata["energy_validation_status"],
        "Max abs error: " + str(max_abs_error),
    ]
    readme_out.write_text("\\n".join(readme_lines) + "\\n")

    print("=== small external-solver-ready package complete ===")
    print("out_dir = " + str(out_dir))
    print("num_variables = " + str(num_variables))
    print("num_qubo_terms = " + str(len(coeffs)))
    print("scale_to_unit_abs_max = " + str(scale_to_unit_abs_max))
    print("ising_offset = " + str(ising_offset))
    print("energy_validation_status = " + metadata["energy_validation_status"])
    print("max_abs_error = " + str(max_abs_error))

if __name__ == "__main__":
    main()
