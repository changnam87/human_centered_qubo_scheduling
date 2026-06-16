import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.core.instance import load_instance, print_instance_summary
from src.core.time_indexed_variables import (
    create_time_indexed_variable_mapping,
    print_time_indexed_variable_mapping
)
from src.core.time_indexed_feasibility import check_time_indexed_feasibility


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def print_schedule(schedule):
    print("=== Decoded schedule ===")

    for operation, selected in schedule.items():
        print(operation, ":", selected)


def print_violations(report):
    print("=== Feasibility violations ===")

    if report["num_violations"] == 0:
        print("No violations.")
        return

    for violation in report["all_violations"]:
        print("-", violation["message"])


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
    print("Number of binary variables:", len(variable_names))

    print()
    print_time_indexed_variable_mapping(
        variable_names,
        index_to_var,
        max_rows=20
    )

    # ------------------------------------------------------------
    # Handcrafted feasible schedule
    # ------------------------------------------------------------
    bitstring = make_empty_bitstring(len(variable_names))

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 1, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    report = check_time_indexed_feasibility(
        bitstring,
        instance,
        var_to_index
    )

    print()
    print("=== Handcrafted feasible candidate ===")
    print("Bitstring length:", len(bitstring))
    print("Number of selected variables:", sum(bitstring))
    print("Bitstring:", format_bitstring(bitstring))

    print()
    print_schedule(report["schedule"])

    print()
    print("=== Feasibility report ===")
    print("Feasible:", report["feasible"])
    print("Number of violations:", report["num_violations"])

    print()
    print_violations(report)

    if report["feasible"]:
        print()
        print("SUCCESS: The handcrafted schedule is feasible.")
    else:
        print()
        print("FAILED: The handcrafted schedule should be feasible, but violations were found.")


if __name__ == "__main__":
    main()
