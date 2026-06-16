import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt


def shorten_label(name):
    if name == "structure_aware_random_seed":
        return "Structure-aware\nrandom seed"
    if name == "structure_aware_cpsat_seed":
        return "Structure-aware\nCP-SAT seed"
    return name


def save_bar_with_ci(df, x_col, y_col, lower_col, upper_col, title, ylabel, output_path):
    labels = [shorten_label(x) for x in df[x_col]]

    y = df[y_col].astype(float)
    lower = df[lower_col].astype(float)
    upper = df[upper_col].astype(float)

    yerr_lower = y - lower
    yerr_upper = upper - y

    plt.figure(figsize=(8, 6))
    plt.bar(labels, y, yerr=[yerr_lower, yerr_upper], capsize=6)
    plt.title(title)
    plt.xlabel("Search method")
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"
    figures_dir = PROJECT_ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    summary_path = tables_dir / "sample_3x3_batch_search_statistical_summary.csv"

    if not summary_path.exists():
        print("Missing:", summary_path)
        print("Run this first:")
        print("python experiments/analyze_sample_3x3_batch_search_statistics.py")
        return

    df = pd.read_csv(summary_path)

    print("=== Plotting batch search statistics ===")
    print("Loaded:", summary_path)
    print("Rows:", len(df))

    # Consistent order
    order = {
        "structure_aware_random_seed": 0,
        "structure_aware_cpsat_seed": 1
    }

    df["order"] = df["search_name"].map(order)
    df = df.sort_values("order")

    feasibility_path = figures_dir / "sample_3x3_batch_feasibility_rate_ci.png"
    mean_gap_path = figures_dir / "sample_3x3_batch_mean_gap_to_cpsat_ci.png"
    best_gap_path = figures_dir / "sample_3x3_batch_best_gap_to_cpsat_ci.png"

    save_bar_with_ci(
        df=df,
        x_col="search_name",
        y_col="feasibility_rate",
        lower_col="feasibility_ci_lower",
        upper_col="feasibility_ci_upper",
        title="Batch sample_3x3: Feasibility Rate with 95% CI",
        ylabel="Feasibility rate",
        output_path=feasibility_path
    )

    save_bar_with_ci(
        df=df,
        x_col="search_name",
        y_col="mean_gap_to_cpsat",
        lower_col="mean_gap_ci_lower",
        upper_col="mean_gap_ci_upper",
        title="Batch sample_3x3: Mean Gap to CP-SAT with 95% CI",
        ylabel="Mean gap to CP-SAT",
        output_path=mean_gap_path
    )

    save_bar_with_ci(
        df=df,
        x_col="search_name",
        y_col="mean_best_gap_to_cpsat_across_instances",
        lower_col="best_gap_ci_lower",
        upper_col="best_gap_ci_upper",
        title="Batch sample_3x3: Mean Best Gap to CP-SAT with 95% CI",
        ylabel="Mean best gap to CP-SAT",
        output_path=best_gap_path
    )

    print()
    print("Saved figures:")
    print(feasibility_path)
    print(mean_gap_path)
    print(best_gap_path)


if __name__ == "__main__":
    main()
