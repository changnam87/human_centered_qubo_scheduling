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
    plt.xlabel("Minimum human assignments")
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

    input_path = tables_dir / "sample_4x4_human_utilization_sensitivity.csv"

    if not input_path.exists():
        print("Missing:", input_path)
        print("Run this first:")
        print("python experiments/run_sample_4x4_human_utilization_sensitivity.py")
        return

    df = pd.read_csv(input_path)
    df = df.sort_values("min_human_assignments")

    print("=== Plotting sample_4x4 human-utilization sensitivity ===")
    print("Loaded:", input_path)
    print("Rows:", len(df))

    # ------------------------------------------------------------
    # Figure 1: Total cost curve
    # ------------------------------------------------------------
    total_cost_path = figures_dir / "sample_4x4_human_sensitivity_total_cost.png"

    save_line_plot(
        df=df,
        x_col="min_human_assignments",
        y_cols=["total_cost"],
        title="sample_4x4: Total Cost vs Minimum Human Assignments",
        y_label="Total cost",
        output_path=total_cost_path
    )

    # ------------------------------------------------------------
    # Figure 2: Human-centered cost terms
    # ------------------------------------------------------------
    human_cost_path = figures_dir / "sample_4x4_human_sensitivity_human_centered_costs.png"

    save_line_plot(
        df=df,
        x_col="min_human_assignments",
        y_cols=["workload", "ergonomic", "safety"],
        title="sample_4x4: Human-Centered Cost Terms",
        y_label="Cost component value",
        output_path=human_cost_path
    )

    # ------------------------------------------------------------
    # Figure 3: Assignment counts
    # ------------------------------------------------------------
    assignment_path = figures_dir / "sample_4x4_human_sensitivity_assignment_counts.png"

    save_line_plot(
        df=df,
        x_col="min_human_assignments",
        y_cols=[
            "human_assignment_count",
            "machine_assignment_count",
            "robot_assignment_count"
        ],
        title="sample_4x4: Assignment Counts by Resource Type",
        y_label="Number of assigned operations",
        output_path=assignment_path
    )

    # ------------------------------------------------------------
    # Figure 4: Main cost components
    # ------------------------------------------------------------
    cost_component_path = figures_dir / "sample_4x4_human_sensitivity_cost_components.png"

    save_line_plot(
        df=df,
        x_col="min_human_assignments",
        y_cols=[
            "processing",
            "start_time",
            "workload",
            "ergonomic",
            "safety"
        ],
        title="sample_4x4: Cost Component Breakdown",
        y_label="Cost component value",
        output_path=cost_component_path
    )

    print()
    print("Saved figures:")
    print(total_cost_path)
    print(human_cost_path)
    print(assignment_path)
    print(cost_component_path)


if __name__ == "__main__":
    main()
