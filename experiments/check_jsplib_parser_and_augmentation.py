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


def main():
    input_path = PROJECT_ROOT / "data" / "benchmarks" / "jsplib" / "sample_3x3.txt"

    print("=== Parsing JSPLib-style file ===")
    base_instance = parse_jsplib_file(input_path)
    print_jsplib_instance_summary(base_instance)

    print()
    print("=== Augmenting with synthetic human-centered attributes ===")

    augmented = augment_with_human_centered_attributes(
        base_instance,
        num_workers=2,
        num_robots=1,
        seed=2026
    )

    print_augmented_summary(augmented)

    output_path = PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026.json"

    save_augmented_instance(augmented, output_path)

    print()
    print("Saved augmented instance to:", output_path)

    print()
    print("=== Sample operation attributes ===")

    for operation in augmented["operations"][:5]:
        print()
        print("Operation:", operation)
        print("Processing time:", augmented["processing_time"][operation])
        print("Skill compatibility:", augmented["skill_compatibility"][operation])
        print("Workload:", augmented["workload_score"][operation])
        print("Ergonomic risk:", augmented["ergonomic_risk"][operation])
        print("Safety risk:", augmented["safety_risk"][operation])
        print("Fatigue coefficient:", augmented["fatigue_coefficient"][operation])


if __name__ == "__main__":
    main()
