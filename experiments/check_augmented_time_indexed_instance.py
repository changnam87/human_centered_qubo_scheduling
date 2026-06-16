import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance
from src.core.time_indexed_variables import create_time_indexed_variable_mapping
from src.core.time_indexed_evaluate import evaluate_time_indexed_solution
from src.core.time_indexed_qubo import (
    build_time_indexed_qubo_matrix,
    time_indexed_qubo_energy
)


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def build_simple_feasible_schedule(instance, num_variables, var_to_index):
    """
    Build a simple feasible schedule for the augmented sample_3x3 instance.

    This uses compatible machine assignments from the original JSPLib sequence.
    The schedule is intentionally simple and sequential enough to avoid overlap.

    Jobs:
    J0: O0_0 -> O0_1 -> O0_2
    J1: O1_0 -> O1_1 -> O1_2
    J2: O2_0 -> O2_1 -> O2_2

    Handcrafted schedule:
    O0_0 M0 t=0 duration 3 ends 3
    O0_1 M1 t=3 duration 2 ends 5
    O0_2 M2 t=5 duration 2 ends 7

    O1_0 M0 t=3 duration 2 ends 5
    O1_1 M2 t=7 duration 1 ends 8
    O1_2 M1 t=8 duration 4 ends 12

    O2_0 M1 t=0 duration 4 ends 4
    O2_1 M2 t=8 duration 3 ends 11
    O2_2 M0 t=11 duration 2 ends 13
    """
    bitstring = make_empty_bitstring(num_variables)

    schedule = [
        ("O0_0", "M0", 0),
        ("O0_1", "M1", 4),
        ("O0_2", "M2", 6),

        ("O1_0", "M0", 3),
        ("O1_1", "R0", 5),
        ("O1_2", "M1", 9),

        ("O2_0", "M1", 0),
        ("O2_1", "M2", 8),
        ("O2_2", "M0", 11),
    ]

    for operation, resource, time in schedule:
        set_start(bitstring, operation, resource, time, var_to_index)

    return bitstring


def print_evaluation(result):
    print()
    print("=== Evaluation result ===")
    print("Feasible:", result["feasible"])
    print("Number of violations:", result["num_violations"])

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
    print("Schedule:")
    for operation, selected in result["schedule"].items():
        print(operation, ":", selected)

    if result["num_violations"] > 0:
        print()
        print("Violations:")
        for violation in result["violations"]:
            print("-", violation["message"])


def main():
    instance_path = PROJECT_ROOT / "data" / "augmented" / "sample_3x3_hc_seed2026_time_indexed.json"

    print("=== Checking augmented time-indexed benchmark instance ===")
    print("Input:", instance_path)

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

    print()
    print("=== Dimensions ===")
    print("Operations:", len(operations))
    print("Resources:", len(resources))
    print("Time slots:", len(time_slots))
    print("Binary variables:", num_variables)

    expected_variables = len(operations) * len(resources) * len(time_slots)
    print("Expected binary variables:", expected_variables)

    # ------------------------------------------------------------
    # Handcrafted feasible schedule
    # ------------------------------------------------------------
    bitstring = build_simple_feasible_schedule(
        instance,
        num_variables,
        var_to_index
    )

    print()
    print("=== Handcrafted benchmark schedule ===")
    print("Selected variables:", sum(bitstring))
    print("Bitstring length:", len(bitstring))

    result = evaluate_time_indexed_solution(
        bitstring,
        instance,
        var_to_index
    )

    print_evaluation(result)

    # ------------------------------------------------------------
    # QUBO matrix validation for this handcrafted schedule
    # ------------------------------------------------------------
    print()
    print("=== Building QUBO matrix ===")

    Q, constant_offset = build_time_indexed_qubo_matrix(
        instance,
        var_to_index
    )

    print("Q shape:", Q.shape)
    print("Constant offset:", constant_offset)

    qubo_energy = time_indexed_qubo_energy(
        bitstring,
        Q,
        constant_offset
    )

    function_total_cost = result["total_cost"]
    error = qubo_energy - function_total_cost
    abs_error = abs(error)

    print()
    print("=== QUBO validation on handcrafted benchmark schedule ===")
    print("Function total cost:", function_total_cost)
    print("QUBO energy:", qubo_energy)
    print("Error:", error)
    print("Absolute error:", abs_error)

    if abs_error < 1e-6:
        print("PASS: QUBO energy matches function-based total cost within tolerance.")
    else:
        print("FAIL: QUBO energy does not match function-based total cost.")

    # ------------------------------------------------------------
    # Save validation result
    # ------------------------------------------------------------
    output_path = PROJECT_ROOT / "results" / "tables" / "sample_3x3_augmented_qubo_validation.csv"

    row = {
        "instance_name": instance["instance_name"],
        "num_operations": len(operations),
        "num_resources": len(resources),
        "num_time_slots": len(time_slots),
        "num_binary_variables": num_variables,
        "bitstring": format_bitstring(bitstring),
        "selected_variables": sum(bitstring),
        "feasible": result["feasible"],
        "num_violations": result["num_violations"],
        "processing": result["processing"],
        "start_time": result["start_time"],
        "workload": result["workload"],
        "ergonomic": result["ergonomic"],
        "safety": result["safety"],
        "original_cost": result["original_cost"],
        "assignment_start_penalty": result["assignment_start_penalty"],
        "skill_penalty": result["skill_penalty"],
        "horizon_penalty": result["horizon_penalty"],
        "precedence_penalty": result["precedence_penalty"],
        "resource_overlap_penalty": result["resource_overlap_penalty"],
        "robot_utilization_penalty": result["robot_utilization_penalty"],
        "total_penalty": result["total_penalty"],
        "total_cost": result["total_cost"],
        "qubo_energy": qubo_energy,
        "error": error,
        "abs_error": abs_error,
        "schedule": str(result["schedule"])
    }

    pd.DataFrame([row]).to_csv(output_path, index=False)

    print()
    print("Saved validation result to:", output_path)


if __name__ == "__main__":
    main()
