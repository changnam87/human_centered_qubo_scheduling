import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd


def file_status(path):
    if path.exists():
        return "FOUND"
    return "MISSING"


def relative(path):
    return str(path.relative_to(PROJECT_ROOT))


def main():
    results_dir = PROJECT_ROOT / "results"
    tables_dir = results_dir / "tables"
    figures_dir = results_dir / "figures"

    manifest_path = results_dir / "toy_v2_result_manifest.md"

    files = {
        "Instance": [
            PROJECT_ROOT / "data" / "toy" / "toy_v2_time_indexed.json"
        ],
        "QUBO validation": [
            tables_dir / "toy_v2_Q_matrix.csv",
            tables_dir / "toy_v2_qubo_validation.csv"
        ],
        "Ising validation": [
            tables_dir / "toy_v2_ising_h.csv",
            tables_dir / "toy_v2_ising_J.csv",
            tables_dir / "toy_v2_ising_validation.csv"
        ],
        "Simulated annealing": [
            tables_dir / "toy_v2_simulated_annealing_results.csv",
            tables_dir / "toy_v2_sa_sensitivity_summary.csv",
            tables_dir / "toy_v2_sa_sensitivity_reads.csv"
        ],
        "Benchmark summary": [
            tables_dir / "toy_v2_solver_benchmark_summary.csv"
        ],
        "CP-SAT baseline": [
            tables_dir / "toy_v2_cpsat_result.csv"
        ],
        "Figures": [
            figures_dir / "toy_v2_sa_feasibility_rate.png",
            figures_dir / "toy_v2_sa_zero_penalty_rate.png",
            figures_dir / "toy_v2_sa_mean_energy.png"
        ]
    }

    summary_path = tables_dir / "toy_v2_solver_benchmark_summary.csv"
    sa_sensitivity_path = tables_dir / "toy_v2_sa_sensitivity_summary.csv"

    benchmark_summary = None
    sa_summary = None

    if summary_path.exists():
        benchmark_summary = pd.read_csv(summary_path)

    if sa_sensitivity_path.exists():
        sa_summary = pd.read_csv(sa_sensitivity_path)

    lines = []

    lines.append("# Toy v2 Result Manifest")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This manifest summarizes the Toy v2 time-indexed human-centered scheduling "
        "experiment. Toy v2 extends the assignment-only Toy v1 model by adding start "
        "times, precedence constraints, resource-overlap constraints, horizon checks, "
        "and time-indexed QUBO/Ising representations."
    )
    lines.append("")

    lines.append("## Toy v2 Model")
    lines.append("")
    lines.append("- Operations: 4")
    lines.append("- Resources: 3")
    lines.append("- Time slots: 6")
    lines.append("- Binary variables: 72")
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

    if benchmark_summary is not None:
        lines.append("## Solver Benchmark Summary")
        lines.append("")
        lines.append("| Component | Best energy/cost | Reference cost | Feasibility rate | Zero-penalty rate | Max validation error |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for _, row in benchmark_summary.iterrows():
            component = row.get("component", "")

            best_value = row.get("best_energy_or_cost", "")
            reference_cost = row.get("reference_cost", "")
            feasibility_rate = row.get("feasibility_rate", "")
            zero_penalty_rate = row.get("zero_penalty_rate", "")
            max_error = row.get("max_abs_validation_error", "")

            lines.append(
                f"| {component} | {best_value} | {reference_cost} | "
                f"{feasibility_rate} | {zero_penalty_rate} | {max_error} |"
            )

        lines.append("")

    if sa_summary is not None:
        lines.append("## SA Sensitivity Summary")
        lines.append("")
        lines.append("| Config | Steps | Initial T | Final T | Best cost | Feasibility rate | Zero-penalty rate | Mean energy |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")

        for _, row in sa_summary.iterrows():
            lines.append(
                f"| {row['config_name']} | {row['num_steps']} | "
                f"{row['initial_temperature']} | {row['final_temperature']} | "
                f"{row['best_total_cost']} | {row['feasibility_rate']} | "
                f"{row['zero_penalty_rate']} | {row['mean_energy']} |"
            )

        lines.append("")

    lines.append("## Current Status")
    lines.append("")
    lines.append("Completed Toy v2 pipeline:")
    lines.append("")
    lines.append("- Time-indexed variable mapping")
    lines.append("- Feasibility checker")
    lines.append("- Infeasible case validation")
    lines.append("- Function-based cost and penalty evaluator")
    lines.append("- Time-indexed QUBO matrix construction")
    lines.append("- QUBO energy validation")
    lines.append("- Ising Hamiltonian conversion")
    lines.append("- Ising energy validation")
    lines.append("- CP-SAT classical baseline")
    lines.append("- Simulated annealing baseline")
    lines.append("- SA sensitivity analysis")
    lines.append("- Solver benchmark summary")
    lines.append("- SA sensitivity figures")
    lines.append("")

    lines.append("## Recommended Next Step")
    lines.append("")
    lines.append(
        "The next recommended step is to move from toy instances to benchmark-derived "
        "instances. A practical next target is to implement a parser and augmentation "
        "pipeline for a small public job-shop or flexible job-shop benchmark instance, "
        "then add synthetic human-centered attributes such as workload, ergonomic risk, "
        "skill compatibility, safety risk, and robot utilization targets."
    )
    lines.append("")

    manifest_text = "\n".join(lines)

    manifest_path.write_text(manifest_text)

    print("Saved Toy v2 result manifest to:", manifest_path)


if __name__ == "__main__":
    main()
