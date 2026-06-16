import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_evaluate import evaluate_time_indexed_solution


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def build_feasible_reference_schedule(num_variables, var_to_index):
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 1, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def build_infeasible_reference_schedule(num_variables, var_to_index):
    """
    Deliberately infeasible:
    O11 -> M at time 0
    O12 -> M at time 0
    O21 -> R at time 0
    O22 -> M at time 3

    This violates:
    - O11 -> O12 precedence
    - M resource overlap between O11 and O12
    """
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 0, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def print_evaluation(label, result):
    print()
    print("=" * 70)
    print(label)
    print("=" * 70)

    print("Feasible:", result["feasible"])
    print("Number of violations:", result["num_violations"])

    print()
    print("Schedule:")
    for operation, selected in result["schedule"].items():
        print(operation, ":", selected)

    print()
    print("Cost breakdown:")
    print("Processing:", result["processing"])
    print("Start time:", result["start_time"])
    print("Workload:", result["workload"])
    print("Ergonomic:", result["ergonomic"])
    print("Safety:", result["safety"])
    print("Original cost:", result["original_cost"])

    print()
    print("Penalty breakdown:")
    print("Assignment-start penalty:", result["assignment_start_penalty"])
    print("Skill penalty:", result["skill_penalty"])
    print("Horizon penalty:", result["horizon_penalty"])
    print("Precedence penalty:", result["precedence_penalty"])
    print("Resource-overlap penalty:", result["resource_overlap_penalty"])
    print("Robot-utilization penalty:", result["robot_utilization_penalty"])
    print("Total penalty:", result["total_penalty"])

    print()
    print("Total cost:", result["total_cost"])

    print()
    print("Violations:")
    if len(result["violations"]) == 0:
        print("No violations.")
    else:
        for violation in result["violations"]:
            print("-", violation["message"])


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

    print("=== Toy v2 cost evaluator validation ===")
    print("Number of binary variables:", num_variables)

    feasible_bitstring = build_feasible_reference_schedule(num_variables, var_to_index)
    infeasible_bitstring = build_infeasible_reference_schedule(num_variables, var_to_index)

    feasible_result = evaluate_time_indexed_solution(
        feasible_bitstring,
        instance,
        var_to_index
    )

    infeasible_result = evaluate_time_indexed_solution(
        infeasible_bitstring,
        instance,
        var_to_index
    )

    print_evaluation("Feasible reference schedule", feasible_result)
    print_evaluation("Infeasible reference schedule", infeasible_result)

    print()
    print("=" * 70)
    print("Validation checks")
    print("=" * 70)

    if feasible_result["feasible"] and feasible_result["total_penalty"] == 0:
        print("PASS: Feasible schedule has zero total penalty.")
    else:
        print("FAIL: Feasible schedule should have zero total penalty.")

    if (not infeasible_result["feasible"]) and infeasible_result["total_penalty"] > 0:
        print("PASS: Infeasible schedule has positive total penalty.")
    else:
        print("FAIL: Infeasible schedule should have positive total penalty.")


if __name__ == "__main__":
    main()
