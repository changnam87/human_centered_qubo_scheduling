"""Parameter sensitivity for the small external package simulated annealing solver.

This script repeatedly calls the minimal SA solver with different settings and
summarizes success rate against the known brute-force optimum.

Known optimum:
    energy = 5.30
    bitstring = 100000000000100
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

BRUTE_FORCE_OPTIMUM = 5.30

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    out_dir = Path("results/tables/small_external_package_sa_sensitivity")
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.quick:
        grid = [
            {"restarts": 100, "iterations": 2000, "initial_temperature": 10.0, "final_temperature": 0.001, "seed": 123},
            {"restarts": 100, "iterations": 5000, "initial_temperature": 10.0, "final_temperature": 0.001, "seed": 123},
            {"restarts": 100, "iterations": 5000, "initial_temperature": 5.0, "final_temperature": 0.0001, "seed": 456},
        ]
    else:
        grid = []
        for restarts in [100, 200]:
            for iterations in [2000, 5000, 10000]:
                for initial_temperature in [2.0, 5.0, 10.0, 20.0]:
                    for final_temperature in [0.0001, 0.001, 0.01]:
                        for seed in [123, 456, 789]:
                            grid.append({
                                "restarts": restarts,
                                "iterations": iterations,
                                "initial_temperature": initial_temperature,
                                "final_temperature": final_temperature,
                                "seed": seed,
                            })

    rows = []

    for run_id, params in enumerate(grid):
        tag = (
            "run" + str(run_id).zfill(3)
            + "_r" + str(params["restarts"])
            + "_it" + str(params["iterations"])
            + "_t" + str(params["initial_temperature"])
            + "_tf" + str(params["final_temperature"])
            + "_s" + str(params["seed"])
        )

        runs_out = out_dir / (tag + "_runs.csv")
        summary_out = out_dir / (tag + "_summary.json")

        cmd = [
            sys.executable,
            "scripts/run_small_external_package_sa_solver.py",
            "--restarts", str(params["restarts"]),
            "--iterations", str(params["iterations"]),
            "--initial-temperature", str(params["initial_temperature"]),
            "--final-temperature", str(params["final_temperature"]),
            "--seed", str(params["seed"]),
            "--runs-out", str(runs_out),
            "--summary-out", str(summary_out),
        ]

        print("=" * 80)
        print("Running", run_id + 1, "of", len(grid), tag)
        subprocess.run(cmd, check=True)

        summary = json.loads(summary_out.read_text())
        row = {
            "run_id": run_id,
            "tag": tag,
            "restarts": params["restarts"],
            "iterations": params["iterations"],
            "initial_temperature": params["initial_temperature"],
            "final_temperature": params["final_temperature"],
            "seed": params["seed"],
            "best_energy": summary["best_energy"],
            "best_bitstring": summary["best_bitstring"],
            "best_gap_to_bruteforce": summary["best_gap_to_bruteforce"],
            "success_count": summary["success_count"],
            "success_rate": summary["success_rate"],
            "validation_status": summary["validation_status"],
            "runs_csv": str(runs_out),
            "summary_json": str(summary_out),
        }
        rows.append(row)
        print("best_energy =", row["best_energy"], "success_rate =", row["success_rate"])

    summary_csv = Path("results/tables/small_external_package_sa_parameter_sensitivity_summary.csv")
    best_json = Path("results/tables/small_external_package_sa_parameter_sensitivity_best.json")

    with summary_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best_by_success = max(rows, key=lambda row: (row["success_rate"], -row["best_energy"]))
    best_json.write_text(json.dumps({
        "experiment": "small_external_package_sa_parameter_sensitivity",
        "num_cases": len(rows),
        "brute_force_optimum": BRUTE_FORCE_OPTIMUM,
        "best_case": best_by_success,
        "note": "Parameter sensitivity for small external package SA solver.",
    }, indent=2))

    print("=" * 80)
    print("SA parameter sensitivity complete")
    print("saved summary_csv =", summary_csv)
    print("saved best_json =", best_json)
    print(json.dumps(best_by_success, indent=2))

if __name__ == "__main__":
    main()
