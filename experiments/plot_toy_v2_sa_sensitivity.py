import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import matplotlib.pyplot as plt


def shorten_config_name(name):
    """
    Make configuration names shorter for plot labels.
    """
    name = name.replace("steps_", "")
    name = name.replace("_T", "\nT")
    name = name.replace("_to_", "→")
    return name


def save_bar_plot(df, x_col, y_col, title, y_label, output_path):
    """
    Save a simple bar plot.

    Notes:
    - Uses matplotlib only.
    - Does not specify custom colors.
    - One figure per plot.
    """
    labels = [shorten_config_name(x) for x in df[x_col]]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, df[y_col])
    plt.title(title)
    plt.xlabel("SA configuration")
    plt.ylabel(y_label)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    input_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_sa_sensitivity_summary.csv"
    figures_dir = PROJECT_ROOT / "results" / "figures"

    figures_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print("Missing input file:", input_path)
        print("Please run:")
        print("python experiments/run_toy_v2_sa_sensitivity.py")
        return

    df = pd.read_csv(input_path)

    print("=== Toy v2 SA sensitivity figure generation ===")
    print("Loaded:", input_path)
    print("Rows:", len(df))

    # Sort by num_steps first, then temperatures for readability
    df = df.sort_values(
        ["num_steps", "initial_temperature", "final_temperature"],
        ascending=[True, True, True]
    )

    feasibility_path = figures_dir / "toy_v2_sa_feasibility_rate.png"
    zero_penalty_path = figures_dir / "toy_v2_sa_zero_penalty_rate.png"
    mean_energy_path = figures_dir / "toy_v2_sa_mean_energy.png"

    save_bar_plot(
        df=df,
        x_col="config_name",
        y_col="feasibility_rate",
        title="Toy v2 SA Feasibility Rate by Configuration",
        y_label="Feasibility rate",
        output_path=feasibility_path
    )

    save_bar_plot(
        df=df,
        x_col="config_name",
        y_col="zero_penalty_rate",
        title="Toy v2 SA Zero-Penalty Rate by Configuration",
        y_label="Zero-penalty rate",
        output_path=zero_penalty_path
    )

    save_bar_plot(
        df=df,
        x_col="config_name",
        y_col="mean_energy",
        title="Toy v2 SA Mean Energy by Configuration",
        y_label="Mean energy",
        output_path=mean_energy_path
    )

    print()
    print("Saved figures:")
    print(feasibility_path)
    print(zero_penalty_path)
    print(mean_energy_path)


if __name__ == "__main__":
    main()
