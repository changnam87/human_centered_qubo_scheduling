import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance, print_instance_summary
from src.core.variables import create_variable_mapping, print_variable_mapping
from src.core.evaluate import evaluate_solution
from src.core.qubo import build_qubo_matrix, qubo_energy


def main():
    instance_path = PROJECT_ROOT / "data" / "toy" / "toy_v1.json"
    instance = load_instance(instance_path)

    print_instance_summary(instance)

    operations = instance["operations"]
    resources = instance["resources"]

    variable_names, index_to_var, var_to_index = create_variable_mapping(
        operations,
        resources
    )

    print()
    print_variable_mapping(variable_names, index_to_var)

    print()
    print("=== Building QUBO matrix ===")

    Q, constant_offset = build_qubo_matrix(instance, var_to_index)

    print("Q shape:", Q.shape)
    print("Constant offset:", constant_offset)

    q_matrix_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_Q_matrix.csv"
    pd.DataFrame(Q, index=variable_names, columns=variable_names).to_csv(q_matrix_path)

    print("Saved Q matrix to:", q_matrix_path)

    brute_force_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_bruteforce_results.csv"

    if not brute_force_path.exists():
        print()
        print("Brute-force result file not found.")
        print("Please run this first:")
        print("python experiments/run_toy_bruteforce.py")
        return

    df = pd.read_csv(brute_force_path, dtype={"bitstring": str})

    validation_rows = []
    max_abs_error = 0.0

    for _, row in df.iterrows():
        bitstring_text = row["bitstring"]
        bitstring = tuple(int(ch) for ch in bitstring_text)

        energy_from_Q = qubo_energy(bitstring, Q, constant_offset)

        result = evaluate_solution(bitstring, instance, var_to_index)

        function_total_cost = result["total_cost"]

        error = energy_from_Q - function_total_cost
        abs_error = abs(error)

        if abs_error > max_abs_error:
            max_abs_error = abs_error

        validation_rows.append({
            "bitstring": bitstring_text,
            "feasible": result["feasible"],
            "assignment": str(result["assignment"]),
            "function_total_cost": function_total_cost,
            "energy_from_Q": energy_from_Q,
            "error": error,
            "abs_error": abs_error
        })

    validation_df = pd.DataFrame(validation_rows)

    validation_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_qubo_validation.csv"
    validation_df.to_csv(validation_path, index=False)

    print()
    print("=== QUBO Validation ===")
    print("Saved validation results to:", validation_path)
    print("Maximum absolute error:", max_abs_error)

    if max_abs_error < 1e-9:
        print("Validation PASSED: Q matrix energy matches the full function-based total cost.")
    else:
        print("Validation FAILED: Q matrix energy does not match the full function-based total cost.")

    print()
    print("=== Best solution by Q matrix energy ===")
    best_by_Q = validation_df.sort_values("energy_from_Q").iloc[0]
    print(best_by_Q)

    print()
    print("=== Top 10 solutions by Q matrix energy ===")
    top_10 = validation_df.sort_values("energy_from_Q").head(10)
    print(top_10[[
        "bitstring",
        "feasible",
        "function_total_cost",
        "energy_from_Q",
        "error"
    ]])


if __name__ == "__main__":
    main()
