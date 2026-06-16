import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.data.jsplib_parser import parse_jsplib_file
from src.data.human_attribute_augmenter import (
    augment_with_human_centered_attributes,
    save_augmented_instance
)
from src.data.time_indexed_adapter import add_time_indexed_fields


def count_compatible_assignments(instance):
    operations = instance["operations"]
    resources = instance["resources"]
    skill_compatibility = instance["skill_compatibility"]

    total = 0

    for operation in operations:
        for resource in resources:
            if skill_compatibility[operation][resource] == 1:
                total += 1

    return total


def count_worker_compatible_assignments(instance):
    operations = instance["operations"]
    workers = instance.get("workers", [])
    skill_compatibility = instance["skill_compatibility"]

    total = 0

    for operation in operations:
        for worker in workers:
            if skill_compatibility[operation][worker] == 1:
                total += 1

    return total


def count_robot_compatible_assignments(instance):
    operations = instance["operations"]
    robots = instance.get("robots", [])
    skill_compatibility = instance["skill_compatibility"]

    total = 0

    for operation in operations:
        for robot in robots:
            if skill_compatibility[operation][robot] == 1:
                total += 1

    return total


def main():
    base_path = PROJECT_ROOT / "data" / "benchmarks" / "jsplib" / "sample_3x3.txt"
    output_dir = PROJECT_ROOT / "data" / "augmented" / "batch"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_batch_instance_summary.csv"

    seeds = [
        1001,
        1002,
        1003,
        1004,
        1005,
        1006,
        1007,
        1008,
        1009,
        1010
    ]

    print("=== Generating sample_3x3 augmented batch ===")
    print("Base file:", base_path)
    print("Number of seeds:", len(seeds))

    base_instance = parse_jsplib_file(base_path)

    rows = []

    for seed in seeds:
        print()
        print("Generating seed:", seed)

        augmented = augment_with_human_centered_attributes(
            base_instance,
            num_workers=2,
            num_robots=1,
            seed=seed
        )

        time_indexed = add_time_indexed_fields(
            augmented,
            planning_horizon=None,
            buffer_factor=1.5
        )

        output_path = output_dir / f"sample_3x3_hc_seed{seed}_time_indexed.json"

        save_augmented_instance(time_indexed, output_path)

        num_operations = len(time_indexed["operations"])
        num_machines = len(time_indexed["machines"])
        num_workers = len(time_indexed["workers"])
        num_robots = len(time_indexed["robots"])
        num_resources = len(time_indexed["resources"])
        planning_horizon = time_indexed["planning_horizon"]
        num_time_slots = len(time_indexed["time_slots"])
        num_binary_variables = num_operations * num_resources * num_time_slots

        total_compatible = count_compatible_assignments(time_indexed)
        worker_compatible = count_worker_compatible_assignments(time_indexed)
        robot_compatible = count_robot_compatible_assignments(time_indexed)

        avg_workload = sum(time_indexed["workload_score"].values()) / num_operations
        avg_ergonomic = sum(time_indexed["ergonomic_risk"].values()) / num_operations
        avg_safety = sum(time_indexed["safety_risk"].values()) / num_operations
        avg_fatigue = sum(time_indexed["fatigue_coefficient"].values()) / num_operations

        rows.append({
            "base_instance": base_instance["instance_name"],
            "seed": seed,
            "output_file": str(output_path.relative_to(PROJECT_ROOT)),
            "num_operations": num_operations,
            "num_machines": num_machines,
            "num_workers": num_workers,
            "num_robots": num_robots,
            "num_resources": num_resources,
            "planning_horizon": planning_horizon,
            "num_time_slots": num_time_slots,
            "num_binary_variables": num_binary_variables,
            "total_compatible_assignments": total_compatible,
            "worker_compatible_assignments": worker_compatible,
            "robot_compatible_assignments": robot_compatible,
            "avg_workload": avg_workload,
            "avg_ergonomic_risk": avg_ergonomic,
            "avg_safety_risk": avg_safety,
            "avg_fatigue_coefficient": avg_fatigue
        })

        print("Saved:", output_path)
        print("Binary variables:", num_binary_variables)
        print("Compatible assignments:", total_compatible)
        print("Worker-compatible assignments:", worker_compatible)
        print("Robot-compatible assignments:", robot_compatible)

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(summary_path, index=False)

    print()
    print("=== Batch generation completed ===")
    print("Saved summary to:", summary_path)

    print()
    print(summary_df[[
        "seed",
        "planning_horizon",
        "num_binary_variables",
        "total_compatible_assignments",
        "worker_compatible_assignments",
        "robot_compatible_assignments",
        "avg_workload",
        "avg_ergonomic_risk",
        "avg_safety_risk"
    ]])


if __name__ == "__main__":
    main()
