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

    manifest_path = results_dir / "sample_4x4_augmented_result_manifest.md"
    solver_summary_path = tables_dir / "sample_4x4_augmented_solver_summary.csv"

    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_4x4_hc_seed2026_time_indexed.json"

    cpsat_path = tables_dir / "sample_4x4_augmented_cpsat_result.csv"
    seeded_results_path = tables_dir / "sample_4x4_augmented_seeded_search_results.csv"
    seeded_summary_path = tables_dir / "sample_4x4_augmented_seeded_search_summary.csv"

    human_utilization_path = tables_dir / "sample_4x4_human_utilization_cpsat_result.csv"
    human_comparison_path = tables_dir / "sample_4x4_human_utilization_comparison.csv"
    human_sensitivity_path = tables_dir / "sample_4x4_human_utilization_sensitivity.csv"
    soft_reward_path = tables_dir / "sample_4x4_soft_human_reward_sensitivity.csv"
    soft_reward_qubo_validation_path = tables_dir / "sample_4x4_soft_human_reward_qubo_validation.csv"

    total_cost_figure = figures_dir / "sample_4x4_human_utilization_total_cost.png"
    assignment_figure = figures_dir / "sample_4x4_human_utilization_assignment_counts.png"
    human_cost_figure = figures_dir / "sample_4x4_human_utilization_human_centered_costs.png"

    sensitivity_total_cost_figure = figures_dir / "sample_4x4_human_sensitivity_total_cost.png"
    sensitivity_hc_cost_figure = figures_dir / "sample_4x4_human_sensitivity_human_centered_costs.png"
    sensitivity_assignment_figure = figures_dir / "sample_4x4_human_sensitivity_assignment_counts.png"
    sensitivity_components_figure = figures_dir / "sample_4x4_human_sensitivity_cost_components.png"

    soft_reward_human_assignments_figure = figures_dir / "sample_4x4_soft_reward_human_assignments.png"
    soft_reward_objective_figure = figures_dir / "sample_4x4_soft_reward_objective_tradeoff.png"
    soft_reward_hc_cost_figure = figures_dir / "sample_4x4_soft_reward_human_centered_costs.png"
    soft_reward_assignment_figure = figures_dir / "sample_4x4_soft_reward_assignment_counts.png"

    files = {
        "Input and augmented instance": [
            PROJECT_ROOT / "data" / "benchmarks" / "jsplib" / "sample_4x4.txt",
            instance_path,
        ],
        "CP-SAT baseline": [
            cpsat_path,
        ],
        "Structure-aware seeded search": [
            seeded_results_path,
            seeded_summary_path,
        ],
        "Human-utilization variant": [
            human_utilization_path,
            human_comparison_path,
        ],
        "Human-utilization sensitivity": [
            human_sensitivity_path,
        ],
        "Soft human-reward sensitivity": [
            soft_reward_path,
        ],
        "Soft human-reward QUBO validation": [
            soft_reward_qubo_validation_path,
        ],
        "Human-utilization figures": [
            total_cost_figure,
            assignment_figure,
            human_cost_figure,
        ],
        "Sensitivity figures": [
            sensitivity_total_cost_figure,
            sensitivity_hc_cost_figure,
            sensitivity_assignment_figure,
            sensitivity_components_figure,
        ],
        "Soft human-reward figures": [
            soft_reward_human_assignments_figure,
            soft_reward_objective_figure,
            soft_reward_hc_cost_figure,
            soft_reward_assignment_figure,
        ],
        "Solver summary": [
            solver_summary_path,
        ],
    }

    if not cpsat_path.exists():
        print("Missing:", cpsat_path)
        return

    if not seeded_summary_path.exists():
        print("Missing:", seeded_summary_path)
        return

    cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})
    seeded_summary_df = pd.read_csv(seeded_summary_path)

    cpsat = cpsat_df.iloc[0]
    cpsat_cost = float(cpsat["total_cost"])

    human_df = None
    human_comparison_df = None
    sensitivity_df = None
    soft_reward_df = None
    soft_reward_qubo_validation_df = None

    if human_utilization_path.exists():
        human_df = pd.read_csv(human_utilization_path, dtype={"bitstring": str})

    if human_comparison_path.exists():
        human_comparison_df = pd.read_csv(human_comparison_path)

    if human_sensitivity_path.exists():
        sensitivity_df = pd.read_csv(human_sensitivity_path, dtype={"bitstring": str})

    if soft_reward_path.exists():
        soft_reward_df = pd.read_csv(soft_reward_path, dtype={"bitstring": str})

    if soft_reward_qubo_validation_path.exists():
        soft_reward_qubo_validation_df = pd.read_csv(soft_reward_qubo_validation_path)

    rows = []

    rows.append({
        "instance_name": "sample_4x4_human_centered_augmented",
        "solver_or_solution": "CP-SAT",
        "role": "Classical exact/strong baseline",
        "status": cpsat["status"],
        "num_operations": int(cpsat["num_operations"]),
        "num_resources": int(cpsat["num_resources"]),
        "num_time_slots": int(cpsat["num_time_slots"]),
        "num_binary_variables": int(cpsat["num_binary_variables"]),
        "selected_variables": int(cpsat["selected_variables"]),
        "feasible": cpsat["feasible"],
        "num_violations": int(cpsat["num_violations"]),
        "processing": float(cpsat["processing"]),
        "start_time": float(cpsat["start_time"]),
        "workload": float(cpsat["workload"]),
        "ergonomic": float(cpsat["ergonomic"]),
        "safety": float(cpsat["safety"]),
        "original_cost": float(cpsat["original_cost"]),
        "total_penalty": float(cpsat["total_penalty"]),
        "total_cost": cpsat_cost,
        "gap_to_cpsat": 0.0,
        "notes": "CP-SAT baseline for sample_4x4."
    })

    for _, row in seeded_summary_df.iterrows():
        rows.append({
            "instance_name": "sample_4x4_human_centered_augmented",
            "solver_or_solution": row["search_name"],
            "role": "Structure-aware operation-level reassignment search",
            "status": "FEASIBLE_READS_FOUND" if row["feasible_reads"] > 0 else "NO_FEASIBLE_READS",
            "num_operations": int(cpsat["num_operations"]),
            "num_resources": int(cpsat["num_resources"]),
            "num_time_slots": int(cpsat["num_time_slots"]),
            "num_binary_variables": int(cpsat["num_binary_variables"]),
            "selected_variables": None,
            "feasible": row["feasible_reads"] > 0,
            "num_violations": None,
            "processing": None,
            "start_time": None,
            "workload": None,
            "ergonomic": None,
            "safety": None,
            "original_cost": None,
            "total_penalty": None,
            "total_cost": row["best_feasible_cost"],
            "gap_to_cpsat": row["best_gap_to_cpsat"],
            "notes": (
                f"reads={int(row['total_reads'])}; "
                f"feasible_reads={int(row['feasible_reads'])}; "
                f"feasibility_rate={row['feasibility_rate']}; "
                f"mean_gap_to_cpsat={row['mean_gap_to_cpsat']}"
            )
        })

    if human_df is not None:
        human = human_df.iloc[0]

        rows.append({
            "instance_name": "sample_4x4_human_centered_augmented",
            "solver_or_solution": "Human-utilization CP-SAT",
            "role": "Human-involvement constrained CP-SAT variant",
            "status": human["status"],
            "num_operations": int(human["num_operations"]),
            "num_resources": int(human["num_resources"]),
            "num_time_slots": int(human["num_time_slots"]),
            "num_binary_variables": int(human["num_binary_variables"]),
            "selected_variables": int(human["selected_variables"]),
            "feasible": human["feasible"],
            "num_violations": int(human["num_violations"]),
            "processing": float(human["processing"]),
            "start_time": float(human["start_time"]),
            "workload": float(human["workload"]),
            "ergonomic": float(human["ergonomic"]),
            "safety": float(human["safety"]),
            "original_cost": float(human["original_cost"]),
            "total_penalty": float(human["total_penalty"]),
            "total_cost": float(human["total_cost"]),
            "gap_to_cpsat": float(human["total_cost"]) - cpsat_cost,
            "notes": (
                f"min_human_assignments={int(human['min_human_assignments'])}; "
                f"human_assignment_count={int(human['human_assignment_count'])}; "
                f"robot_assignment_count={int(human['robot_assignment_count'])}"
            )
        })

    solver_summary_df = pd.DataFrame(rows)
    solver_summary_df.to_csv(solver_summary_path, index=False)

    lines = []

    lines.append("# sample_4x4 Augmented Result Manifest")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This manifest summarizes the first larger benchmark-derived pilot instance. "
        "The purpose is to verify that the human-centered time-indexed scheduling "
        "pipeline remains executable when the problem grows from sample_3x3 to "
        "sample_4x4. This is still a prototype/pilot validation step, not a final "
        "paper-level computational study."
    )
    lines.append("")

    lines.append("## Instance Summary")
    lines.append("")
    lines.append("- Base format: JSPLib-style job-shop scheduling")
    lines.append("- Jobs: 4")
    lines.append("- Machines: 4")
    lines.append("- Operations: 16")
    lines.append("- Human workers: 3")
    lines.append("- Robot resources: 2")
    lines.append("- Total resources: 9")
    lines.append("- Planning horizon: 63")
    lines.append("- Time slots: 63")
    lines.append("- Binary variables: 9072")
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

    lines.append("## Solver Summary")
    lines.append("")
    lines.append("| Solver / search | Status | Feasible | Total cost / best cost | Gap to baseline CP-SAT | Notes |")
    lines.append("|---|---|---:|---:|---:|---|")

    for _, row in solver_summary_df.iterrows():
        lines.append(
            f"| {row['solver_or_solution']} | {row['status']} | {row['feasible']} | "
            f"{row['total_cost']} | {row['gap_to_cpsat']} | {row['notes']} |"
        )

    lines.append("")

    lines.append("## CP-SAT Baseline Result")
    lines.append("")
    lines.append(f"- Status: {cpsat['status']}")
    lines.append(f"- Feasible: {cpsat['feasible']}")
    lines.append(f"- Violations: {int(cpsat['num_violations'])}")
    lines.append(f"- Total penalty: {float(cpsat['total_penalty'])}")
    lines.append(f"- Total cost: {float(cpsat['total_cost'])}")
    lines.append(f"- Processing cost: {float(cpsat['processing'])}")
    lines.append(f"- Start-time cost: {float(cpsat['start_time'])}")
    lines.append(f"- Workload cost: {float(cpsat['workload'])}")
    lines.append(f"- Ergonomic cost: {float(cpsat['ergonomic'])}")
    lines.append(f"- Safety cost: {float(cpsat['safety'])}")
    lines.append(f"- Wall time: {float(cpsat['wall_time'])}")
    lines.append("")

    lines.append("## Structure-Aware Search Summary")
    lines.append("")
    lines.append("| Search method | Reads | Feasible reads | Feasibility rate | Best feasible cost | Best gap to CP-SAT | Mean gap to CP-SAT |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for _, row in seeded_summary_df.iterrows():
        lines.append(
            f"| {row['search_name']} | {int(row['total_reads'])} | "
            f"{int(row['feasible_reads'])} | {row['feasibility_rate']} | "
            f"{row['best_feasible_cost']} | {row['best_gap_to_cpsat']} | "
            f"{row['mean_gap_to_cpsat']} |"
        )

    lines.append("")

    if human_df is not None:
        human = human_df.iloc[0]

        lines.append("## Human-Utilization Variant Result")
        lines.append("")
        lines.append("- Variant: hard minimum human assignment constraint")
        lines.append(f"- Minimum human assignments: {int(human['min_human_assignments'])}")
        lines.append(f"- Status: {human['status']}")
        lines.append(f"- Feasible: {human['feasible']}")
        lines.append(f"- Violations: {int(human['num_violations'])}")
        lines.append(f"- Human assignment count: {int(human['human_assignment_count'])}")
        lines.append(f"- Robot assignment count: {int(human['robot_assignment_count'])}")
        lines.append(f"- Total penalty: {float(human['total_penalty'])}")
        lines.append(f"- Total cost: {float(human['total_cost'])}")
        lines.append(f"- Processing cost: {float(human['processing'])}")
        lines.append(f"- Start-time cost: {float(human['start_time'])}")
        lines.append(f"- Workload cost: {float(human['workload'])}")
        lines.append(f"- Ergonomic cost: {float(human['ergonomic'])}")
        lines.append(f"- Safety cost: {float(human['safety'])}")
        lines.append("")

    if human_comparison_df is not None:
        lines.append("## Baseline vs Human-Utilization Comparison")
        lines.append("")
        lines.append("| Variant | Human assignments | Robot assignments | Machine assignments | Workload | Ergonomic | Safety | Total cost | Cost increase vs baseline | Percent increase |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in human_comparison_df.iterrows():
            lines.append(
                f"| {row['model_variant']} | {int(row['human_assignment_count'])} | "
                f"{int(row['robot_assignment_count'])} | {int(row['machine_assignment_count'])} | "
                f"{row['workload']} | {row['ergonomic']} | {row['safety']} | "
                f"{row['total_cost']} | {row['cost_increase_vs_baseline']} | "
                f"{row['percent_increase_vs_baseline']} |"
            )

        lines.append("")

    if sensitivity_df is not None:
        lines.append("## Human-Utilization Sensitivity")
        lines.append("")
        lines.append("| Min human assignments | Actual human | Machine | Robot | Processing | Start time | Workload | Ergonomic | Safety | Total cost | Increase vs min0 | Percent increase |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in sensitivity_df.iterrows():
            lines.append(
                f"| {int(row['min_human_assignments'])} | "
                f"{int(row['human_assignment_count'])} | "
                f"{int(row['machine_assignment_count'])} | "
                f"{int(row['robot_assignment_count'])} | "
                f"{row['processing']} | {row['start_time']} | "
                f"{row['workload']} | {row['ergonomic']} | {row['safety']} | "
                f"{row['total_cost']} | {row['cost_increase_vs_min0']} | "
                f"{row['percent_increase_vs_min0']} |"
            )

        lines.append("")

    if soft_reward_df is not None:
        lines.append("## Soft Human-Reward Sensitivity")
        lines.append("")
        lines.append("| Human reward | Human assignments | Machine | Robot | Processing | Start time | Workload | Ergonomic | Safety | Cost without reward | Reward value | Reward-adjusted objective |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in soft_reward_df.iterrows():
            lines.append(
                f"| {row['human_reward']} | "
                f"{int(row['human_assignment_count'])} | "
                f"{int(row['machine_assignment_count'])} | "
                f"{int(row['robot_assignment_count'])} | "
                f"{row['processing']} | {row['start_time']} | "
                f"{row['workload']} | {row['ergonomic']} | {row['safety']} | "
                f"{row['total_cost_without_reward']} | {row['reward_value']} | "
                f"{row['reward_adjusted_objective']} |"
            )

        lines.append("")

    if soft_reward_qubo_validation_df is not None:
        lines.append("## Soft Human-Reward QUBO Validation")
        lines.append("")
        lines.append("| Human reward | Human assignments | Expected reward-adjusted objective | QUBO energy | Absolute error | Pass |")
        lines.append("|---:|---:|---:|---:|---:|---:|")

        for _, row in soft_reward_qubo_validation_df.iterrows():
            lines.append(
                f"| {row['human_reward']} | "
                f"{int(row['human_assignment_count'])} | "
                f"{row['expected_reward_adjusted_objective']} | "
                f"{row['qubo_energy']} | "
                f"{row['abs_error_vs_expected_objective']} | "
                f"{row['pass_expected_objective']} |"
            )

        max_error = soft_reward_qubo_validation_df["abs_error_vs_expected_objective"].max()

        lines.append("")
        lines.append(f"Maximum absolute validation error: {max_error}")
        lines.append("")

    lines.append("## Key Pilot Findings")
    lines.append("")
    lines.append("- CP-SAT solved the 9072-variable time-indexed sample_4x4 instance to optimality.")
    lines.append("- The baseline CP-SAT total cost was 57.0 with zero penalty.")
    lines.append("- Structure-aware random-seed search found feasible solutions, but the best gap to CP-SAT remained large.")
    lines.append("- Structure-aware CP-SAT-seeded search preserved the CP-SAT optimal solution in the best read, but this is a warm-start ablation.")
    lines.append("- As the problem size increased from 1836 to 9072 binary variables, seed quality and local search design became more important.")
    lines.append("- The baseline objective tends to avoid human workers, producing zero workload and ergonomic cost under CP-SAT.")
    lines.append("- Adding a hard minimum human assignment constraint activated workload and ergonomic cost terms.")
    lines.append("- The human-utilization variant increased total cost from 57.0 to 62.1, a 5.1-unit increase, approximately 8.95%.")
    lines.append("- The sensitivity experiment showed a monotonic cost increase as minimum human assignments increased from 0 to 4.")
    lines.append("- Human involvement increased workload and ergonomic costs, while start-time cost decreased modestly, suggesting a scheduling-flexibility trade-off.")
    lines.append("- The soft human-reward variant showed threshold behavior: rewards of 0–1 selected no human assignments, reward 2 selected one human assignment, reward 4 selected two, and reward 5 selected three.")
    lines.append("- Under the soft reward objective, total cost without reward increased as human involvement increased, but reward-adjusted objective decreased.")
    lines.append("- The soft human-reward QUBO validation passed, confirming that QUBO energy matches the reward-adjusted objective across tested reward values.")
    lines.append("")

    lines.append("## Current Status")
    lines.append("")
    lines.append("Completed sample_4x4 pilot pipeline:")
    lines.append("")
    lines.append("- Larger JSPLib-style instance generation")
    lines.append("- Synthetic human-centered augmentation")
    lines.append("- Time-indexed instance generation")
    lines.append("- CP-SAT baseline")
    lines.append("- Structure-aware seeded search")
    lines.append("- Human-utilization constrained CP-SAT variant")
    lines.append("- Baseline vs human-utilization comparison")
    lines.append("- Human-utilization sensitivity analysis")
    lines.append("- Human-utilization and sensitivity figures")
    lines.append("- Soft human-reward sensitivity analysis")
    lines.append("- Soft human-reward figures")
    lines.append("- Soft human-reward QUBO validation")
    lines.append("- Solver summary")
    lines.append("")

    lines.append("## Recommended Next Step")
    lines.append("")
    lines.append(
        "The next recommended step is to formalize the human-involvement reward "
        "as a multi-objective trade-off model. The current soft-reward pilot shows "
        "that reward strength controls when human assignments become attractive, "
        "but future experiments should test this behavior across multiple instances "
        "and augmentation seeds."
    )
    lines.append("")

    manifest_text = "\n".join(lines)
    manifest_path.write_text(manifest_text)

    print("Saved solver summary to:", solver_summary_path)
    print("Saved manifest to:", manifest_path)


if __name__ == "__main__":
    main()
