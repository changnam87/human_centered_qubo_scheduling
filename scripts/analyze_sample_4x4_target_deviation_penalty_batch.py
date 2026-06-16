"""
Analyze sample_4x4 target-deviation penalty batch pilot.

Main questions
--------------
1. Does target_deviation_penalty pull human assignments toward target=4?
2. Can the penalty induce human involvement even when human_reward is low?
3. Which penalty value gives the smallest distance from target for each reward?
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
        default="results/tables/sample_4x4_target_deviation_penalty_batch.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_target_deviation_penalty_summary.csv",
    )

    parser.add_argument(
        "--best-out",
        type=str,
        default="results/tables/sample_4x4_target_deviation_penalty_best_by_reward.csv",
    )

    parser.add_argument(
        "--fig-dir",
        type=str,
        default="results/figures",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    summary_out = Path(args.summary_out)
    best_out = Path(args.best_out)
    fig_dir = Path(args.fig_dir)

    summary_out.parent.mkdir(parents=True, exist_ok=True)
    best_out.parent.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    solved = df[df["status"].isin(["OPTIMAL", "FEASIBLE"])].copy()

    if solved.empty:
        raise RuntimeError("No OPTIMAL or FEASIBLE rows found.")

    metrics = [
        "human_assignments",
        "distance_from_target",
        "total_cost_without_reward",
        "adjusted_objective_manual",
        "workload",
        "ergonomic",
        "wall_seconds",
    ]

    summary = solved.groupby(["human_reward", "target_deviation_penalty"])[metrics].agg(
        ["mean", "std", "min", "max"]
    )

    summary.columns = ["_".join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    summary.to_csv(summary_out, index=False)

    best_rows = []

    for reward, group in summary.groupby("human_reward"):
        best = group.sort_values(
            [
                "distance_from_target_mean",
                "human_assignments_std",
                "total_cost_without_reward_mean",
            ]
        ).iloc[0]

        best_rows.append(
            {
                "human_reward": reward,
                "best_target_deviation_penalty": best["target_deviation_penalty"],
                "human_assignments_mean": best["human_assignments_mean"],
                "human_assignments_std": best["human_assignments_std"],
                "distance_from_target_mean": best["distance_from_target_mean"],
                "total_cost_without_reward_mean": best["total_cost_without_reward_mean"],
                "adjusted_objective_manual_mean": best["adjusted_objective_manual_mean"],
                "workload_mean": best["workload_mean"],
                "ergonomic_mean": best["ergonomic_mean"],
            }
        )

    best_df = pd.DataFrame(best_rows)
    best_df.to_csv(best_out, index=False)

    target = int(solved["target_human_assignments"].iloc[0])

    # Figure 1: Human assignments vs target deviation penalty.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("target_deviation_penalty")
        plt.plot(
            group["target_deviation_penalty"],
            group["human_assignments_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.axhline(target, linestyle="--", label=f"target={target}")
    plt.xlabel("Target deviation penalty")
    plt.ylabel("Mean human assignments")
    plt.title("sample_4x4: human assignments vs target-deviation penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_target_deviation_human_assignments.png",
        dpi=300,
    )
    plt.close()

    # Figure 2: Distance from target.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("target_deviation_penalty")
        plt.plot(
            group["target_deviation_penalty"],
            group["distance_from_target_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Target deviation penalty")
    plt.ylabel("Mean distance from target")
    plt.title("sample_4x4: distance from target vs target-deviation penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_target_deviation_distance_from_target.png",
        dpi=300,
    )
    plt.close()

    # Figure 3: Cost without reward.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("target_deviation_penalty")
        plt.plot(
            group["target_deviation_penalty"],
            group["total_cost_without_reward_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Target deviation penalty")
    plt.ylabel("Mean total cost without reward")
    plt.title("sample_4x4: cost before reward vs target-deviation penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_target_deviation_cost_without_reward.png",
        dpi=300,
    )
    plt.close()

    # Figure 4: Adjusted objective.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("target_deviation_penalty")
        plt.plot(
            group["target_deviation_penalty"],
            group["adjusted_objective_manual_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Target deviation penalty")
    plt.ylabel("Mean adjusted objective")
    plt.title("sample_4x4: adjusted objective vs target-deviation penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_target_deviation_adjusted_objective.png",
        dpi=300,
    )
    plt.close()

    print("=== Target-deviation penalty analysis complete ===")
    print(f"Input rows: {len(df)}")
    print(f"Solved rows: {len(solved)}")
    print(f"Saved summary: {summary_out}")
    print(f"Saved best-by-reward table: {best_out}")
    print(f"Saved figures to: {fig_dir}")

    print("\n=== Best target-deviation penalty by reward ===")
    print(best_df.to_string(index=False))

    print("\n=== Summary preview ===")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
