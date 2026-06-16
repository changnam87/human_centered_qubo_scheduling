"""Qiskit classical optimizer smoke test for the tiny QAOA-ready QUBO package.

This script loads the tiny QUBO into qiskit_optimization QuadraticProgram and
tries to solve it with classical Qiskit Optimization optimizers.

Preferred solver path:
  1. CplexOptimizer if available
  2. MinimumEigenOptimizer with NumPyMinimumEigensolver if available
  3. Manual exhaustive fallback over 2^n assignments

This does not run QAOA, a quantum simulator, or quantum hardware.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import itertools
import json
from pathlib import Path

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

def build_quadratic_program(payload):
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
    return qp

def solve_manual(payload):
    n = int(payload["num_binary_variables"])
    rows = []
    for bits_tuple in itertools.product([0, 1], repeat=n):
        bits = list(bits_tuple)
        e = manual_qubo_energy(bits, payload)
        rows.append({"bitstring": bitstring(bits), "energy": e})
    best = min(rows, key=lambda r: r["energy"])
    return best, rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/tiny_qaoa_ready_package")
    parser.add_argument("--out", type=str, default="results/tables/tiny_qiskit_classical_optimizer_smoke_test.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/tiny_qiskit_classical_optimizer_smoke_test_summary.json")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    qiskit_json_path = package_dir / "qiskit_qubo.json"
    metadata_path = package_dir / "package_metadata.json"
    payload = json.loads(qiskit_json_path.read_text())
    metadata = json.loads(metadata_path.read_text())

    out_path = Path(args.out)
    summary_path = Path(args.summary_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    if importlib.util.find_spec("qiskit_optimization") is None:
        reason = "qiskit_optimization is not installed in the current environment."
        summary = {
            "experiment": "tiny_qiskit_classical_optimizer_smoke_test",
            "status": "SKIPPED",
            "reason": reason,
            "qiskit_qubo_json": str(qiskit_json_path),
            "note": "Install qiskit-optimization to run Qiskit optimizer validation.",
        }
        summary_path.write_text(json.dumps(summary, indent=2))
        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["status", "reason"])
            writer.writeheader()
            writer.writerow({"status": "SKIPPED", "reason": reason})
        print("=== tiny Qiskit classical optimizer smoke test skipped ===")
        print("reason =", reason)
        return

    qp = build_quadratic_program(payload)
    known_best_bitstring = metadata["best_bitstring"]
    known_best_energy = float(metadata["best_energy"])

    solver_name = None
    solver_status = None
    solver_bitstring = None
    solver_energy = None
    solver_message = ""

    # Try CplexOptimizer if installed and usable.
    try:
        from qiskit_optimization.algorithms import CplexOptimizer
        result = CplexOptimizer().solve(qp)
        solver_name = "CplexOptimizer"
        solver_status = str(result.status)
        solver_bits = [int(round(v)) for v in result.x]
        solver_bitstring = bitstring(solver_bits)
        solver_energy = float(result.fval)
    except Exception as exc:
        solver_message += "CplexOptimizer unavailable or failed: " + repr(exc) + " | "

    # Try MinimumEigenOptimizer with NumPyMinimumEigensolver if available.
    if solver_bitstring is None:
        try:
            from qiskit_algorithms import NumPyMinimumEigensolver
            from qiskit_optimization.algorithms import MinimumEigenOptimizer
            result = MinimumEigenOptimizer(NumPyMinimumEigensolver()).solve(qp)
            solver_name = "MinimumEigenOptimizer_NumPyMinimumEigensolver"
            solver_status = str(result.status)
            solver_bits = [int(round(v)) for v in result.x]
            solver_bitstring = bitstring(solver_bits)
            solver_energy = float(result.fval)
        except Exception as exc:
            solver_message += "MinimumEigenOptimizer unavailable or failed: " + repr(exc) + " | "

    # Always compute manual exhaustive reference.
    manual_best, manual_rows = solve_manual(payload)

    # If Qiskit solvers unavailable, use manual fallback but mark as FALLBACK_PASS if correct.
    if solver_bitstring is None:
        solver_name = "manual_exhaustive_fallback"
        solver_status = "FALLBACK"
        solver_bitstring = manual_best["bitstring"]
        solver_energy = manual_best["energy"]

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["bitstring", "energy"])
        writer.writeheader()
        writer.writerows(manual_rows)

    abs_error_solver_vs_known = abs(float(solver_energy) - known_best_energy)
    abs_error_manual_vs_known = abs(float(manual_best["energy"]) - known_best_energy)
    solver_matches_known = solver_bitstring == known_best_bitstring and abs_error_solver_vs_known < 1e-9
    manual_matches_known = manual_best["bitstring"] == known_best_bitstring and abs_error_manual_vs_known < 1e-9

    if solver_name == "manual_exhaustive_fallback":
        status = "FALLBACK_PASS" if manual_matches_known else "FAIL"
    else:
        status = "PASS" if solver_matches_known and manual_matches_known else "FAIL"

    summary = {
        "experiment": "tiny_qiskit_classical_optimizer_smoke_test",
        "status": status,
        "solver_name": solver_name,
        "solver_status": solver_status,
        "solver_message": solver_message.strip(),
        "num_variables": int(payload["num_binary_variables"]),
        "num_assignments_enumerated_manual_reference": len(manual_rows),
        "known_best_bitstring": known_best_bitstring,
        "known_best_energy": known_best_energy,
        "solver_best_bitstring": solver_bitstring,
        "solver_best_energy": solver_energy,
        "manual_best_bitstring": manual_best["bitstring"],
        "manual_best_energy": manual_best["energy"],
        "solver_matches_known": solver_matches_known,
        "manual_matches_known": manual_matches_known,
        "abs_error_solver_vs_known": abs_error_solver_vs_known,
        "abs_error_manual_vs_known": abs_error_manual_vs_known,
        "quadratic_program_name": qp.name,
        "num_qp_variables": qp.get_num_vars(),
        "num_qp_linear_constraints": qp.get_num_linear_constraints(),
        "num_qp_quadratic_constraints": qp.get_num_quadratic_constraints(),
        "qiskit_qubo_json": str(qiskit_json_path),
        "manual_reference_csv": str(out_path),
        "note": "Classical Qiskit Optimization smoke test. No QAOA, simulator, or hardware execution.",
    }
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=== tiny Qiskit classical optimizer smoke test complete ===")
    print("status =", status)
    print("solver_name =", solver_name)
    print("known_best_bitstring =", known_best_bitstring)
    print("solver_best_bitstring =", solver_bitstring)
    print("known_best_energy =", known_best_energy)
    print("solver_best_energy =", solver_energy)
    print("saved summary =", summary_path)

if __name__ == "__main__":
    main()
