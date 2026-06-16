"""
Full energy validation for sample_4x4 squared target penalty pilot.

Purpose
-------
This script validates that the stored adjusted objective for each row in the
sample_4x4 squared target penalty batch result matches the recomputed
QUBO-compatible objective:

    energy
        = total_cost_without_reward
          - human_reward * human_assignments
          + lambda_target * (human_assignments - target_human_assignments)^2

This is a formulation-level energy consistency check.

It verifies that the CP-SAT equivalent objective values stored in the result
table are consistent with the QUBO-compatible squared target formulation.

Input
-----
results/tables/sample_4x4_squared_target_penalty_batch.csv

Outputs
-------
results/tables/sample_4x4_squared_target_energy_validation.csv
results/tables/sample_4x4_squared_target_energy_validation_summary.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        type=str,
        default="results/tables/sample_4x4_squared_target_penalty_batch.csv",
    )

    parser.add_argument(
        "--out",
        type=str,
        default="results/tables/sample_4x4_squared_target_energy_validation.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_squared_target_energy_validation_summary.csv",
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-9,
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    out_path = Path(args.out)
    summary_out = Path(args.summary_out)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    solved = df[df["status"].isin(["OPTIMAL", "FEASIBLE"])].copy()

    if solved.empty:
        raise RuntimeError("No OPTIMAL or FEASIBLE rows found.")

    solved["recomputed_squared_target_energy"] = (
        solved["total_cost_without_reward"]
        - solved["human_reward"] * solved["human_assignments"]
        + solved["lambda_target"]
        * (
            solved["human_assignments"]
            - solved["target_human_assignments"]
        )
        ** 2
    )

    solved["abs_error_vs_manual"] = (
        solved["recomputed_squared_target_energy"]
        - solved["adjusted_objective_manual"]
    ).abs()

    if "objective_cp_sat" in solved.columns:
        solved["abs_error_vs_cp_sat"] = (
            solved["recomputed_squared_target_energy"]
            - solved["objective_cp_sat"]
        ).abs()
    else:
        solved["abs_error_vs_cp_sat"] = None

    validation_cols = [
        "seed",
        "human_reward",
        "lambda_target",
        "target_human_assignments",
        "status",
        "human_assignments",
        "distance_from_target",
        "squared_deviation",
        "total_cost_without_reward",
        "reward_term",
        "squared_target_penalty_term",
        "adjusted_objective_manual",
        "objective_cp_sat",
        "recomputed_squared_target_energy",
        "abs_error_vs_manual",
        "abs_error_vs_cp_sat",
    ]

    available_cols = [c for c in validation_cols if c in solved.columns]
    validation_df = solved[available_cols].copy()
    validation_df.to_csv(out_path, index=False)

    max_abs_error_vs_manual = float(validation_df["abs_error_vs_manual"].max())
    mean_abs_error_vs_manual = float(validation_df["abs_error_vs_manual"].mean())

    if "abs_error_vs_cp_sat" in validation_df.columns:
        max_abs_error_vs_cp_sat = float(validation_df["abs_error_vs_cp_sat"].max())
        mean_abs_error_vs_cp_sat = float(validation_df["abs_error_vs_cp_sat"].mean())
    else:
        max_abs_error_vs_cp_sat = None
        mean_abs_error_vs_cp_sat = None

    pass_manual = max_abs_error_vs_manual <= args.tolerance

    # CP-SAT objective may differ only by numerical scaling/rounding. In this
    # current formulation, values should normally match very closely as well.
    pass_cp_sat = (
        max_abs_error_vs_cp_sat is not None
        and max_abs_error_vs_cp_sat <= args.tolerance
    )

    summary = pd.DataFrame(
        [
            {
                "input_rows": len(df),
                "solved_rows": len(solved),
                "tolerance": args.tolerance,
                "max_abs_error_vs_manual": max_abs_error_vs_manual,
                "mean_abs_error_vs_manual": mean_abs_error_vs_manual,
                "pass_vs_manual": pass_manual,
                "max_abs_error_vs_cp_sat": max_abs_error_vs_cp_sat,
                "mean_abs_error_vs_cp_sat": mean_abs_error_vs_cp_sat,
                "pass_vs_cp_sat": pass_cp_sat,
                "validation_status": "PASS" if pass_manual else "FAIL",
            }
        ]
    )

    summary.to_csv(summary_out, index=False)

    print("=== sample_4x4 squared target energy validation ===")
    print(f"Input: {input_path}")
    print(f"Input rows: {len(df)}")
    print(f"Solved rows: {len(solved)}")
    print(f"Output: {out_path}")
    print(f"Summary: {summary_out}")
    print(f"Tolerance: {args.tolerance}")
    print(f"max_abs_error_vs_manual = {max_abs_error_vs_manual}")
    print(f"mean_abs_error_vs_manual = {mean_abs_error_vs_manual}")
    print(f"pass_vs_manual = {pass_manual}")
    print(f"max_abs_error_vs_cp_sat = {max_abs_error_vs_cp_sat}")
    print(f"mean_abs_error_vs_cp_sat = {mean_abs_error_vs_cp_sat}")
    print(f"pass_vs_cp_sat = {pass_cp_sat}")

    if pass_manual:
        print("VALIDATION PASS")
    else:
        print("VALIDATION FAIL")


if __name__ == "__main__":
    main()
