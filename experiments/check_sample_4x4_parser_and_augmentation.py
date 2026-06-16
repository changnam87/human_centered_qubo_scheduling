import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.jsplib_parser import (
    parse_jsplib_file,
    print_jsplib_instance_summary
)
from src.data.human_attribute_augmenter import (
    augment_with_human_centered_attributes,
    save_augmented_instance,
    print_augmented_summary
)
from src.data.time_indexed_adapter import (
    add_time_indexed_fields,
    print_time_indexed_instance_summary
)


def main():
    input_path = PROJECT_ROOT / "data" / "benchmarks" / "jsplib" / "sample_4x4.txt"

    print("=== Parsing sample_4x4 JSPLib-style file ===")
    base_instance = parse_jsplib_file(input_path)
    print_jsplib_instance_summary(base_instance)

    print()
    print("=== Augmenting sample_4x4 with synthetic human-centered attributes ===")

    augmented = augment_with_human_centered_attributes(
        base_instance,
        num_workers=3,
        num_robots=2,
        seed=2026
    )

    print_augmented_summary(augmented)

    print()
    print("=== Adding time-indexed fields ===")

    time_indexed = add_time_indexed_fields(
        augmented,
        planning_horizon=None,
        buffer_factor=1.5
    )

    print_time_indexed_instance_summary(time_indexed)

    output_path = PROJECT_ROOT / "data" / "augmented" / "sample_4x4_hc_seed2026_time_indexed.json"

    save_augmented_instance(time_indexed, output_path)

    print()
    print("Saved time-indexed augmented sample_4x4 instance to:", output_path)

    print()
    print("=== Sanity checks ===")

    num_operations = len(time_indexed["operations"])
    num_resources = len(time_indexed["resources"])
    num_time_slots = len(time_indexed["time_slots"])
    num_variables = num_operations * num_resources * num_time_slots

    print("Operations:", num_operations)
    print("Resources:", num_resources)
    print("Time slots:", num_time_slots)
    print("Binary variables:", num_variables)

    print()
    print("First 5 operations:")

    for operation in time_indexed["operations"][:5]:
        print()
        print("Operation:", operation)
        print("Machine requirement:", time_indexed["machine_requirement"][operation])
        print("Processing time:", time_indexed["processing_time"][operation])
        print("Skill compatibility:", time_indexed["skill_compatibility"][operation])
        print("Workload:", time_indexed["workload_score"][operation])
        print("Ergonomic risk:", time_indexed["ergonomic_risk"][operation])
        print("Safety risk:", time_indexed["safety_risk"][operation])
        print("Fatigue coefficient:", time_indexed["fatigue_coefficient"][operation])


if __name__ == "__main__":
    main()
