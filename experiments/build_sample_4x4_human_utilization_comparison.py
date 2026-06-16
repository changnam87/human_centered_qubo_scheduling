import sys
from pathlib import Path
import ast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd


def count_assignments_from_schedule(schedule_text, workers, robots):
    """
    Count human and robot assignments from saved schedule string.
    """
    schedule = ast.literal_eval(schedule_text)

    human_count = 0
    robot_count = 0
    machine_count = 0

    for operation, selected in schedule.items():
        resource = None

        if isinstance(selected, dict):
            resource = selected.get("resource")

        elif isinstance(selected, (list, tuple)):
            if len(selected) == 0:
                resource = None
            else:
                first = selected[0]

                if isinstance(first, dict):
                    resource = first.get("resource")
                elif isinstance(first, (list, tuple)):
                    resource = first[0]
                elif isinstance(first, str):
                    resource = first

        if resource in workers:
            human_count += 1
        elif resource in robots:
            robot_count += 1
        elif resource is not None:
            machine_count += 1

    return human_count, robot_count, machine_count


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"

    baseline_path = tables_dir / "sample_4x4_augmented_cpsat_result.csv"
    human_path = tables_dir / "sample_4x4_human_utilization_cpsat_result.csv"

    output_path = tables_dir / "sample_4x4_human_utilization_comparison.csv"

    required_files = [
        baseline_path,
        human_path
    ]

    print("=== Checking required files ===")

    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            return

    baseline_df = pd.read_csv(baseline_path, dtype={"bitstring": str})
    human_df = pd.read_csv(human_path, dtype={"bitstring": str})

    baseline = baseline_df.iloc[0]
    human = human_df.iloc[0]

    workers = ["H0", "H1", "H2"]
    robots = ["R0", "R1"]

    baseline_human_count, baseline_robot_count, baseline_machine_count = count_assignments_from_schedule(
        baseline["schedule"],
        workers,
        robots
    )

    human_human_count = int(human["human_assignment_count"])
    human_robot_count = int(human["robot_assignment_count"])
    human_machine_count = int(human["selected_variables"]) - human_human_count - human_robot_count

    baseline_cost = float(baseline["total_cost"])
    human_cost = float(human["total_cost"])

    cost_increase = human_cost - baseline_cost
    percent_increase = cost_increase / baseline_cost * 100.0

    rows = []

    rows.append({
        "model_variant": "Baseline CP-SAT",
        "description": "No explicit human-utilization requirement",
        "status": baseline["status"],
        "feasible": baseline["feasible"],
        "num_violations": int(baseline["num_violations"]),
        "human_assignment_count": baseline_human_count,
        "robot_assignment_count": baseline_robot_count,
        "machine_assignment_count": baseline_machine_count,
        "processing": float(baseline["processing"]),
        "start_time": float(baseline["start_time"]),
        "workload": float(baseline["workload"]),
        "ergonomic": float(baseline["ergonomic"]),
        "safety": float(baseline["safety"]),
        "total_penalty": float(baseline["total_penalty"]),
        "total_cost": baseline_cost,
        "cost_increase_vs_baseline": 0.0,
        "percent_increase_vs_baseline": 0.0,
        "wall_time": float(baseline["wall_time"]),
        "notes": "CP-SAT selects no human worker assignments under the current objective."
    })

    rows.append({
        "model_variant": "Human-utilization CP-SAT",
        "description": "Hard constraint: at least 2 operations assigned to human workers",
        "status": human["status"],
        "feasible": human["feasible"],
        "num_violations": int(human["num_violations"]),
        "human_assignment_count": human_human_count,
        "robot_assignment_count": human_robot_count,
        "machine_assignment_count": human_machine_count,
        "processing": float(human["processing"]),
        "start_time": float(human["start_time"]),
        "workload": float(human["workload"]),
        "ergonomic": float(human["ergonomic"]),
        "safety": float(human["safety"]),
        "total_penalty": float(human["total_penalty"]),
        "total_cost": human_cost,
        "cost_increase_vs_baseline": cost_increase,
        "percent_increase_vs_baseline": percent_increase,
        "wall_time": float(human["wall_time"]),
        "notes": "Human involvement activates workload and ergonomic cost terms."
    })

    comparison_df = pd.DataFrame(rows)
    comparison_df.to_csv(output_path, index=False)

    print()
    print("=== sample_4x4 human-utilization comparison ===")
    print(comparison_df[[
        "model_variant",
        "human_assignment_count",
        "robot_assignment_count",
        "machine_assignment_count",
        "processing",
        "start_time",
        "workload",
        "ergonomic",
        "safety",
        "total_penalty",
        "total_cost",
        "cost_increase_vs_baseline",
        "percent_increase_vs_baseline"
    ]])

    print()
    print("Saved comparison to:", output_path)


if __name__ == "__main__":
    main()
