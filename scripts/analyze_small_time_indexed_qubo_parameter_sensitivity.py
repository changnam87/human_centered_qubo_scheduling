"""
Analyze small time-indexed QUBO parameter sensitivity.

Outputs:
1. Summary by constraint_penalty
2. Summary by human_reward and lambda_target
3. Best feasible/target-consistent settings
4. Figures
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        type=str,
        default="results/tables/small_time_indexed_qubo_parameter_sensitivity.csv",
    )

    parser.add_argument(
        "--summary-constraint-out",
        type=str,
        default="results/tables/small_time_indexed_qubo_summary_by_constraint_penalty.csv",
    )

    parser.add_argument(
        "--summary-reward-lambda-out",
        type=str,
        default="results/tables/small_time_indexed_qubo_summary_by_reward_lambda.csv",
    )

    parser.add_argument(
        "--target-consistent-out",
        type=str,
        default="results/tables/small_time_indexed_qubo_target_consistent_settings.csv",
    )

    parser.add_argument(
        "--fig-dir",
        type=str,
        default="results/figures",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    summary_constraint_out = Path(args.summary_constraint_out)
    summary_reward_lambda_out = Path(args.summary_reward_lambda_out)
    target_consistent_out = Path(args.target_consistent_out)
    fig_dir = Path(args.fig_dir)

    summary_constraint_out.parent.mkdir(parents=True, exist_ok=True)
    summary_reward_lambda_out.parent.mkdir(parents=True, exist_ok=True)
    target_consistent_out.parent.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    df["best_all_feasible_int"] = df["best_all_feasible"].astype(int)
    df["best_all_target_consistent"] = (
        (df["best_all_feasible"] == True)
        & (df["best_all_distance_from_target"] == 0)
    )
    df["best_all_target_consistent_int"] = df["best_all_target_consistent"].astype(int)

    # Summary by constraint penalty.
    summary_constraint = (
        df.groupby("constraint_penalty")
        .agg(
            settings=("constraint_penalty", "count"),
            feasible_rate=("best_all_feasible_int", "mean"),
            target_consistent_rate=("best_all_target_consistent_int", "mean"),
            mean_best_all_human_count=("best_all_human_count", "mean"),
            mean_best_all_distance_from_target=("best_all_distance_from_target", "mean"),
            mean_assignment_violations=("best_all_assignment_violations", "mean"),
            mean_overlap_violations=("best_all_overlap_violations", "mean"),
            mean_precedence_violations=("best_all_precedence_violations", "mean"),
        )
        .reset_index()
    )

    summary_constraint.to_csv(summary_constraint_out, index=False)

    # Summary by reward/lambda.
    summary_reward_lambda = (
        df.groupby(["human_reward", "lambda_target"])
        .agg(
            settings=("human_reward", "count"),
            feasible_rate=("best_all_feasible_int", "mean"),
            target_consistent_rate=("best_all_target_consistent_int", "mean"),
            mean_best_all_human_count=("best_all_human_count", "mean"),
            mean_best_all_distance_from_target=("best_all_distance_from_target", "mean"),
        )
        .reset_index()
    )

    summary_reward_lambda.to_csv(summary_reward_lambda_out, index=False)

    # Target-consistent settings.
    target_consistent = df[df["best_all_target_consistent"]].copy()
    target_consistent = target_consistent.sort_values(
        ["constraint_penalty", "human_reward", "lambda_target"]
    )
    target_consistent.to_csv(target_consistent_out, index=False)

    # Figure 1: Feasibility rate vs constraint penalty.
    plt.figure()
    plt.plot(
        summary_constraint["constraint_penalty"],
        summary_constraint["feasible_rate"],
        marker="o",
    )
    plt.xlabel("Constraint penalty")
    plt.ylabel("Feasibility rate of QUBO optimum")
    plt.title("Small time-indexed QUBO: feasibility vs constraint penalty")
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_feasibility_vs_constraint_penalty.png",
        dpi=300,
    )
    plt.close()

    # Figure 2: Target-consistent rate vs constraint penalty.
    plt.figure()
    plt.plot(
        summary_constraint["constraint_penalty"],
        summary_constraint["target_consistent_rate"],
        marker="o",
    )
    plt.xlabel("Constraint penalty")
    plt.ylabel("Target-consistent feasible optimum rate")
    plt.title("Small time-indexed QUBO: target consistency vs constraint penalty")
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_target_consistency_vs_constraint_penalty.png",
        dpi=300,
    )
    plt.close()

    # Figure 3: Mean violations vs constraint penalty.
    plt.figure()
    plt.plot(
        summary_constraint["constraint_penalty"],
        summary_constraint["mean_assignment_violations"],
        marker="o",
        label="assignment",
    )
    plt.plot(
        summary_constraint["constraint_penalty"],
        summary_constraint["mean_overlap_violations"],
        marker="o",
        label="overlap",
    )
    plt.plot(
        summary_constraint["constraint_penalty"],
        summary_constraint["mean_precedence_violations"],
        marker="o",
        label="precedence",
    )
    plt.xlabel("Constraint penalty")
    plt.ylabel("Mean violations in QUBO optimum")
    plt.title("Small time-indexed QUBO: violations vs constraint penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_violations_vs_constraint_penalty.png",
        dpi=300,
    )
    plt.close()

    # Figure 4: Human count by reward/lambda at largest constraint penalty.
    max_penalty = df["constraint_penalty"].max()
    high_penalty_df = df[df["constraint_penalty"] == max_penalty].copy()

    plt.figure()

    for reward, group in high_penalty_df.groupby("human_reward"):
        group = group.sort_values("lambda_target")
        plt.plot(
            group["lambda_target"],
            group["best_all_human_count"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.axhline(1, linestyle="--", label="target=1")
    plt.xlabel("Lambda target")
    plt.ylabel("Human count in QUBO optimum")
    plt.title("Small time-indexed QUBO: human count at high constraint penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_human_count_high_penalty.png",
        dpi=300,
    )
    plt.close()

    print("=== Small time-indexed QUBO parameter sensitivity analysis ===")
    print(f"Input rows: {len(df)}")
    print(f"Saved summary by constraint penalty: {summary_constraint_out}")
    print(f"Saved summary by reward/lambda: {summary_reward_lambda_out}")
    print(f"Saved target-consistent settings: {target_consistent_out}")
    print(f"Saved figures to: {fig_dir}")

    print("\n=== Summary by constraint penalty ===")
    print(summary_constraint.to_string(index=False))

    print("\n=== Number of target-consistent settings ===")
    print(len(target_consistent))


if __name__ == "__main__":
    main()
