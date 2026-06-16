"""
Analyze sample_4x4 soft reward + overuse penalty batch pilot.

Main questions
--------------
1. Does overuse penalty reduce excessive human assignment?
2. Which overuse penalty keeps human assignments closest to the target?
3. How does the trade-off differ across human_reward values?
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
        default="results/tables/sample_4x4_soft_reward_overuse_penalty_batch.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_soft_reward_overuse_penalty_summary.csv",
    )

    parser.add_argument(
        "--best-out",
        type=str,
        default="results/tables/sample_4x4_soft_reward_overuse_penalty_best_by_reward.csv",
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
        "overuse_count",
        "distance_from_target",
        "total_cost_without_reward",
        "adjusted_objective_manual",
        "workload",
        "ergonomic",
        "wall_seconds",
    ]

    summary = solved.groupby(["human_reward", "overuse_penalty"])[metrics].agg(
        ["mean", "std", "min", "max"]
    )

    summary.columns = ["_".join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    summary.to_csv(summary_out, index=False)

    # Best penalty by reward: closest average human assignments to target.
    best_rows = []

    for reward, group in summary.groupby("human_reward"):
        best = group.sort_values(
            ["distance_from_target_mean", "overuse_count_mean", "total_cost_without_reward_mean"]
        ).iloc[0]

        best_rows.append(
            {
                "human_reward": reward,
                "best_overuse_penalty": best["overuse_penalty"],
                "human_assignments_mean": best["human_assignments_mean"],
                "human_assignments_std": best["human_assignments_std"],
                "distance_from_target_mean": best["distance_from_target_mean"],
                "overuse_count_mean": best["overuse_count_mean"],
                "total_cost_without_reward_mean": best["total_cost_without_reward_mean"],
                "adjusted_objective_manual_mean": best["adjusted_objective_manual_mean"],
            }
        )

    best_df = pd.DataFrame(best_rows)
    best_df.to_csv(best_out, index=False)

    # Figure 1: Human assignments vs overuse penalty.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("overuse_penalty")
        plt.plot(
            group["overuse_penalty"],
            group["human_assignments_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    target = int(solved["target_human_assignments"].iloc[0])
    plt.axhline(target, linestyle="--", label=f"target={target}")
    plt.xlabel("Overuse penalty")
    plt.ylabel("Mean human assignments")
    plt.title("sample_4x4: human assignments vs overuse penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_overuse_penalty_human_assignments.png",
        dpi=300,
    )
    plt.close()

    # Figure 2: Distance from target vs overuse penalty.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("overuse_penalty")
        plt.plot(
            group["overuse_penalty"],
            group["distance_from_target_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Overuse penalty")
    plt.ylabel("Mean distance from target")
    plt.title("sample_4x4: distance from target vs overuse penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_overuse_penalty_distance_from_target.png",
        dpi=300,
    )
    plt.close()

    # Figure 3: Cost before reward vs overuse penalty.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("overuse_penalty")
        plt.plot(
            group["overuse_penalty"],
            group["total_cost_without_reward_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Overuse penalty")
    plt.ylabel("Mean total cost without reward")
    plt.title("sample_4x4: cost before reward vs overuse penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_overuse_penalty_cost_without_reward.png",
        dpi=300,
    )
    plt.close()

    # Figure 4: Adjusted objective vs overuse penalty.
    plt.figure()

    for reward, group in summary.groupby("human_reward"):
        group = group.sort_values("overuse_penalty")
        plt.plot(
            group["overuse_penalty"],
            group["adjusted_objective_manual_mean"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Overuse penalty")
    plt.ylabel("Mean adjusted objective")
    plt.title("sample_4x4: adjusted objective vs overuse penalty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "sample_4x4_overuse_penalty_adjusted_objective.png",
        dpi=300,
    )
    plt.close()

    print("=== Overuse penalty analysis complete ===")
    print(f"Input rows: {len(df)}")
    print(f"Solved rows: {len(solved)}")
    print(f"Saved summary: {summary_out}")
    print(f"Saved best-by-reward table: {best_out}")
    print(f"Saved figures to: {fig_dir}")

    print("\n=== Best overuse penalty by reward ===")
    print(best_df.to_string(index=False))

    print("\n=== Summary preview ===")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
