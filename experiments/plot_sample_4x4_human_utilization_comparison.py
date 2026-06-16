import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt


def shorten_variant(name):
    if name == "Baseline CP-SAT":
        return "Baseline\nCP-SAT"
    if name == "Human-utilization CP-SAT":
        return "Human-utilization\nCP-SAT"
    return name


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"
    figures_dir = PROJECT_ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    input_path = tables_dir / "sample_4x4_human_utilization_comparison.csv"

    if not input_path.exists():
        print("Missing:", input_path)
        print("Run this first:")
        print("python experiments/build_sample_4x4_human_utilization_comparison.py")
        return

    df = pd.read_csv(input_path)

    print("=== Plotting sample_4x4 human-utilization comparison ===")
    print("Loaded:", input_path)

    labels = [shorten_variant(x) for x in df["model_variant"]]

    # ------------------------------------------------------------
    # Figure 1: Total cost comparison
    # ------------------------------------------------------------
    total_cost_path = figures_dir / "sample_4x4_human_utilization_total_cost.png"

    plt.figure(figsize=(8, 6))
    plt.bar(labels, df["total_cost"])
    plt.title("sample_4x4: Total Cost Comparison")
    plt.xlabel("Model variant")
    plt.ylabel("Total cost")
    plt.tight_layout()
    plt.savefig(total_cost_path, dpi=300)
    plt.close()

    # ------------------------------------------------------------
    # Figure 2: Assignment count comparison
    # Grouped bar chart using pandas/matplotlib.
    # ------------------------------------------------------------
    assignment_path = figures_dir / "sample_4x4_human_utilization_assignment_counts.png"

    assignment_df = df[[
        "model_variant",
        "machine_assignment_count",
        "robot_assignment_count",
        "human_assignment_count"
    ]].copy()

    assignment_df["model_variant"] = assignment_df["model_variant"].apply(shorten_variant)
    assignment_df = assignment_df.set_index("model_variant")

    plt.figure(figsize=(9, 6))
    assignment_df.plot(kind="bar", ax=plt.gca())
    plt.title("sample_4x4: Assignment Counts by Resource Type")
    plt.xlabel("Model variant")
    plt.ylabel("Number of assigned operations")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(assignment_path, dpi=300)
    plt.close()

    # ------------------------------------------------------------
    # Figure 3: Human-centered cost components
    # ------------------------------------------------------------
    human_cost_path = figures_dir / "sample_4x4_human_utilization_human_centered_costs.png"

    cost_df = df[[
        "model_variant",
        "workload",
        "ergonomic",
        "safety"
    ]].copy()

    cost_df["model_variant"] = cost_df["model_variant"].apply(shorten_variant)
    cost_df = cost_df.set_index("model_variant")

    plt.figure(figsize=(9, 6))
    cost_df.plot(kind="bar", ax=plt.gca())
    plt.title("sample_4x4: Human-Centered Cost Components")
    plt.xlabel("Model variant")
    plt.ylabel("Cost component value")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(human_cost_path, dpi=300)
    plt.close()

    print()
    print("Saved figures:")
    print(total_cost_path)
    print(assignment_path)
    print(human_cost_path)


if __name__ == "__main__":
    main()
