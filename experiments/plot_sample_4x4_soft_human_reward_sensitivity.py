import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt


def save_line_plot(df, x_col, y_cols, title, y_label, output_path):
    plt.figure(figsize=(9, 6))

    for y_col in y_cols:
        plt.plot(df[x_col], df[y_col], marker="o", label=y_col)

    plt.title(title)
    plt.xlabel("Human assignment reward")
    plt.ylabel(y_label)
    plt.xticks(df[x_col])
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"
    figures_dir = PROJECT_ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    input_path = tables_dir / "sample_4x4_soft_human_reward_sensitivity.csv"

    if not input_path.exists():
        print("Missing:", input_path)
        print("Run this first:")
        print("python experiments/run_sample_4x4_soft_human_reward_sensitivity.py")
        return

    df = pd.read_csv(input_path)
    df = df.sort_values("human_reward")

    print("=== Plotting sample_4x4 soft human-reward sensitivity ===")
    print("Loaded:", input_path)
    print("Rows:", len(df))

    # ------------------------------------------------------------
    # Figure 1: Human assignments vs reward
    # ------------------------------------------------------------
    human_assignment_path = figures_dir / "sample_4x4_soft_reward_human_assignments.png"

    save_line_plot(
        df=df,
        x_col="human_reward",
        y_cols=["human_assignment_count"],
        title="sample_4x4: Human Assignments vs Human Reward",
        y_label="Number of human-assigned operations",
        output_path=human_assignment_path
    )

    # ------------------------------------------------------------
    # Figure 2: Total cost without reward vs reward-adjusted objective
    # ------------------------------------------------------------
    objective_path = figures_dir / "sample_4x4_soft_reward_objective_tradeoff.png"

    save_line_plot(
        df=df,
        x_col="human_reward",
        y_cols=[
            "total_cost_without_reward",
            "reward_adjusted_objective"
        ],
        title="sample_4x4: Cost vs Reward-Adjusted Objective",
        y_label="Objective / cost value",
        output_path=objective_path
    )

    # ------------------------------------------------------------
    # Figure 3: Human-centered costs
    # ------------------------------------------------------------
    human_cost_path = figures_dir / "sample_4x4_soft_reward_human_centered_costs.png"

    save_line_plot(
        df=df,
        x_col="human_reward",
        y_cols=[
            "workload",
            "ergonomic",
            "safety"
        ],
        title="sample_4x4: Human-Centered Costs vs Human Reward",
        y_label="Cost component value",
        output_path=human_cost_path
    )

    # ------------------------------------------------------------
    # Figure 4: Assignment counts
    # ------------------------------------------------------------
    assignment_path = figures_dir / "sample_4x4_soft_reward_assignment_counts.png"

    save_line_plot(
        df=df,
        x_col="human_reward",
        y_cols=[
            "human_assignment_count",
            "machine_assignment_count",
            "robot_assignment_count"
        ],
        title="sample_4x4: Assignment Counts vs Human Reward",
        y_label="Number of assigned operations",
        output_path=assignment_path
    )

    print()
    print("Saved figures:")
    print(human_assignment_path)
    print(objective_path)
    print(human_cost_path)
    print(assignment_path)


if __name__ == "__main__":
    main()
