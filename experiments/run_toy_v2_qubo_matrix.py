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


def build_feasible_reference_schedule(num_variables, var_to_index):
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 1, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def build_infeasible_reference_schedule(num_variables, var_to_index):
    bitstring = make_empty_bitstring(num_variables)

    set_start(bitstring, "O11", "M", 0, var_to_index)
    set_start(bitstring, "O12", "M", 0, var_to_index)
    set_start(bitstring, "O21", "R", 0, var_to_index)
    set_start(bitstring, "O22", "M", 3, var_to_index)

    return bitstring


def validate_candidate(label, bitstring, instance, var_to_index, Q, constant_offset):
    function_result = evaluate_time_indexed_solution(
        bitstring,
        instance,
        var_to_index
    )

    qubo_energy = time_indexed_qubo_energy(
        bitstring,
        Q,
        constant_offset
    )

    function_total_cost = function_result["total_cost"]
    error = qubo_energy - function_total_cost
    abs_error = abs(error)

    print()
    print("=" * 70)
    print(label)
    print("=" * 70)

    print("Feasible:", function_result["feasible"])
    print("Number of violations:", function_result["num_violations"])
    print("Function total cost:", function_total_cost)
    print("QUBO energy:", qubo_energy)
    print("Error:", error)
    print("Absolute error:", abs_error)

    print()
    print("Cost breakdown:")
    print("Processing:", function_result["processing"])
    print("Start time:", function_result["start_time"])
    print("Workload:", function_result["workload"])
    print("Ergonomic:", function_result["ergonomic"])
    print("Safety:", function_result["safety"])
    print("Original cost:", function_result["original_cost"])

    print()
    print("Penalty breakdown:")
    print("Assignment-start penalty:", function_result["assignment_start_penalty"])
    print("Skill penalty:", function_result["skill_penalty"])
    print("Horizon penalty:", function_result["horizon_penalty"])
    print("Precedence penalty:", function_result["precedence_penalty"])
    print("Resource-overlap penalty:", function_result["resource_overlap_penalty"])
    print("Robot-utilization penalty:", function_result["robot_utilization_penalty"])
    print("Total penalty:", function_result["total_penalty"])

    return {
        "label": label,
        "bitstring": format_bitstring(bitstring),
        "feasible": function_result["feasible"],
        "num_violations": function_result["num_violations"],
        "function_total_cost": function_total_cost,
        "qubo_energy": qubo_energy,
        "error": error,
        "abs_error": abs_error,
        "processing": function_result["processing"],
        "start_time": function_result["start_time"],
        "workload": function_result["workload"],
        "ergonomic": function_result["ergonomic"],
        "safety": function_result["safety"],
        "original_cost": function_result["original_cost"],
        "assignment_start_penalty": function_result["assignment_start_penalty"],
        "skill_penalty": function_result["skill_penalty"],
        "horizon_penalty": function_result["horizon_penalty"],
        "precedence_penalty": function_result["precedence_penalty"],
        "resource_overlap_penalty": function_result["resource_overlap_penalty"],
        "robot_utilization_penalty": function_result["robot_utilization_penalty"],
        "total_penalty": function_result["total_penalty"],
        "total_cost": function_result["total_cost"]
    }


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

    print("=== Toy v2 QUBO matrix validation ===")
    print("Number of binary variables:", num_variables)

    print()
    print("=== Building time-indexed QUBO matrix ===")

    Q, constant_offset = build_time_indexed_qubo_matrix(
        instance,
        var_to_index
    )

    print("Q shape:", Q.shape)
    print("Constant offset:", constant_offset)

    q_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_Q_matrix.csv"
    pd.DataFrame(Q, index=variable_names, columns=variable_names).to_csv(q_path)

    print("Saved Q matrix to:", q_path)

    feasible_bitstring = build_feasible_reference_schedule(
        num_variables,
        var_to_index
    )

    infeasible_bitstring = build_infeasible_reference_schedule(
        num_variables,
        var_to_index
    )

    rows = []

    rows.append(
        validate_candidate(
            "Feasible reference schedule",
            feasible_bitstring,
            instance,
            var_to_index,
            Q,
            constant_offset
        )
    )

    rows.append(
        validate_candidate(
            "Infeasible reference schedule",
            infeasible_bitstring,
            instance,
            var_to_index,
            Q,
            constant_offset
        )
    )

    validation_df = pd.DataFrame(rows)

    validation_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_qubo_validation.csv"
    validation_df.to_csv(validation_path, index=False)

    print()
    print("=" * 70)
    print("Validation summary")
    print("=" * 70)

    max_abs_error = validation_df["abs_error"].max()

    print("Maximum absolute error:", max_abs_error)

    if max_abs_error < 1e-9:
        print("PASS: QUBO energy matches function-based total cost for tested schedules.")
    else:
        print("FAIL: QUBO energy does not match function-based total cost.")

    print()
    print("Saved validation results to:", validation_path)


if __name__ == "__main__":
    main()
