"""
Summarize QUBO size scaling across prototype checkpoints.

This script collects manually defined prototype sizes and writes a simple
growth table for variables and QUBO terms.

Purpose
-------
The goal is to document how QUBO size grows as we move from:
1. assignment-only toy QUBO
2. small time-indexed QUBO
3. medium time-indexed QUBO
4. sample_4x4 CP-SAT-equivalent scale
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_json(path: str):
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def main() -> None:
    toy = load_json("results/tables/toy_squared_target_qubo_summary.json")
    small = load_json("results/tables/small_time_indexed_qubo_summary.json")
    medium = load_json("results/tables/medium_time_indexed_qubo_summary.json")

    rows = []

    if toy:
        rows.append(
            {
                "checkpoint": "toy_assignment_qubo",
                "operations": toy.get("num_operations"),
                "resources": toy.get("num_resources"),
                "horizon": None,
                "variables": toy.get("num_variables"),
                "qubo_terms": toy.get("num_qubo_terms"),
                "linear_terms": toy.get("num_linear_terms"),
                "quadratic_terms": toy.get("num_quadratic_terms"),
                "validation": toy.get("validation_status"),
                "validation_mode": "brute_force",
            }
        )

    if small:
        rows.append(
            {
                "checkpoint": "small_time_indexed_qubo",
                "operations": small.get("num_operations"),
                "resources": small.get("num_resources"),
                "horizon": small.get("horizon"),
                "variables": small.get("num_variables"),
                "qubo_terms": small.get("num_qubo_terms"),
                "linear_terms": small.get("num_linear_terms"),
                "quadratic_terms": small.get("num_quadratic_terms"),
                "validation": small.get("validation_status"),
                "validation_mode": "brute_force",
            }
        )

    if medium:
        rows.append(
            {
                "checkpoint": "medium_time_indexed_qubo",
                "operations": medium.get("num_operations"),
                "resources": medium.get("num_resources"),
                "horizon": medium.get("horizon"),
                "variables": medium.get("num_variables"),
                "qubo_terms": medium.get("num_qubo_terms"),
                "linear_terms": medium.get("num_linear_terms"),
                "quadratic_terms": medium.get("num_quadratic_terms"),
                "validation": medium.get("validation_status"),
                "validation_mode": "sampled_plus_greedy_feasible",
            }
        )

    rows.append(
        {
            "checkpoint": "sample_4x4_time_indexed_scale",
            "operations": 16,
            "resources": 9,
            "horizon": 63,
            "variables": 16 * 9 * 63,
            "qubo_terms": None,
            "linear_terms": None,
            "quadratic_terms": None,
            "validation": "cp_sat_equivalent_validated",
            "validation_mode": "energy_recompute_no_full_qubo_export_yet",
        }
    )

    df = pd.DataFrame(rows)

    out_path = Path("results/tables/qubo_size_scaling_summary.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print("=== QUBO size scaling summary ===")
    print(df.to_string(index=False))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
