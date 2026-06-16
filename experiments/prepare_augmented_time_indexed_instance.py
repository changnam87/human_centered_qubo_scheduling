import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.time_indexed_adapter import (
    load_json,
    save_json,
    add_time_indexed_fields,
    print_time_indexed_instance_summary
)


def main():
    input_path = PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026.json"

    output_path = PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026_time_indexed.json"

    print("=== Preparing augmented time-indexed instance ===")
    print("Input:", input_path)

    instance = load_json(input_path)

    # For this small 3x3 instance, automatic horizon is fine.
    # Later we can manually control this.
    time_indexed_instance = add_time_indexed_fields(
        instance,
        planning_horizon=None,
        buffer_factor=1.5
    )

    print_time_indexed_instance_summary(time_indexed_instance)

    save_json(time_indexed_instance, output_path)

    print()
    print("Saved time-indexed augmented instance to:", output_path)


if __name__ == "__main__":
    main()
