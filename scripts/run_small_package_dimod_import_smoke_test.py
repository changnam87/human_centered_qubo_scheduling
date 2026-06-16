"""dimod import smoke test for the small external solver package.

This script attempts to import dimod and build BinaryQuadraticModel objects
from the small package dimod-style BQM JSON exports.

If dimod is not installed, the script exits gracefully with SKIPPED status.

This does not run D-Wave hardware, quantum annealing, or QAOA.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import random
from pathlib import Path

def bitstring_to_binary_sample(bitstring: str):
    return {str(i): int(bit) for i, bit in enumerate(bitstring)}

def bitstring_to_spin_sample(bitstring: str):
    return {str(i): 2 * int(bit) - 1 for i, bit in enumerate(bitstring)}

def manual_binary_energy(bitstring: str, bqm_json: dict) -> float:
    bits = [int(c) for c in bitstring]
    e = float(bqm_json["offset"])
    for k, bias in bqm_json["linear"].items():
        e += float(bias) * bits[int(k)]
    for key, bias in bqm_json["quadratic"].items():
        i, j = [int(x) for x in key.split(",")]
        e += float(bias) * bits[i] * bits[j]
    return e

def manual_spin_energy(bitstring: str, bqm_json: dict) -> float:
    spins = [2 * int(c) - 1 for c in bitstring]
    e = float(bqm_json["offset"])
    for k, bias in bqm_json["linear"].items():
        e += float(bias) * spins[int(k)]
    for key, bias in bqm_json["quadratic"].items():
        i, j = [int(x) for x in key.split(",")]
        e += float(bias) * spins[i] * spins[j]
    return e

def build_dimod_bqm(dimod, bqm_json: dict):
    linear = dict(bqm_json["linear"])
    quadratic = {}
    for key, bias in bqm_json["quadratic"].items():
        i, j = key.split(",")
        quadratic[(i, j)] = float(bias)
    offset = float(bqm_json["offset"])
    vartype = bqm_json["vartype"]
    return dimod.BinaryQuadraticModel(linear, quadratic, offset, vartype)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=str, default="exports/small_time_indexed_solver_package")
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--num-random-samples", type=int, default=20)
    parser.add_argument("--out", type=str, default="results/tables/small_package_dimod_import_smoke_test.csv")
    parser.add_argument("--summary-out", type=str, default="results/tables/small_package_dimod_import_smoke_test_summary.json")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    binary_json_path = package_dir / "small_time_indexed_dimod_binary_bqm.json"
    spin_json_path = package_dir / "small_time_indexed_dimod_spin_bqm.json"
    metadata_path = package_dir / "package_metadata.json"

    binary_json = json.loads(binary_json_path.read_text())
    spin_json = json.loads(spin_json_path.read_text())
    metadata = json.loads(metadata_path.read_text())
    num_variables = int(metadata["num_variables"])

    summary_path = Path(args.summary_out)
    out_path = Path(args.out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if importlib.util.find_spec("dimod") is None:
        summary = {
            "experiment": "small_package_dimod_import_smoke_test",
            "status": "SKIPPED",
            "reason": "dimod is not installed in the current environment.",
            "num_variables": num_variables,
            "binary_bqm_json": str(binary_json_path),
            "spin_bqm_json": str(spin_json_path),
            "note": "Install dimod to run actual BinaryQuadraticModel import validation.",
        }
        summary_path.write_text(json.dumps(summary, indent=2))
        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["status", "reason"])
            writer.writeheader()
            writer.writerow({"status": "SKIPPED", "reason": summary["reason"]})
        print("=== dimod import smoke test skipped ===")
        print("reason =", summary["reason"])
        print("saved summary =", summary_path)
        return

    import dimod

    binary_bqm = build_dimod_bqm(dimod, binary_json)
    spin_bqm = build_dimod_bqm(dimod, spin_json)

    rng = random.Random(args.seed)
    samples = []
    samples.append(("all_zero", "0" * num_variables))
    samples.append(("all_one", "1" * num_variables))
    samples.append(("known_best", "100000000000100"))
    for k in range(args.num_random_samples):
        bits = "".join(str(rng.randint(0, 1)) for _ in range(num_variables))
        samples.append(("random_" + str(k), bits))

    rows = []
    for name, bitstring in samples:
        manual_binary = manual_binary_energy(bitstring, binary_json)
        manual_spin = manual_spin_energy(bitstring, spin_json)
        dimod_binary = binary_bqm.energy(bitstring_to_binary_sample(bitstring))
        dimod_spin = spin_bqm.energy(bitstring_to_spin_sample(bitstring))
        rows.append({
            "sample_name": name,
            "bitstring": bitstring,
            "manual_binary_energy": manual_binary,
            "dimod_binary_energy": dimod_binary,
            "manual_spin_energy": manual_spin,
            "dimod_spin_energy": dimod_spin,
            "abs_error_manual_vs_dimod_binary": abs(manual_binary - dimod_binary),
            "abs_error_manual_vs_dimod_spin": abs(manual_spin - dimod_spin),
            "abs_error_dimod_binary_vs_dimod_spin": abs(dimod_binary - dimod_spin),
        })

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    max_abs_error = max(
        max(
            row["abs_error_manual_vs_dimod_binary"],
            row["abs_error_manual_vs_dimod_spin"],
            row["abs_error_dimod_binary_vs_dimod_spin"],
        )
        for row in rows
    )

    summary = {
        "experiment": "small_package_dimod_import_smoke_test",
        "status": "PASS" if max_abs_error < 1e-9 else "FAIL",
        "dimod_version": getattr(dimod, "__version__", "unknown"),
        "num_variables": num_variables,
        "num_samples": len(rows),
        "binary_num_variables": len(binary_bqm.variables),
        "spin_num_variables": len(spin_bqm.variables),
        "binary_num_interactions": len(binary_bqm.quadratic),
        "spin_num_interactions": len(spin_bqm.quadratic),
        "max_abs_error": max_abs_error,
        "binary_bqm_json": str(binary_json_path),
        "spin_bqm_json": str(spin_json_path),
        "rows_csv": str(out_path),
        "note": "Actual dimod BinaryQuadraticModel import smoke test. No hardware execution.",
    }
    summary_path.write_text(json.dumps(summary, indent=2))

    print("=== dimod import smoke test complete ===")
    print("status =", summary["status"])
    print("dimod_version =", summary["dimod_version"])
    print("num_samples =", len(rows))
    print("max_abs_error =", max_abs_error)
    print("saved rows =", out_path)
    print("saved summary =", summary_path)

if __name__ == "__main__":
    main()
