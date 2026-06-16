import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd


def file_status(path):
    return "FOUND" if path.exists() else "MISSING"


def relative(path):
    return str(path.relative_to(PROJECT_ROOT))


def main():
    results_dir = PROJECT_ROOT / "results"
    tables_dir = results_dir / "tables"
    figures_dir = results_dir / "figures"

    manifest_path = results_dir / "sample_3x3_augmented_result_manifest.md"

    files = {
        "Input and augmented instance": [
            PROJECT_ROOT / "data" / "benchmarks" / "jsplib" / "sample_3x3.txt",
            PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026.json",
            PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026_time_indexed.json",
        ],
        "QUBO validation": [
            tables_dir / "sample_3x3_augmented_qubo_validation.csv",
        ],
        "CP-SAT baseline": [
            tables_dir / "sample_3x3_augmented_cpsat_result.csv",
        ],
        "Random-bit simulated annealing": [
            tables_dir / "sample_3x3_augmented_sa_results.csv",
        ],
        "Structure-aware seeded search": [
            tables_dir / "sample_3x3_augmented_seeded_search_results.csv",
            tables_dir / "sample_3x3_augmented_seeded_search_summary.csv",
        ],
        "Solver comparison summaries": [
            tables_dir / "sample_3x3_augmented_solver_summary.csv",
            tables_dir / "sample_3x3_augmented_search_method_comparison.csv",
        ],
        "Statistical analysis": [
            tables_dir / "sample_3x3_search_statistical_analysis.csv",
            tables_dir / "sample_3x3_search_cost_summary_with_ci.csv",
            tables_dir / "sample_3x3_search_continuous_effect_sizes.csv",
        ],
        "Figures": [
            figures_dir / "sample_3x3_search_feasibility_rate.png",
            figures_dir / "sample_3x3_search_best_feasible_cost.png",
            figures_dir / "sample_3x3_search_best_gap_to_cpsat.png",
            figures_dir / "sample_3x3_search_feasibility_rate_ci.png",
            figures_dir / "sample_3x3_search_mean_feasible_cost_ci.png",
            figures_dir / "sample_3x3_search_mean_gap_to_cpsat_ci.png",
        ],
    }

    solver_summary_path = tables_dir / "sample_3x3_augmented_solver_summary.csv"
    search_comparison_path = tables_dir / "sample_3x3_augmented_search_method_comparison.csv"
    stats_path = tables_dir / "sample_3x3_search_statistical_analysis.csv"
    cost_ci_path = tables_dir / "sample_3x3_search_cost_summary_with_ci.csv"

    solver_summary = None
    search_comparison = None
    stats_df = None
    cost_ci_df = None

    if solver_summary_path.exists():
        solver_summary = pd.read_csv(solver_summary_path)

    if search_comparison_path.exists():
        search_comparison = pd.read_csv(search_comparison_path)

    if stats_path.exists():
        stats_df = pd.read_csv(stats_path)

    if cost_ci_path.exists():
        cost_ci_df = pd.read_csv(cost_ci_path)

    lines = []

    lines.append("# sample_3x3 Augmented Result Manifest")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This manifest summarizes the first benchmark-derived human-centered "
        "time-indexed scheduling experiment. The base instance is a small "
        "JSPLib-style 3-job, 3-machine sample instance. Synthetic human-centered "
        "attributes were added to support computational benchmarking of a "
        "human-centered QUBO/Ising scheduling formulation."
    )
    lines.append("")

    lines.append("## Instance Summary")
    lines.append("")
    lines.append("- Base format: JSPLib-style job-shop scheduling")
    lines.append("- Jobs: 3")
    lines.append("- Machines: 3")
    lines.append("- Operations: 9")
    lines.append("- Human workers: 2")
    lines.append("- Robot resources: 1")
    lines.append("- Total resources: 6")
    lines.append("- Planning horizon: 34")
    lines.append("- Time slots: 34")
    lines.append("- Binary variables: 1836")
    lines.append("- Decision variable: x[o, r, t] = 1 if operation o starts on resource r at time t")
    lines.append("")

    lines.append("## Generated Files")
    lines.append("")

    for category, paths in files.items():
        lines.append(f"### {category}")
        lines.append("")
        lines.append("| File | Status |")
        lines.append("|---|---|")

        for path in paths:
            lines.append(f"| `{relative(path)}` | {file_status(path)} |")

        lines.append("")

    if solver_summary is not None:
        lines.append("## Solver Summary")
        lines.append("")
        lines.append("| Solver / solution | Feasible | Violations | Total cost | Gap to CP-SAT | Improvement over handcrafted |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for _, row in solver_summary.iterrows():
            lines.append(
                f"| {row['solver_or_solution']} | {row['feasible']} | "
                f"{row['num_violations']} | {row['total_cost']} | "
                f"{row['gap_to_cpsat']} | {row['improvement_over_handcrafted']} |"
            )

        lines.append("")

    if search_comparison is not None:
        lines.append("## Search Method Comparison")
        lines.append("")
        lines.append("| Method | Reads | Feasible reads | Feasibility rate | Best feasible cost | Best gap to CP-SAT |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for _, row in search_comparison.iterrows():
            lines.append(
                f"| {row['method']} | {row['total_reads']} | "
                f"{row['feasible_reads']} | {row['feasibility_rate']} | "
                f"{row['best_feasible_cost']} | {row['best_gap_to_cpsat']} |"
            )

        lines.append("")

    if stats_df is not None:
        feasibility_df = stats_df[stats_df["analysis_type"] == "feasibility_proportion"]

        lines.append("## Feasibility Rate with 95% Wilson CI")
        lines.append("")
        lines.append("| Method | n | Feasible | Rate | CI lower | CI upper |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for _, row in feasibility_df.iterrows():
            lines.append(
                f"| {row['method']} | {row['n']} | {row['successes']} | "
                f"{row['feasibility_rate']} | {row['ci_lower']} | {row['ci_upper']} |"
            )

        lines.append("")

        effect_df = stats_df[stats_df["analysis_type"] == "feasibility_effect_size"]

        if len(effect_df) > 0:
            lines.append("## Feasibility Effect Sizes")
            lines.append("")
            lines.append("| Comparison | Risk difference | Cohen's h | Odds ratio | Comparison type |")
            lines.append("|---|---:|---:|---:|---|")

            for _, row in effect_df.iterrows():
                lines.append(
                    f"| {row['comparison']} | {row['effect_size_value']} | "
                    f"{row['cohens_h']} | {row['odds_ratio_haldane']} | "
                    f"{row['comparison_type']} |"
                )

            lines.append("")

    if cost_ci_df is not None:
        lines.append("## Feasible Cost and Gap with Bootstrap 95% CI")
        lines.append("")
        lines.append("| Method | n feasible | Best cost | Mean cost | Cost CI lower | Cost CI upper | Mean gap | Gap CI lower | Gap CI upper |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in cost_ci_df.iterrows():
            lines.append(
                f"| {row['method']} | {row['n_feasible']} | "
                f"{row['best_feasible_cost']} | {row['mean_feasible_cost']} | "
                f"{row['mean_cost_ci_lower']} | {row['mean_cost_ci_upper']} | "
                f"{row['mean_gap_to_cpsat']} | {row['mean_gap_ci_lower']} | "
                f"{row['mean_gap_ci_upper']} |"
            )

        lines.append("")

    lines.append("## Key Findings")
    lines.append("")
    lines.append("- CP-SAT found an optimal feasible solution with total cost 31.8.")
    lines.append("- The handcrafted feasible schedule had total cost 34.2.")
    lines.append("- CP-SAT improved the handcrafted schedule by 2.4 cost units, approximately 7.02%.")
    lines.append("- Random-bit simulated annealing found no feasible solutions across 200 reads.")
    lines.append("- Structure-aware seeded search from the handcrafted schedule achieved 100% feasibility and improved the handcrafted solution to best cost 33.4.")
    lines.append("- Structure-aware seeded search from the CP-SAT solution achieved best cost 31.8, but should be interpreted as a warm-start ablation rather than a fair main comparison.")
    lines.append("- The main methodological finding is that operation-level structure-aware moves are far more suitable than arbitrary bit flips for large time-indexed QUBO scheduling models.")
    lines.append("")

    lines.append("## Current Status")
    lines.append("")
    lines.append("Completed benchmark-derived sample_3x3 pipeline:")
    lines.append("")
    lines.append("- JSPLib-style parser")
    lines.append("- Synthetic human-centered augmentation")
    lines.append("- Time-indexed adapter")
    lines.append("- Generalized time-indexed evaluator")
    lines.append("- Generalized QUBO validation")
    lines.append("- CP-SAT classical baseline")
    lines.append("- Random-bit simulated annealing baseline")
    lines.append("- Structure-aware seeded local search")
    lines.append("- Solver comparison table")
    lines.append("- Statistical analysis with confidence intervals and effect sizes")
    lines.append("- CI/error-bar figures")
    lines.append("")

    lines.append("## Recommended Next Step")
    lines.append("")
    lines.append(
        "The next recommended step is to repeat this benchmark-derived pipeline "
        "on additional small instances with different sizes, resource mixes, and "
        "human-centered augmentation seeds. This will allow analysis of robustness "
        "across instance structure, constraint density, and human-centered attribute distributions."
    )
    lines.append("")

    manifest_text = "\n".join(lines)

    manifest_path.write_text(manifest_text)

    print("Saved sample_3x3 augmented result manifest to:", manifest_path)


if __name__ == "__main__":
    main()
