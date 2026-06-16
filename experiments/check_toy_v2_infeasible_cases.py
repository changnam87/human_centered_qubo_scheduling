import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_feasibility import check_time_indexed_feasibility


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def print_case_result(case_name, report, expected_feasible):
    print()
    print("=" * 70)
    print("Case:", case_name)
    print("=" * 70)

    print("Expected feasible:", expected_feasible)
    print("Actual feasible:", report["feasible"])
    print("Number of violations:", report["num_violations"])

    print()
    print("Violations:")
    if report["num_violations"] == 0:
        print("No violations.")
    else:
        for violation in report["all_violations"]:
            print("-", violation["message"])

    if report["feasible"] == expected_feasible:
        print()
        print("PASS")
    else:
        print()
        print("FAIL")


def build_feasible_reference_schedule(num_variables, var_to_index):
    """
    Feasible reference schedule:

    O11 -> M at time 0, duration 1, ends at 1
    O12 -> M at time 1, duration 2, ends at 3
    O21 -> R at time 0, duration 2, ends at 2
    O22 -> M at time 3, duration 1, ends at 4
    """
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 1, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def main():
    instance_path = PROJECT_ROOT / "data" / "toy" / "toy_v2_time_indexed.json"
    instance = load_instance(instance_path)

    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    variable_names, index_to_var, var_to_index = create_time_indexed_variable_mapping(
        operations,
        resources,
        time_slots
    )

    num_variables = len(variable_names)

    print("=== Toy v2 infeasible case validation ===")
    print("Number of binary variables:", num_variables)

    # ------------------------------------------------------------
    # Case 0: Feasible reference case
    # ------------------------------------------------------------
    feasible_case = build_feasible_reference_schedule(num_variables, var_to_index)
    report = check_time_indexed_feasibility(feasible_case, instance, var_to_index)
    print_case_result(
        "Case 0: feasible reference schedule",
        report,
        expected_feasible=True
    )

    # ------------------------------------------------------------
    # Case 1: Operation starts twice
    # O11 is assigned to M at time 0 and H at time 2.
    # ------------------------------------------------------------
    case1 = build_feasible_reference_schedule(num_variables, var_to_index)
    set_start(case1, "O11", "H", 2, var_to_index)

    report = check_time_indexed_feasibility(case1, instance, var_to_index)
    print_case_result(
        "Case 1: operation starts twice",
        report,
        expected_feasible=False
    )

    # ------------------------------------------------------------
    # Case 2: Skill-incompatible resource
    # O12 is assigned to R at time 1, but O12-R is incompatible.
    # To keep assignment count exactly once, we remove O12-M-time1 first.
    # ------------------------------------------------------------
    case2 = build_feasible_reference_schedule(num_variables, var_to_index)

    old_index = var_to_index[("O12", "M", 1)]
    case2[old_index] = 0

    set_start(case2, "O12", "R", 1, var_to_index)

    report = check_time_indexed_feasibility(case2, instance, var_to_index)
    print_case_result(
        "Case 2: skill-incompatible resource",
        report,
        expected_feasible=False
    )

    # ------------------------------------------------------------
    # Case 3: Precedence violation
    # O12 starts at time 0, while O11 ends at time 1.
    # O11 -> O12 is violated.
    # To keep assignment count exactly once, remove O12-M-time1 first.
    # ------------------------------------------------------------
    case3 = build_feasible_reference_schedule(num_variables, var_to_index)

    old_index = var_to_index[("O12", "M", 1)]
    case3[old_index] = 0

    set_start(case3, "O12", "M", 0, var_to_index)

    report = check_time_indexed_feasibility(case3, instance, var_to_index)
    print_case_result(
        "Case 3: precedence violation",
        report,
        expected_feasible=False
    )

    # ------------------------------------------------------------
    # Case 4: Resource overlap
    # O11 uses M at [0,1)
    # O12 uses M at [0,2)
    # They overlap on M.
    #
    # This also creates a precedence violation for O11 -> O12.
    # That is acceptable; the checker should catch both or at least
    # identify the schedule as infeasible.
    # ------------------------------------------------------------
    case4 = build_feasible_reference_schedule(num_variables, var_to_index)

    old_index = var_to_index[("O12", "M", 1)]
    case4[old_index] = 0

    set_start(case4, "O12", "M", 0, var_to_index)

    report = check_time_indexed_feasibility(case4, instance, var_to_index)
    print_case_result(
        "Case 4: resource overlap",
        report,
        expected_feasible=False
    )

    # ------------------------------------------------------------
    # Case 5: Horizon violation
    # O12 starts at time 5 on M with duration 2, ends at 7,
    # beyond horizon 6.
    # To keep assignment count exactly once, remove O12-M-time1 first.
    # ------------------------------------------------------------
    case5 = build_feasible_reference_schedule(num_variables, var_to_index)

    old_index = var_to_index[("O12", "M", 1)]
    case5[old_index] = 0

    set_start(case5, "O12", "M", 5, var_to_index)

    report = check_time_indexed_feasibility(case5, instance, var_to_index)
    print_case_result(
        "Case 5: horizon violation",
        report,
        expected_feasible=False
    )

    print()
    print("=" * 70)
    print("Finished Toy v2 infeasible case validation.")
    print("=" * 70)


if __name__ == "__main__":
    main()
