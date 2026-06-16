import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.core.instance import load_instance, print_instance_summary
from src.core.time_indexed_variables import (
    create_time_indexed_variable_mapping,
    print_time_indexed_variable_mapping
)


def main():
    instance_path = PROJECT_ROOT / "data" / "toy" / "toy_v2_time_indexed.json"

    instance = load_instance(instance_path)

    print_instance_summary(instance)

    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    variable_names, index_to_var, var_to_index = create_time_indexed_variable_mapping(
        operations,
        resources,
        time_slots
    )

    print()
    print("=== Toy v2 dimensions ===")
    print("Number of operations:", len(operations))
    print("Number of resources:", len(resources))
    print("Number of time slots:", len(time_slots))
    print("Number of binary variables:", len(variable_names))

    print()
    print_time_indexed_variable_mapping(
        variable_names,
        index_to_var,
        max_rows=40
    )

    print()
    print("=== Precedence constraints ===")
    for before, after in instance["precedence"]:
        print(before, "->", after)

    print()
    print("=== Processing times ===")
    for operation in operations:
        print(operation, instance["processing_time"][operation])

    print()
    print("=== Skill compatibility ===")
    for operation in operations:
        print(operation, instance["skill_compatibility"][operation])


if __name__ == "__main__":
    main()
