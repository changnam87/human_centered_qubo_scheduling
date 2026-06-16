import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt


def shorten_label(label):
    if label == "Random-bit simulated annealing":
        return "Random-bit\nSA"
    if label == "Structure-aware seeded search from handcrafted":
        return "Seeded search\nfrom handcrafted"
    if label == "Structure-aware seeded search from CP-SAT":
        return "Seeded search\nfrom CP-SAT"
    return label


def save_bar_plot(df, x_col, y_col, title, y_label, output_path):
    labels = [shorten_label(x) for x in df[x_col]]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, df[y_col])
    plt.title(title)
    plt.xlabel("Search method")
    plt.ylabel(y_label)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    input_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_search_method_comparison.csv"
    figures_dir = PROJECT_ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print("Missing input file:", input_path)
        print("Please run:")
        print("python experiments/build_sample_3x3_search_method_comparison.py")
        return

    df = pd.read_csv(input_path)

    print("=== sample_3x3 search method comparison plotting ===")
    print("Loaded:", input_path)
    print("Rows:", len(df))

    # plotting copy
    plot_df = df.copy()

    # best_feasible_cost / best_gap_to_cpsat may contain NaN for random SA
    # keep feasibility plot with all rows
    feasibility_path = figures_dir / "sample_3x3_search_feasibility_rate.png"
    save_bar_plot(
        df=plot_df,
        x_col="method",
        y_col="feasibility_rate",
        title="sample_3x3 Augmented: Feasibility Rate by Search Method",
        y_label="Feasibility rate",
        output_path=feasibility_path
    )

    # cost plot only for rows with available best feasible cost
    cost_df = plot_df[plot_df["best_feasible_cost"].notna()].copy()
    best_cost_path = figures_dir / "sample_3x3_search_best_feasible_cost.png"
    save_bar_plot(
        df=cost_df,
        x_col="method",
        y_col="best_feasible_cost",
        title="sample_3x3 Augmented: Best Feasible Cost by Search Method",
        y_label="Best feasible cost",
        output_path=best_cost_path
    )

    # gap plot only for rows with available gap
    gap_df = plot_df[plot_df["best_gap_to_cpsat"].notna()].copy()
    gap_path = figures_dir / "sample_3x3_search_best_gap_to_cpsat.png"
    save_bar_plot(
        df=gap_df,
        x_col="method",
        y_col="best_gap_to_cpsat",
        title="sample_3x3 Augmented: Best Gap to CP-SAT by Search Method",
        y_label="Best gap to CP-SAT",
        output_path=gap_path
    )

    print()
    print("Saved figures:")
    print(feasibility_path)
    print(best_cost_path)
    print(gap_path)


if __name__ == "__main__":
    main()
