"""QAOA parameter sensitivity for the tiny QAOA-ready package.

This script repeatedly runs the tiny QAOA simulator smoke test with different
reps, maxiter, and seed settings.

This is a tiny toy software/simulator experiment only.
It does not run quantum hardware and does not imply quantum advantage.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    out_dir = Path("results/tables/tiny_qaoa_parameter_sensitivity")
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.quick:
        grid = []
        for reps in [1, 2]:
            for maxiter in [50, 100]:
                for seed in [123, 456]:
                    grid.append({"reps": reps, "maxiter": maxiter, "seed": seed})
    else:
        grid = []
        for reps in [1, 2, 3]:
            for maxiter in [50, 100, 200]:
                for seed in [123, 456, 789, 1001, 2025]:
                    grid.append({"reps": reps, "maxiter": maxiter, "seed": seed})

    rows = []

    for run_id, params in enumerate(grid):
        tag = (
            "run" + str(run_id).zfill(3)
            + "_p" + str(params["reps"])
            + "_it" + str(params["maxiter"])
            + "_s" + str(params["seed"])
        )
        rows_out = out_dir / (tag + "_rows.csv")
        summary_out = out_dir / (tag + "_summary.json")

        cmd = [
            sys.executable,
            "scripts/run_tiny_qaoa_simulator_smoke_test.py",
            "--reps", str(params["reps"]),
            "--maxiter", str(params["maxiter"]),
            "--seed", str(params["seed"]),
            "--out", str(rows_out),
            "--summary-out", str(summary_out),
        ]

        print("=" * 80)
        print("Running", run_id + 1, "of", len(grid), tag)
        subprocess.run(cmd, check=True)

        summary = json.loads(summary_out.read_text())
        row = {
            "run_id": run_id,
            "tag": tag,
            "reps": params["reps"],
            "maxiter": params["maxiter"],
            "seed": params["seed"],
            "status": summary.get("status"),
            "sampler_name": summary.get("sampler_name"),
            "qaoa_status": summary.get("qaoa_status"),
            "known_best_bitstring": summary.get("known_best_bitstring"),
            "known_best_energy": summary.get("known_best_energy"),
            "qaoa_bitstring": summary.get("qaoa_bitstring"),
            "qaoa_energy": summary.get("qaoa_energy"),
            "qaoa_gap_to_known": summary.get("qaoa_gap_to_known"),
            "qaoa_matches_known": summary.get("qaoa_matches_known"),
            "summary_json": str(summary_out),
            "rows_csv": str(rows_out),
        }
        rows.append(row)
        print("status =", row["status"], "qaoa_bitstring =", row["qaoa_bitstring"], "gap =", row["qaoa_gap_to_known"])

    summary_csv = Path("results/tables/tiny_qaoa_parameter_sensitivity_summary.csv")
    best_json = Path("results/tables/tiny_qaoa_parameter_sensitivity_best.json")

    with summary_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    pass_rows = [r for r in rows if r["status"] == "PASS" and r["qaoa_matches_known"] is True]
    partial_rows = [r for r in rows if r["status"] == "PARTIAL_PASS"]
    skipped_rows = [r for r in rows if r["status"] == "SKIPPED"]
    fail_rows = [r for r in rows if r["status"] == "FAIL"]

    success_rate = len(pass_rows) / len(rows) if rows else 0.0
    best_case = None
    if pass_rows:
        best_case = min(pass_rows, key=lambda r: (r["reps"], r["maxiter"], r["seed"]))
    else:
        valid_energy_rows = [r for r in rows if r["qaoa_gap_to_known"] is not None]
        if valid_energy_rows:
            best_case = min(valid_energy_rows, key=lambda r: abs(float(r["qaoa_gap_to_known"])))

    best_summary = {
        "experiment": "tiny_qaoa_parameter_sensitivity",
        "num_cases": len(rows),
        "pass_count": len(pass_rows),
        "partial_pass_count": len(partial_rows),
        "skipped_count": len(skipped_rows),
        "fail_count": len(fail_rows),
        "success_rate": success_rate,
        "best_case": best_case,
        "note": "Tiny QAOA toy simulator parameter sensitivity only. No hardware or quantum advantage claim.",
    }
    best_json.write_text(json.dumps(best_summary, indent=2))

    print("=" * 80)
    print("tiny QAOA parameter sensitivity complete")
    print("num_cases =", len(rows))
    print("pass_count =", len(pass_rows))
    print("success_rate =", success_rate)
    print("saved summary_csv =", summary_csv)
    print("saved best_json =", best_json)
    print(json.dumps(best_summary, indent=2))

if __name__ == "__main__":
    main()
