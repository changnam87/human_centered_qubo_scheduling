"""Run parameter sensitivity for sample_4x4 merged QUBO local search.

This script repeatedly calls the existing local search prototype with different
restarts, iterations, temperature settings, and random seeds.

Purpose:
    Try to reduce the gap between the current local QUBO best solution and the
    objective-equivalent CP-SAT squared-target optimum.

Reference:
    CP-SAT squared-target optimum = 47.70
    previous local QUBO best = 51.25
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

CP_SAT_OPTIMUM = 47.70

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Run a smaller quick grid.")
    parser.add_argument("--chunksize", type=int, default=500000)
    args = parser.parse_args()

    out_dir = Path("results/tables/local_search_parameter_sensitivity")
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.quick:
        grid = [
            {"restarts": 20, "iterations": 5000, "initial_temperature": 10.0, "final_temperature": 0.01, "seed": 123},
            {"restarts": 30, "iterations": 10000, "initial_temperature": 10.0, "final_temperature": 0.01, "seed": 123},
            {"restarts": 30, "iterations": 10000, "initial_temperature": 20.0, "final_temperature": 0.001, "seed": 456},
        ]
    else:
        grid = []
        for restarts in [30, 50]:
            for iterations in [10000, 20000]:
                for initial_temperature in [5.0, 10.0, 20.0]:
                    for final_temperature in [0.001, 0.01]:
                        for seed in [123, 456, 789]:
                            grid.append({
                                "restarts": restarts,
                                "iterations": iterations,
                                "initial_temperature": initial_temperature,
                                "final_temperature": final_temperature,
                                "seed": seed,
                            })

    summary_rows = []

    for run_id, params in enumerate(grid):
        tag = (
            f"run{run_id:03d}_r{params['restarts']}"
            f"_it{params['iterations']}"
            f"_t{params['initial_temperature']}"
            f"_tf{params['final_temperature']}"
            f"_s{params['seed']}"
        )

        runs_out = out_dir / f"{tag}_runs.csv"
        best_out = out_dir / f"{tag}_best_solution.csv"
        summary_out = out_dir / f"{tag}_summary.json"

        cmd = [
            sys.executable,
            "scripts/run_sample_4x4_merged_qubo_local_search.py",
            "--restarts", str(params["restarts"]),
            "--iterations", str(params["iterations"]),
            "--chunksize", str(args.chunksize),
            "--seed", str(params["seed"]),
            "--initial-temperature", str(params["initial_temperature"]),
            "--final-temperature", str(params["final_temperature"]),
            "--runs-out", str(runs_out),
            "--best-solution-out", str(best_out),
            "--summary-out", str(summary_out),
        ]

        print("=" * 80)
        print(f"Running sensitivity case {run_id + 1}/{len(grid)}: {tag}")
        print(" ".join(cmd))
        subprocess.run(cmd, check=True)

        summary = json.loads(summary_out.read_text())
        best_energy = float(summary["best_energy"])
        abs_gap = best_energy - CP_SAT_OPTIMUM
        rel_gap = abs_gap / CP_SAT_OPTIMUM

        row = {
            "run_id": run_id,
            "tag": tag,
            "restarts": params["restarts"],
            "iterations": params["iterations"],
            "initial_temperature": params["initial_temperature"],
            "final_temperature": params["final_temperature"],
            "seed": params["seed"],
            "best_energy": best_energy,
            "cpsat_optimum": CP_SAT_OPTIMUM,
            "absolute_gap": abs_gap,
            "relative_gap": rel_gap,
            "feasible_runs": summary["feasible_runs"],
            "feasible_rate": summary["feasible_rate"],
            "best_run": summary["best_run"],
            "load_seconds": summary["load_seconds"],
            "runs_csv": str(runs_out),
            "best_solution_csv": str(best_out),
            "summary_json": str(summary_out),
        }

        summary_rows.append(row)
        print(f"best_energy={best_energy:.4f}, abs_gap={abs_gap:.4f}, rel_gap={rel_gap:.4%}")

    summary_csv = Path("results/tables/sample_4x4_local_search_parameter_sensitivity_summary.csv")
    summary_json = Path("results/tables/sample_4x4_local_search_parameter_sensitivity_best.json")

    with summary_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    best_row = min(summary_rows, key=lambda row: row["best_energy"])
    summary_json.write_text(json.dumps({
        "experiment": "sample_4x4_local_search_parameter_sensitivity",
        "num_cases": len(summary_rows),
        "cpsat_optimum": CP_SAT_OPTIMUM,
        "previous_local_best": 51.25,
        "best_case": best_row,
        "note": "Prototype local search sensitivity; not a proof of optimality.",
    }, indent=2))

    print("=" * 80)
    print("Parameter sensitivity complete")
    print(f"Saved summary CSV: {summary_csv}")
    print(f"Saved best JSON: {summary_json}")
    print("Best case:")
    print(json.dumps(best_row, indent=2))

if __name__ == "__main__":
    main()
