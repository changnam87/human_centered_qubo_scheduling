"""
Analyze reward/lambda target-consistency map for the small time-indexed QUBO.

Purpose
-------
STEP 9 identified that constraint_penalty >= 5.0 stabilizes feasibility.

This script focuses on that feasible regime and analyzes which combinations of:

    human_reward
    lambda_target

produce target-consistent feasible QUBO optima.

Target consistency means:

    best_all_feasible == True
    best_all_distance_from_target == 0

This helps separate two roles:

1. constraint_penalty controls scheduling feasibility
2. human_reward and lambda_target control human-utilization target consistency

This remains a small prototype validation.
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
        "--min-stable-constraint-penalty",
        type=float,
        default=5.0,
    )

    parser.add_argument(
        "--map-out",
        type=str,
        default="results/tables/small_time_indexed_qubo_reward_lambda_target_map.csv",
    )

    parser.add_argument(
        "--heatmap-out",
        type=str,
        default="results/tables/small_time_indexed_qubo_reward_lambda_target_consistency_heatmap.csv",
    )

    parser.add_argument(
        "--settings-out",
        type=str,
        default="results/tables/small_time_indexed_qubo_reward_lambda_target_consistent_settings.csv",
    )

    parser.add_argument(
        "--fig-dir",
        type=str,
        default="results/figures",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    map_out = Path(args.map_out)
    heatmap_out = Path(args.heatmap_out)
    settings_out = Path(args.settings_out)
    fig_dir = Path(args.fig_dir)

    map_out.parent.mkdir(parents=True, exist_ok=True)
    heatmap_out.parent.mkdir(parents=True, exist_ok=True)
    settings_out.parent.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    stable = df[df["constraint_penalty"] >= args.min_stable_constraint_penalty].copy()

    if stable.empty:
        raise RuntimeError("No rows found in stable constraint-penalty regime.")

    stable["target_consistent"] = (
        (stable["best_all_feasible"] == True)
        & (stable["best_all_distance_from_target"] == 0)
    )

    stable["target_consistent_int"] = stable["target_consistent"].astype(int)
    stable["best_all_feasible_int"] = stable["best_all_feasible"].astype(int)

    # Summary map by reward/lambda.
    reward_lambda_map = (
        stable.groupby(["human_reward", "lambda_target"])
        .agg(
            settings=("human_reward", "count"),
            feasible_rate=("best_all_feasible_int", "mean"),
            target_consistent_rate=("target_consistent_int", "mean"),
            mean_human_count=("best_all_human_count", "mean"),
            mean_distance_from_target=("best_all_distance_from_target", "mean"),
            mean_energy=("best_all_energy", "mean"),
            min_energy=("best_all_energy", "min"),
            max_energy=("best_all_energy", "max"),
        )
        .reset_index()
    )

    reward_lambda_map.to_csv(map_out, index=False)

    # Heatmap-style wide table: rows = human_reward, cols = lambda_target.
    heatmap = reward_lambda_map.pivot(
        index="human_reward",
        columns="lambda_target",
        values="target_consistent_rate",
    )

    heatmap.to_csv(heatmap_out)

    target_consistent_settings = stable[stable["target_consistent"]].copy()
    target_consistent_settings = target_consistent_settings.sort_values(
        ["constraint_penalty", "human_reward", "lambda_target"]
    )
    target_consistent_settings.to_csv(settings_out, index=False)

    # Figure 1: target consistency rate by lambda for each reward.
    plt.figure()

    for reward, group in reward_lambda_map.groupby("human_reward"):
        group = group.sort_values("lambda_target")
        plt.plot(
            group["lambda_target"],
            group["target_consistent_rate"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Lambda target")
    plt.ylabel("Target-consistent rate")
    plt.title("Small time-indexed QUBO: target consistency by reward/lambda")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_target_consistency_reward_lambda.png",
        dpi=300,
    )
    plt.close()

    # Figure 2: mean human count by lambda for each reward.
    plt.figure()

    for reward, group in reward_lambda_map.groupby("human_reward"):
        group = group.sort_values("lambda_target")
        plt.plot(
            group["lambda_target"],
            group["mean_human_count"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.axhline(1, linestyle="--", label="target=1")
    plt.xlabel("Lambda target")
    plt.ylabel("Mean human count")
    plt.title("Small time-indexed QUBO: mean human count by reward/lambda")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_human_count_reward_lambda.png",
        dpi=300,
    )
    plt.close()

    # Figure 3: mean distance from target.
    plt.figure()

    for reward, group in reward_lambda_map.groupby("human_reward"):
        group = group.sort_values("lambda_target")
        plt.plot(
            group["lambda_target"],
            group["mean_distance_from_target"],
            marker="o",
            label=f"reward={reward}",
        )

    plt.xlabel("Lambda target")
    plt.ylabel("Mean distance from target")
    plt.title("Small time-indexed QUBO: distance from target by reward/lambda")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_distance_reward_lambda.png",
        dpi=300,
    )
    plt.close()

    # Figure 4: simple heatmap using matplotlib imshow.
    plt.figure()

    heatmap_values = heatmap.values
    plt.imshow(heatmap_values, aspect="auto")
    plt.colorbar(label="Target-consistent rate")
    plt.xticks(
        range(len(heatmap.columns)),
        [str(c) for c in heatmap.columns],
    )
    plt.yticks(
        range(len(heatmap.index)),
        [str(i) for i in heatmap.index],
    )
    plt.xlabel("Lambda target")
    plt.ylabel("Human reward")
    plt.title("Target-consistent rate heatmap")
    plt.tight_layout()
    plt.savefig(
        fig_dir / "small_time_indexed_qubo_reward_lambda_heatmap.png",
        dpi=300,
    )
    plt.close()

    print("=== Reward/lambda target-consistency map complete ===")
    print(f"Input rows: {len(df)}")
    print(f"Stable-regime rows: {len(stable)}")
    print(f"Minimum stable constraint penalty: {args.min_stable_constraint_penalty}")
    print(f"Saved reward/lambda map: {map_out}")
    print(f"Saved heatmap table: {heatmap_out}")
    print(f"Saved target-consistent settings: {settings_out}")
    print(f"Saved figures to: {fig_dir}")

    print("\n=== Reward/lambda target-consistency map ===")
    print(reward_lambda_map.to_string(index=False))

    print("\n=== Heatmap table ===")
    print(heatmap.to_string())

    print("\n=== Number of target-consistent settings ===")
    print(len(target_consistent_settings))


if __name__ == "__main__":
    main()
