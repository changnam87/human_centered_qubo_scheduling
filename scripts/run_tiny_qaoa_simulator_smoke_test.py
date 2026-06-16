"""Tiny QAOA simulator smoke test for the tiny QAOA-ready QUBO package.

This script attempts to solve the tiny 6-variable QUBO using Qiskit Algorithms QAOA
through Qiskit Optimization MinimumEigenOptimizer.

This is a toy simulator/software experiment only.
It does not run quantum hardware and does not imply quantum advantage.
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

def make_sampler(seed: int):
    # Qiskit primitive names differ across versions.
    try:
        from qiskit.primitives import StatevectorSampler
        try:
            return StatevectorSampler(seed=seed), "StatevectorSampler"
        except TypeError:
            return StatevectorSampler(), "StatevectorSampler"
    except Exception:
        pass

    try:
        from qiskit.primitives import Sampler
        try:
            return Sampler(options={"seed": seed}), "Sampler"
        except TypeError:
            return Sampler(), "Sampler"
    except Exception as exc:
        raise RuntimeError("No compatible Qiskit sampler primitive found: " + repr(exc))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/tiny_qaoa_ready_package")
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--maxiter", type=int, default=100)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--out", type=str, default="results/tables/tiny_qaoa_simulator_smoke_test.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/tiny_qaoa_simulator_smoke_test_summary.json")
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

    required = ["qiskit", "qiskit_optimization", "qiskit_algorithms"]
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        reason = "Missing required packages: " + ", ".join(missing)
        summary = {
            "experiment": "tiny_qaoa_simulator_smoke_test",
            "status": "SKIPPED",
            "reason": reason,
            "num_variables": int(payload["num_binary_variables"]),
            "qiskit_qubo_json": str(qiskit_json_path),
            "note": "Install missing Qiskit packages to run QAOA simulator smoke test.",
        }
        summary_path.write_text(json.dumps(summary, indent=2))
        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["status", "reason"])
            writer.writeheader()
            writer.writerow({"status": "SKIPPED", "reason": reason})
        print("=== tiny QAOA simulator smoke test skipped ===")
        print("reason =", reason)
        return

    manual_best, manual_rows = solve_manual(payload)
    qp = build_quadratic_program(payload)

    qaoa_bitstring = None
    qaoa_energy = None
    qaoa_status = None
    qaoa_message = ""
    sampler_name = None

    try:
        from qiskit_algorithms import QAOA
        from qiskit_algorithms.optimizers import COBYLA
        from qiskit_optimization.algorithms import MinimumEigenOptimizer

        sampler, sampler_name = make_sampler(args.seed)
        optimizer = COBYLA(maxiter=args.maxiter)
        qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=args.reps)
        result = MinimumEigenOptimizer(qaoa).solve(qp)
        qaoa_status = str(result.status)
        qaoa_bits = [int(round(v)) for v in result.x]
        qaoa_bitstring = bitstring(qaoa_bits)
        qaoa_energy = float(result.fval)
    except Exception as exc:
        qaoa_message = repr(exc)

    rows = []
    for row in manual_rows:
        rows.append({
            "bitstring": row["bitstring"],
            "manual_energy": row["energy"],
            "is_manual_best": row["bitstring"] == manual_best["bitstring"],
            "is_qaoa_solution": row["bitstring"] == qaoa_bitstring if qaoa_bitstring is not None else False,
        })

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    known_best_bitstring = metadata["best_bitstring"]
    known_best_energy = float(metadata["best_energy"])
    manual_matches_known = manual_best["bitstring"] == known_best_bitstring and abs(manual_best["energy"] - known_best_energy) < 1e-9

    if qaoa_bitstring is None:
        status = "SKIPPED"
        qaoa_matches_known = False
        gap_to_known = None
    else:
        gap_to_known = qaoa_energy - known_best_energy
        qaoa_matches_known = qaoa_bitstring == known_best_bitstring and abs(gap_to_known) < 1e-6
        status = "PASS" if qaoa_matches_known and manual_matches_known else "PARTIAL_PASS"

    summary = {
        "experiment": "tiny_qaoa_simulator_smoke_test",
        "status": status,
        "num_variables": int(payload["num_binary_variables"]),
        "reps": args.reps,
        "maxiter": args.maxiter,
        "seed": args.seed,
        "sampler_name": sampler_name,
        "qaoa_status": qaoa_status,
        "qaoa_message": qaoa_message,
        "known_best_bitstring": known_best_bitstring,
        "known_best_energy": known_best_energy,
        "manual_best_bitstring": manual_best["bitstring"],
        "manual_best_energy": manual_best["energy"],
        "manual_matches_known": manual_matches_known,
        "qaoa_bitstring": qaoa_bitstring,
        "qaoa_energy": qaoa_energy,
        "qaoa_gap_to_known": gap_to_known,
        "qaoa_matches_known": qaoa_matches_known,
        "quadratic_program_name": qp.name,
        "num_qp_variables": qp.get_num_vars(),
        "qiskit_qubo_json": str(qiskit_json_path),
        "rows_csv": str(out_path),
        "note": "Tiny QAOA simulator/software smoke test only. No quantum hardware or quantum advantage claim.",
    }
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=== tiny QAOA simulator smoke test complete ===")
    print("status =", status)
    print("sampler_name =", sampler_name)
    print("known_best_bitstring =", known_best_bitstring)
    print("known_best_energy =", known_best_energy)
    print("qaoa_bitstring =", qaoa_bitstring)
    print("qaoa_energy =", qaoa_energy)
    print("qaoa_gap_to_known =", gap_to_known)
    print("qaoa_message =", qaoa_message)
    print("saved summary =", summary_path)

if __name__ == "__main__":
    main()
