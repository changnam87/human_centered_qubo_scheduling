"""
Analyze sample_4x4 soft human-reward batch sensitivity results.

Outputs
-------
1. Per-seed threshold table:
   - first reward where human_assignments >= 1
   - first reward where human_assignments >= 2
   - first reward where human_assignments >= 3

2. Summary statistics by reward:
   - mean/std/min/max human assignments
   - mean/std reward-adjusted objective
   - mean/std total cost without reward
   - mean/std workload
   - mean/std ergonomic

3. Figures:
   - human assignments vs reward
   - total cost without reward vs reward
   - reward-adjusted objective vs reward
   - threshold distribution
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def first_reward_at_least(group: pd.DataFrame, target: int):
    eligible = group[group["human_assignments"] >= target]
    if eligible.empty:
        return None
    return int(eligible["human_reward"].min())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        default="results/tables/sample_4x4_soft_human_reward_batch_sensitivity.csv",
    )
    parser.add_argument(
        "--threshold-out",
        type=str,
        default="results/tables/sample_4x4_soft_human_reward_batch_thresholds.csv",
    )
    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_soft_human_reward_batch_summary_by_reward.csv",
    )
    parser.add_argument(
        "--fig-dir",
        type=str,
        default="results/figures",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    threshold_out = Path(args.threshold_out)
    summary_out = Path(args.summary_out)
    fig_dir = Path(args.fig_dir)

    threshold_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    solved = df[df["status"].isin(["OPTIMAL", "FEASIBLE"])].copy()

    if solved.empty:
        raise RuntimeError("No OPTIMAL or FEASIBLE rows found.")

    # -----------------------------
    # Threshold table
    # -----------------------------
    threshold_rows = []

    for seed, group in solved.groupby("seed"):
        group = group.sort_values("human_reward")

        threshold_rows.append(
            {
                "seed": seed,
                "threshold_human_ge_1": first_reward_at_least(group, 1),
                "threshold_human_ge_2": first_reward_at_least(group, 2),
                "threshold_human_ge_3": first_reward_at_least(group, 3),
                "max_human_assignments": int(group["human_assignments"].max()),
                "human_assignments_at_reward_0": int(
                    group.loc[group["human_reward"] == 0, "human_assignments"].iloc[0]
                )
                if (group["human_reward"] == 0).any()
                else None,
                "human_assignments_at_reward_5": int(
                    group.loc[group["human_reward"] == 5, "human_assignments"].iloc[0]
                )
                if (group["human_reward"] == 5).any()
                else None,
            }
        )

    threshold_df = pd.DataFrame(threshold_rows)
    threshold_df.to_csv(threshold_out, index=False)

    # -----------------------------
    # Summary statistics by reward
    # -----------------------------
    metrics = [
        "human_assignments",
        "reward_adjusted_objective",
        "total_cost_without_reward",
        "start_time_cost",
        "assignment_cost",
        "workload",
        "ergonomic",
        "wall_seconds",
    ]

    summary = solved.groupby("human_reward")[metrics].agg(
        ["mean", "std", "min", "max"]
    )

    summary.columns = ["_".join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    summary.to_csv(summary_out, index=False)

    # -----------------------------
    # Figure 1: Human assignments vs reward
    # -----------------------------
    plt.figure()
    for seed, group in solved.groupby("seed"):
        group = group.sort_values("human_reward")
        plt.plot(
            group["human_reward"],
            group["human_assignments"],
            marker="o",
            alpha=0.5,
        )

    mean_by_reward = solved.groupby("human_reward")["human_assignments"].mean()
    plt.plot(
        mean_by_reward.index,
        mean_by_reward.values,
        marker="o",
        linewidth=3,
        label="Mean",
    )

    plt.xlabel("Human reward")
    plt.ylabel("Human assignments")
    plt.title("sample_4x4 soft human-reward sensitivity: human assignments")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "sample_4x4_soft_reward_batch_human_assignments.png", dpi=300)
    plt.close()

    # -----------------------------
    # Figure 2: Total cost without reward vs reward
    # -----------------------------
    plt.figure()
    for seed, group in solved.groupby("seed"):
        group = group.sort_values("human_reward")
        plt.plot(
            group["human_reward"],
            group["total_cost_without_reward"],
            marker="o",
            alpha=0.5,
        )

    mean_by_reward = solved.groupby("human_reward")[
        "total_cost_without_reward"
    ].mean()
    plt.plot(
        mean_by_reward.index,
        mean_by_reward.values,
        marker="o",
        linewidth=3,
        label="Mean",
    )

    plt.xlabel("Human reward")
    plt.ylabel("Total cost without reward")
    plt.title("sample_4x4 soft reward batch: cost before reward")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "sample_4x4_soft_reward_batch_cost_without_reward.png", dpi=300)
    plt.close()

    # -----------------------------
    # Figure 3: Reward-adjusted objective vs reward
    # -----------------------------
    plt.figure()
    for seed, group in solved.groupby("seed"):
        group = group.sort_values("human_reward")
        plt.plot(
            group["human_reward"],
            group["reward_adjusted_objective"],
            marker="o",
            alpha=0.5,
        )

    mean_by_reward = solved.groupby("human_reward")[
        "reward_adjusted_objective"
    ].mean()
    plt.plot(
        mean_by_reward.index,
        mean_by_reward.values,
        marker="o",
        linewidth=3,
        label="Mean",
    )

    plt.xlabel("Human reward")
    plt.ylabel("Reward-adjusted objective")
    plt.title("sample_4x4 soft reward batch: reward-adjusted objective")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "sample_4x4_soft_reward_batch_reward_adjusted_objective.png", dpi=300)
    plt.close()

    # -----------------------------
    # Figure 4: Threshold distribution
    # -----------------------------
    threshold_long = threshold_df.melt(
        id_vars=["seed"],
        value_vars=[
            "threshold_human_ge_1",
            "threshold_human_ge_2",
            "threshold_human_ge_3",
        ],
        var_name="threshold_type",
        value_name="first_reward",
    ).dropna()

    plt.figure()
    for label, group in threshold_long.groupby("threshold_type"):
        counts = group["first_reward"].value_counts().sort_index()
        plt.plot(counts.index, counts.values, marker="o", label=label)

    plt.xlabel("First reward value")
    plt.ylabel("Number of seeds")
    plt.title("sample_4x4 soft reward batch: threshold distribution")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "sample_4x4_soft_reward_batch_threshold_distribution.png", dpi=300)
    plt.close()

    print("=== Analysis complete ===")
    print(f"Input rows: {len(df)}")
    print(f"Solved rows: {len(solved)}")
    print(f"Saved threshold table: {threshold_out}")
    print(f"Saved summary table: {summary_out}")
    print(f"Saved figures to: {fig_dir}")

    print("\n=== Threshold table preview ===")
    print(threshold_df.to_string(index=False))

    print("\n=== Summary by reward preview ===")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
