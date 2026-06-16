"""Qiskit Optimization smoke test for the tiny QAOA-ready QUBO package.

This script attempts to load exports/tiny_qaoa_ready_package/qiskit_qubo.json
into a qiskit_optimization QuadraticProgram and validates objective energies
against the brute-force energy table.

If qiskit_optimization is not installed, the script records SKIPPED status.

This does not run QAOA, a quantum simulator, or quantum hardware.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import itertools
import json
from pathlib import Path

import pandas as pd

def manual_qubo_energy(bits, payload):
    e = float(payload["constant"])
    for var, coeff in payload["linear"].items():
        idx = int(var.replace("x", ""))
        e += float(coeff) * bits[idx]
    for key, coeff in payload["quadratic"].items():
        a, b = key.split(",")
        i = int(a.replace("x", ""))
        j = int(b.replace("x", ""))
        e += float(coeff) * bits[i] * bits[j]
    return e

def bitstring(bits):
    return "".join(str(int(b)) for b in bits)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/tiny_qaoa_ready_package")
    parser.add_argument("--out", type=str, default="results/tables/tiny_qiskit_optimization_smoke_test.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/tiny_qiskit_optimization_smoke_test_summary.json")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    qiskit_json_path = package_dir / "qiskit_qubo.json"
    brute_csv_path = package_dir / "bruteforce_energy_table.csv"
    metadata_path = package_dir / "package_metadata.json"

    payload = json.loads(qiskit_json_path.read_text())
    metadata = json.loads(metadata_path.read_text())
    brute_df = pd.read_csv(brute_csv_path)
    num_variables = int(payload["num_binary_variables"])

    out_path = Path(args.out)
    summary_path = Path(args.summary_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    if importlib.util.find_spec("qiskit_optimization") is None:
        reason = "qiskit_optimization is not installed in the current environment."
        summary = {
            "experiment": "tiny_qiskit_optimization_smoke_test",
            "status": "SKIPPED",
            "reason": reason,
            "num_variables": num_variables,
            "qiskit_qubo_json": str(qiskit_json_path),
            "note": "Install qiskit-optimization to run actual QuadraticProgram validation.",
        }
        summary_path.write_text(json.dumps(summary, indent=2))
        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["status", "reason"])
            writer.writeheader()
            writer.writerow({"status": "SKIPPED", "reason": reason})
        print("=== Qiskit Optimization smoke test skipped ===")
        print("reason =", reason)
        print("saved summary =", summary_path)
        return

    from qiskit_optimization import QuadraticProgram

    qp = QuadraticProgram("tiny_qaoa_ready_qubo")
    for var in payload["variables"]:
        qp.binary_var(name=var)

    linear = {var: float(coeff) for var, coeff in payload["linear"].items()}
    quadratic = {}
    for key, coeff in payload["quadratic"].items():
        a, b = key.split(",")
        quadratic[(a, b)] = float(coeff)
    qp.minimize(constant=float(payload["constant"]), linear=linear, quadratic=quadratic)

    rows = []
    max_abs_error_manual_vs_qiskit = 0.0
    max_abs_error_manual_vs_bruteforce_csv = 0.0

    brute_lookup = {str(row.bitstring).zfill(num_variables): float(row.energy) for row in brute_df.itertuples(index=False)}

    for bits_tuple in itertools.product([0, 1], repeat=num_variables):
        bits = list(bits_tuple)
        bstr = bitstring(bits)
        manual_e = manual_qubo_energy(bits, payload)
        qiskit_e = float(qp.objective.evaluate(bits))
        brute_e = brute_lookup[bstr]
        err_mq = abs(manual_e - qiskit_e)
        err_mb = abs(manual_e - brute_e)
        max_abs_error_manual_vs_qiskit = max(max_abs_error_manual_vs_qiskit, err_mq)
        max_abs_error_manual_vs_bruteforce_csv = max(max_abs_error_manual_vs_bruteforce_csv, err_mb)
        rows.append({
            "bitstring": bstr,
            "manual_energy": manual_e,
            "qiskit_quadratic_program_energy": qiskit_e,
            "bruteforce_csv_energy": brute_e,
            "abs_error_manual_vs_qiskit": err_mq,
            "abs_error_manual_vs_bruteforce_csv": err_mb,
        })

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best_manual = min(rows, key=lambda r: r["manual_energy"])
    best_qiskit = min(rows, key=lambda r: r["qiskit_quadratic_program_energy"])
    max_abs_error = max(max_abs_error_manual_vs_qiskit, max_abs_error_manual_vs_bruteforce_csv)

    summary = {
        "experiment": "tiny_qiskit_optimization_smoke_test",
        "status": "PASS" if max_abs_error < 1e-9 and best_manual["bitstring"] == best_qiskit["bitstring"] else "FAIL",
        "num_variables": num_variables,
        "num_assignments_enumerated": len(rows),
        "qiskit_optimization_available": True,
        "best_manual_bitstring": best_manual["bitstring"],
        "best_manual_energy": best_manual["manual_energy"],
        "best_qiskit_bitstring": best_qiskit["bitstring"],
        "best_qiskit_energy": best_qiskit["qiskit_quadratic_program_energy"],
        "known_metadata_best_bitstring": metadata["best_bitstring"],
        "known_metadata_best_energy": metadata["best_energy"],
        "max_abs_error_manual_vs_qiskit": max_abs_error_manual_vs_qiskit,
        "max_abs_error_manual_vs_bruteforce_csv": max_abs_error_manual_vs_bruteforce_csv,
        "max_abs_error": max_abs_error,
        "quadratic_program_name": qp.name,
        "num_qp_variables": qp.get_num_vars(),
        "num_qp_linear_constraints": qp.get_num_linear_constraints(),
        "num_qp_quadratic_constraints": qp.get_num_quadratic_constraints(),
        "qiskit_qubo_json": str(qiskit_json_path),
        "rows_csv": str(out_path),
        "note": "Qiskit Optimization QuadraticProgram smoke test only. No QAOA or quantum execution.",
    }
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=== tiny Qiskit Optimization smoke test complete ===")
    print("status =", summary["status"])
    print("num_variables =", num_variables)
    print("num_assignments_enumerated =", len(rows))
    print("best_manual_bitstring =", best_manual["bitstring"])
    print("best_manual_energy =", best_manual["manual_energy"])
    print("best_qiskit_bitstring =", best_qiskit["bitstring"])
    print("best_qiskit_energy =", best_qiskit["qiskit_quadratic_program_energy"])
    print("max_abs_error =", max_abs_error)
    print("saved rows =", out_path)
    print("saved summary =", summary_path)

if __name__ == "__main__":
    main()
