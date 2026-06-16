"""Summarize solver benchmarks for the small external QUBO/Ising package.

This script consolidates:
  1. brute-force smoke test
  2. initial simulated annealing baseline
  3. best simulated annealing parameter sensitivity case

It does not rerun solvers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

def read_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print("WARNING missing " + str(p))
        return {}
    return json.loads(p.read_text())

def main() -> None:
    brute = read_json("results/tables/small_external_solver_smoke_test_summary.json")
    sa_initial = read_json("results/tables/small_external_package_sa_solver_summary.json")
    sa_sensitivity = read_json("results/tables/small_external_package_sa_parameter_sensitivity_best.json")
    package_metadata = read_json("exports/small_time_indexed_solver_package/package_metadata.json")

    best_case = sa_sensitivity.get("best_case", {})

    rows = []

    rows.append({
        "solver": "brute_force",
        "description": "Exhaustive enumeration over all assignments.",
        "num_variables": brute.get("num_variables"),
        "assignments_or_restarts": brute.get("num_assignments_enumerated"),
        "iterations_per_restart": None,
        "initial_temperature": None,
        "final_temperature": None,
        "seed": None,
        "best_energy": brute.get("best_qubo_energy"),
        "best_bitstring": brute.get("best_bitstring"),
        "gap_to_bruteforce": 0.0,
        "success_count": brute.get("num_assignments_enumerated"),
        "success_rate": 1.0,
        "validation_status": brute.get("validation_status"),
    })

    rows.append({
        "solver": "simulated_annealing_initial",
        "description": "Initial bit-flip simulated annealing baseline.",
        "num_variables": sa_initial.get("num_variables"),
        "assignments_or_restarts": sa_initial.get("restarts"),
        "iterations_per_restart": sa_initial.get("iterations"),
        "initial_temperature": sa_initial.get("initial_temperature"),
        "final_temperature": sa_initial.get("final_temperature"),
        "seed": sa_initial.get("seed"),
        "best_energy": sa_initial.get("best_energy"),
        "best_bitstring": sa_initial.get("best_bitstring"),
        "gap_to_bruteforce": sa_initial.get("best_gap_to_bruteforce"),
        "success_count": sa_initial.get("success_count"),
        "success_rate": sa_initial.get("success_rate"),
        "validation_status": sa_initial.get("validation_status"),
    })

    rows.append({
        "solver": "simulated_annealing_best_sensitivity",
        "description": "Best case from SA parameter sensitivity grid.",
        "num_variables": package_metadata.get("num_variables"),
        "assignments_or_restarts": best_case.get("restarts"),
        "iterations_per_restart": best_case.get("iterations"),
        "initial_temperature": best_case.get("initial_temperature"),
        "final_temperature": best_case.get("final_temperature"),
        "seed": best_case.get("seed"),
        "best_energy": best_case.get("best_energy"),
        "best_bitstring": best_case.get("best_bitstring"),
        "gap_to_bruteforce": best_case.get("best_gap_to_bruteforce"),
        "success_count": best_case.get("success_count"),
        "success_rate": best_case.get("success_rate"),
        "validation_status": best_case.get("validation_status"),
    })

    out_csv = Path("results/tables/small_external_package_solver_benchmark_summary.csv")
    out_json = Path("results/tables/small_external_package_solver_benchmark_summary.json")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)

    summary = {
        "experiment": "small_external_package_solver_benchmark_summary",
        "package_dir": "exports/small_time_indexed_solver_package",
        "num_variables": package_metadata.get("num_variables"),
        "brute_force_optimum": brute.get("best_qubo_energy"),
        "brute_force_bitstring": brute.get("best_bitstring"),
        "initial_sa_success_rate": sa_initial.get("success_rate"),
        "best_sa_success_rate": best_case.get("success_rate"),
        "success_rate_improvement": None if sa_initial.get("success_rate") is None or best_case.get("success_rate") is None else best_case.get("success_rate") - sa_initial.get("success_rate"),
        "benchmark_rows": rows,
        "note": "Compact benchmark summary for the small external package; not a full sample_4x4 benchmark.",
    }

    out_json.write_text(json.dumps(summary, indent=2))

    print("=== small external package solver benchmark summary complete ===")
    print("saved csv =", out_csv)
    print("saved json =", out_json)
    print(json.dumps({
        "brute_force_optimum": summary["brute_force_optimum"],
        "initial_sa_success_rate": summary["initial_sa_success_rate"],
        "best_sa_success_rate": summary["best_sa_success_rate"],
        "success_rate_improvement": summary["success_rate_improvement"],
    }, indent=2))

if __name__ == "__main__":
    main()
