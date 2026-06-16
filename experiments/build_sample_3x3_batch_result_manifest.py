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
    data_dir = PROJECT_ROOT / "data" / "augmented" / "batch"

    manifest_path = results_dir / "sample_3x3_batch_result_manifest.md"

    files = {
        "Batch generated instances": sorted(data_dir.glob("sample_3x3_hc_seed*_time_indexed.json")),
        "Batch instance summary": [
            tables_dir / "sample_3x3_augmented_batch_instance_summary.csv",
        ],
        "Batch CP-SAT baseline": [
            tables_dir / "sample_3x3_augmented_batch_cpsat_results.csv",
            tables_dir / "sample_3x3_batch_cpsat_distribution_summary.csv",
        ],
        "Batch seeded search": [
            tables_dir / "sample_3x3_augmented_batch_seeded_search_results.csv",
            tables_dir / "sample_3x3_augmented_batch_seeded_search_summary.csv",
        ],
        "Batch statistical analysis": [
            tables_dir / "sample_3x3_batch_search_statistical_summary.csv",
            tables_dir / "sample_3x3_batch_search_effect_sizes.csv",
            tables_dir / "sample_3x3_batch_search_hypothesis_tests.csv",
        ],
        "Batch figures": [
            figures_dir / "sample_3x3_batch_feasibility_rate_ci.png",
            figures_dir / "sample_3x3_batch_mean_gap_to_cpsat_ci.png",
            figures_dir / "sample_3x3_batch_best_gap_to_cpsat_ci.png",
        ],
    }

    instance_summary_path = tables_dir / "sample_3x3_augmented_batch_instance_summary.csv"
    cpsat_results_path = tables_dir / "sample_3x3_augmented_batch_cpsat_results.csv"
    cpsat_distribution_path = tables_dir / "sample_3x3_batch_cpsat_distribution_summary.csv"
    search_summary_path = tables_dir / "sample_3x3_batch_search_statistical_summary.csv"
    effect_sizes_path = tables_dir / "sample_3x3_batch_search_effect_sizes.csv"
    hypothesis_tests_path = tables_dir / "sample_3x3_batch_search_hypothesis_tests.csv"

    instance_summary = pd.read_csv(instance_summary_path) if instance_summary_path.exists() else None
    cpsat_results = pd.read_csv(cpsat_results_path, dtype={"bitstring": str}) if cpsat_results_path.exists() else None
    cpsat_distribution = pd.read_csv(cpsat_distribution_path) if cpsat_distribution_path.exists() else None
    search_summary = pd.read_csv(search_summary_path) if search_summary_path.exists() else None
    effect_sizes = pd.read_csv(effect_sizes_path) if effect_sizes_path.exists() else None
    hypothesis_tests = pd.read_csv(hypothesis_tests_path) if hypothesis_tests_path.exists() else None

    lines = []

    lines.append("# sample_3x3 Batch Result Manifest")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This manifest summarizes a batch pilot experiment using 10 synthetic "
        "human-centered augmentations of the sample_3x3 JSPLib-style instance. "
        "The purpose is not to claim final paper-level results, but to verify that "
        "the benchmark augmentation, CP-SAT baseline, structure-aware search, "
        "statistical analysis, multiple-comparison correction, and visualization "
        "pipeline can be executed repeatedly across augmentation seeds."
    )
    lines.append("")

    lines.append("## Batch Design")
    lines.append("")
    lines.append("- Base instance: sample_3x3 JSPLib-style job-shop instance")
    lines.append("- Augmentation seeds: 1001–1010")
    lines.append("- Number of augmented instances: 10")
    lines.append("- Machines: 3")
    lines.append("- Human workers: 2")
    lines.append("- Robot resources: 1")
    lines.append("- Total resources: 6")
    lines.append("- Main baseline: CP-SAT")
    lines.append("- Heuristic search methods:")
    lines.append("  - structure-aware random-seed local search")
    lines.append("  - structure-aware CP-SAT-seeded warm-start search")
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

    if instance_summary is not None:
        lines.append("## Batch Instance Summary")
        lines.append("")
        lines.append("| Seed | Horizon | Binary variables | Compatible assignments | Worker-compatible | Robot-compatible | Avg workload | Avg ergonomic | Avg safety |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in instance_summary.iterrows():
            lines.append(
                f"| {int(row['seed'])} | {int(row['planning_horizon'])} | "
                f"{int(row['num_binary_variables'])} | "
                f"{int(row['total_compatible_assignments'])} | "
                f"{int(row['worker_compatible_assignments'])} | "
                f"{int(row['robot_compatible_assignments'])} | "
                f"{row['avg_workload']} | {row['avg_ergonomic_risk']} | "
                f"{row['avg_safety_risk']} |"
            )

        lines.append("")

    if cpsat_distribution is not None:
        row = cpsat_distribution.iloc[0]

        lines.append("## CP-SAT Distribution Summary")
        lines.append("")
        lines.append(f"- Number of instances: {int(row['num_instances'])}")
        lines.append(f"- Number optimal: {int(row['num_optimal'])}")
        lines.append(f"- Number feasible: {int(row['num_feasible'])}")
        lines.append(f"- Mean total cost: {row['mean_total_cost']}")
        lines.append(f"- 95% bootstrap CI for mean total cost: [{row['mean_total_cost_ci_lower']}, {row['mean_total_cost_ci_upper']}]")
        lines.append(f"- Min total cost: {row['min_total_cost']}")
        lines.append(f"- Max total cost: {row['max_total_cost']}")
        lines.append(f"- Mean wall time: {row['mean_wall_time']}")
        lines.append("")

    if cpsat_results is not None:
        lines.append("## CP-SAT Seed-Level Results")
        lines.append("")
        lines.append("| Seed | Status | Feasible | Total cost | Processing | Start time | Workload | Ergonomic | Safety | Penalty | Wall time |")
        lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in cpsat_results.iterrows():
            lines.append(
                f"| {int(row['seed'])} | {row['status']} | {row['feasible']} | "
                f"{row['total_cost']} | {row['processing']} | {row['start_time']} | "
                f"{row['workload']} | {row['ergonomic']} | {row['safety']} | "
                f"{row['total_penalty']} | {row['wall_time']} |"
            )

        lines.append("")

    if search_summary is not None:
        lines.append("## Batch Search Statistical Summary")
        lines.append("")
        lines.append("| Search method | Reads | Feasible reads | Feasibility rate | 95% CI lower | 95% CI upper | Mean gap | Mean best gap |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in search_summary.iterrows():
            lines.append(
                f"| {row['search_name']} | {int(row['total_reads'])} | "
                f"{int(row['feasible_reads'])} | {row['feasibility_rate']} | "
                f"{row['feasibility_ci_lower']} | {row['feasibility_ci_upper']} | "
                f"{row['mean_gap_to_cpsat']} | {row['mean_best_gap_to_cpsat_across_instances']} |"
            )

        lines.append("")

    if effect_sizes is not None:
        lines.append("## Effect Sizes")
        lines.append("")
        lines.append("| Comparison | Metric | Group 1 value | Group 2 value | Difference | Effect size details |")
        lines.append("|---|---|---:|---:|---:|---|")

        for _, row in effect_sizes.iterrows():
            details = []

            if "cohens_h" in row and pd.notna(row.get("cohens_h")):
                details.append(f"Cohen's h={row['cohens_h']}")
            if "odds_ratio_haldane" in row and pd.notna(row.get("odds_ratio_haldane")):
                details.append(f"OR={row['odds_ratio_haldane']}")
            if "cohens_d" in row and pd.notna(row.get("cohens_d")):
                details.append(f"Cohen's d={row['cohens_d']}")
            if "cliffs_delta" in row and pd.notna(row.get("cliffs_delta")):
                details.append(f"Cliff's delta={row['cliffs_delta']}")

            lines.append(
                f"| {row['comparison']} | {row['metric']} | "
                f"{row['group1_value']} | {row['group2_value']} | "
                f"{row['difference']} | {'; '.join(details)} |"
            )

        lines.append("")

    if hypothesis_tests is not None:
        lines.append("## Hypothesis Tests with Multiple-Comparison Correction")
        lines.append("")
        lines.append("P-values were adjusted using the Holm-Bonferroni procedure across the batch search-method test family.")
        lines.append("")
        lines.append("| Metric | Test | Statistic | Raw p | Holm-adjusted p | Significant after Holm 0.05 |")
        lines.append("|---|---|---:|---:|---:|---:|")

        for _, row in hypothesis_tests.iterrows():
            lines.append(
                f"| {row['metric']} | {row['test']} | {row['statistic']} | "
                f"{row['raw_p_value']} | {row['holm_adjusted_p_value']} | "
                f"{row['significant_after_holm_0_05']} |"
            )

        lines.append("")

    lines.append("## Key Pilot Findings")
    lines.append("")
    lines.append("- CP-SAT solved all 10 augmented instances to optimality and feasibility.")
    lines.append("- Both structure-aware search methods achieved high feasibility rates.")
    lines.append("- Feasibility differences between structure-aware random-seed and CP-SAT-seed search were not statistically significant after Holm-Bonferroni correction.")
    lines.append("- Gap-to-CP-SAT differences were statistically significant after correction, indicating that seed quality affects solution quality even when feasibility is high.")
    lines.append("- The CP-SAT-seeded search should be interpreted as a warm-start ablation, not as a fair main comparison against random-seed search.")
    lines.append("- The batch pilot supports the methodological idea that operation-level structure-aware moves are more appropriate than arbitrary bit flips for large time-indexed QUBO scheduling search.")
    lines.append("")

    lines.append("## Current Status")
    lines.append("")
    lines.append("Completed batch pilot pipeline:")
    lines.append("")
    lines.append("- Batch synthetic human-centered augmentation")
    lines.append("- Batch time-indexed instance generation")
    lines.append("- Batch CP-SAT baseline")
    lines.append("- Batch structure-aware seeded search")
    lines.append("- Batch statistical summary")
    lines.append("- Effect size analysis")
    lines.append("- Holm-Bonferroni multiple-comparison correction")
    lines.append("- Batch CI/error-bar figures")
    lines.append("")

    lines.append("## Recommended Next Step")
    lines.append("")
    lines.append(
        "The next recommended step is to introduce at least one larger or structurally "
        "different benchmark-derived instance. This will test whether the same "
        "pipeline remains robust as the number of operations, resources, planning "
        "horizon, and constraint density increase."
    )
    lines.append("")

    manifest_text = "\n".join(lines)

    manifest_path.write_text(manifest_text)

    print("Saved batch result manifest to:", manifest_path)


if __name__ == "__main__":
    main()
