import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def shorten_label(label):
    if label == "Random-bit SA":
        return "Random-bit\nSA"
    if label == "Seeded search from handcrafted":
        return "Seeded search\nfrom handcrafted"
    if label == "Seeded search from CP-SAT":
        return "Seeded search\nfrom CP-SAT"
    return label


def plot_with_ci(df, x_col, y_col, lower_col, upper_col, title, y_label, output_path):
    labels = [shorten_label(x) for x in df[x_col]]
    y = df[y_col].astype(float).values
    lower = df[lower_col].astype(float).values
    upper = df[upper_col].astype(float).values

    yerr_lower = y - lower
    yerr_upper = upper - y

    plt.figure(figsize=(10, 6))
    plt.bar(labels, y, yerr=[yerr_lower, yerr_upper], capsize=6)
    plt.title(title)
    plt.xlabel("Search method")
    plt.ylabel(y_label)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"
    figures_dir = PROJECT_ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    stats_path = tables_dir / "sample_3x3_search_statistical_analysis.csv"
    cost_path = tables_dir / "sample_3x3_search_cost_summary_with_ci.csv"

    required_files = [stats_path, cost_path]

    print("=== Checking required files ===")
    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            return

    stats_df = pd.read_csv(stats_path)
    cost_df = pd.read_csv(cost_path)

    # ------------------------------------------------------------
    # 1. Feasibility rate + Wilson CI
    # ------------------------------------------------------------
    feasibility_df = stats_df[
        stats_df["analysis_type"] == "feasibility_proportion"
    ].copy()

    feasibility_df = feasibility_df.sort_values("method")

    feasibility_output = figures_dir / "sample_3x3_search_feasibility_rate_ci.png"

    plot_with_ci(
        df=feasibility_df,
        x_col="method",
        y_col="feasibility_rate",
        lower_col="ci_lower",
        upper_col="ci_upper",
        title="sample_3x3 Augmented: Feasibility Rate with 95% CI",
        y_label="Feasibility rate",
        output_path=feasibility_output
    )

    # ------------------------------------------------------------
    # 2. Mean feasible cost + bootstrap 95% CI
    # Exclude methods with no feasible reads
    # ------------------------------------------------------------
    feasible_cost_df = cost_df[
        cost_df["n_feasible"] > 0
    ].copy()

    feasible_cost_df = feasible_cost_df.sort_values("method")

    cost_output = figures_dir / "sample_3x3_search_mean_feasible_cost_ci.png"

    plot_with_ci(
        df=feasible_cost_df,
        x_col="method",
        y_col="mean_feasible_cost",
        lower_col="mean_cost_ci_lower",
        upper_col="mean_cost_ci_upper",
        title="sample_3x3 Augmented: Mean Feasible Cost with 95% CI",
        y_label="Mean feasible cost",
        output_path=cost_output
    )

    # ------------------------------------------------------------
    # 3. Mean gap to CP-SAT + bootstrap 95% CI
    # Exclude methods with no feasible reads
    # ------------------------------------------------------------
    gap_df = cost_df[
        cost_df["n_feasible"] > 0
    ].copy()

    gap_df = gap_df.sort_values("method")

    gap_output = figures_dir / "sample_3x3_search_mean_gap_to_cpsat_ci.png"

    plot_with_ci(
        df=gap_df,
        x_col="method",
        y_col="mean_gap_to_cpsat",
        lower_col="mean_gap_ci_lower",
        upper_col="mean_gap_ci_upper",
        title="sample_3x3 Augmented: Mean Gap to CP-SAT with 95% CI",
        y_label="Mean gap to CP-SAT",
        output_path=gap_output
    )

    print()
    print("Saved figures:")
    print(feasibility_output)
    print(cost_output)
    print(gap_output)


if __name__ == "__main__":
    main()
