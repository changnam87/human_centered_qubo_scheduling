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
from src.core.ising import qubo_to_ising, binary_to_spin, ising_energy


def make_empty_bitstring(num_variables):
    return [0] * num_variables


def set_start(bitstring, operation, resource, time, var_to_index):
    index = var_to_index[(operation, resource, time)]
    bitstring[index] = 1


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def format_spinstring(spins):
    return "".join("+" if int(s) == 1 else "-" for s in spins)


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


def validate_candidate(label, bitstring, instance, var_to_index, Q, qubo_offset, h, J, ising_offset):
    spins = binary_to_spin(bitstring)

    energy_qubo = time_indexed_qubo_energy(
        bitstring,
        Q,
        qubo_offset
    )

    energy_ising = ising_energy(
        spins,
        h,
        J,
        ising_offset
    )

    evaluator_result = evaluate_time_indexed_solution(
        bitstring,
        instance,
        var_to_index
    )

    error = energy_ising - energy_qubo
    abs_error = abs(error)

    print()
    print("=" * 70)
    print(label)
    print("=" * 70)
    print("Feasible:", evaluator_result["feasible"])
    print("Number of violations:", evaluator_result["num_violations"])
    print("Function total cost:", evaluator_result["total_cost"])
    print("QUBO energy:", energy_qubo)
    print("Ising energy:", energy_ising)
    print("Error:", error)
    print("Absolute error:", abs_error)

    return {
        "label": label,
        "bitstring": format_bitstring(bitstring),
        "spinstring": format_spinstring(spins),
        "feasible": evaluator_result["feasible"],
        "num_violations": evaluator_result["num_violations"],
        "function_total_cost": evaluator_result["total_cost"],
        "energy_qubo": energy_qubo,
        "energy_ising": energy_ising,
        "error": error,
        "abs_error": abs_error,
        "processing": evaluator_result["processing"],
        "start_time": evaluator_result["start_time"],
        "workload": evaluator_result["workload"],
        "ergonomic": evaluator_result["ergonomic"],
        "safety": evaluator_result["safety"],
        "original_cost": evaluator_result["original_cost"],
        "assignment_start_penalty": evaluator_result["assignment_start_penalty"],
        "skill_penalty": evaluator_result["skill_penalty"],
        "horizon_penalty": evaluator_result["horizon_penalty"],
        "precedence_penalty": evaluator_result["precedence_penalty"],
        "resource_overlap_penalty": evaluator_result["resource_overlap_penalty"],
        "robot_utilization_penalty": evaluator_result["robot_utilization_penalty"],
        "total_penalty": evaluator_result["total_penalty"],
        "total_cost": evaluator_result["total_cost"]
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

    print("=== Toy v2 Ising conversion validation ===")
    print("Number of binary variables:", num_variables)

    print()
    print("=== Building Toy v2 QUBO matrix ===")

    Q, qubo_offset = build_time_indexed_qubo_matrix(
        instance,
        var_to_index
    )

    print("Q shape:", Q.shape)
    print("QUBO offset:", qubo_offset)

    print()
    print("=== Converting QUBO to Ising ===")

    h, J, ising_offset = qubo_to_ising(Q, qubo_offset)

    print("h length:", len(h))
    print("J shape:", J.shape)
    print("Ising offset:", ising_offset)

    h_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_ising_h.csv"
    J_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_ising_J.csv"

    h_df = pd.DataFrame({
        "variable": variable_names,
        "h": h
    })

    J_df = pd.DataFrame(J, index=variable_names, columns=variable_names)

    h_df.to_csv(h_path, index=False)
    J_df.to_csv(J_path)

    print("Saved h vector to:", h_path)
    print("Saved J matrix to:", J_path)

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
            qubo_offset,
            h,
            J,
            ising_offset
        )
    )

    rows.append(
        validate_candidate(
            "Infeasible reference schedule",
            infeasible_bitstring,
            instance,
            var_to_index,
            Q,
            qubo_offset,
            h,
            J,
            ising_offset
        )
    )

    validation_df = pd.DataFrame(rows)

    validation_path = PROJECT_ROOT / "results" / "tables" / "toy_v2_ising_validation.csv"
    validation_df.to_csv(validation_path, index=False)

    print()
    print("=" * 70)
    print("Validation summary")
    print("=" * 70)

    max_abs_error = validation_df["abs_error"].max()

    print("Maximum absolute error:", max_abs_error)

    if max_abs_error < 1e-6:
        print("PASS: Ising energy matches QUBO energy for tested schedules within numerical tolerance.")
    else:
        print("FAIL: Ising energy does not match QUBO energy.")

    print()
    print("Saved validation results to:", validation_path)


if __name__ == "__main__":
    main()
