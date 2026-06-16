import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance, print_instance_summary
from src.core.variables import create_variable_mapping, print_variable_mapping
from src.core.qubo import build_qubo_matrix, qubo_energy
from src.core.ising import qubo_to_ising, binary_to_spin, ising_energy


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

    Q, qubo_offset = build_qubo_matrix(instance, var_to_index)

    print("Q shape:", Q.shape)
    print("QUBO offset:", qubo_offset)

    print()
    print("=== Converting QUBO to Ising ===")

    h, J, ising_offset = qubo_to_ising(Q, qubo_offset)

    print("Number of h biases:", len(h))
    print("J shape:", J.shape)
    print("Ising offset:", ising_offset)

    # Save Ising parameters
    h_df = pd.DataFrame({
        "variable": variable_names,
        "h": h
    })

    J_df = pd.DataFrame(J, index=variable_names, columns=variable_names)

    h_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_ising_h.csv"
    J_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_ising_J.csv"

    h_df.to_csv(h_path, index=False)
    J_df.to_csv(J_path)

    print("Saved h vector to:", h_path)
    print("Saved J matrix to:", J_path)

    # Validate against brute-force bitstrings
    brute_force_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_bruteforce_results.csv"

    if not brute_force_path.exists():
        print()
        print("Brute-force result file not found.")
        print("Please run this first:")
        print("python experiments/run_toy_bruteforce.py")
        return

    df = pd.read_csv(brute_force_path, dtype={"bitstring": str})

    rows = []
    max_abs_error = 0.0

    for _, row in df.iterrows():
        bitstring_text = row["bitstring"]
        bitstring = tuple(int(ch) for ch in bitstring_text)

        spins = binary_to_spin(bitstring)

        energy_qubo = qubo_energy(bitstring, Q, qubo_offset)
        energy_ising = ising_energy(spins, h, J, ising_offset)

        error = energy_ising - energy_qubo
        abs_error = abs(error)

        if abs_error > max_abs_error:
            max_abs_error = abs_error

        rows.append({
            "bitstring": bitstring_text,
            "spinstring": "".join("+" if s == 1 else "-" for s in spins),
            "energy_qubo": energy_qubo,
            "energy_ising": energy_ising,
            "error": error,
            "abs_error": abs_error
        })

    validation_df = pd.DataFrame(rows)

    validation_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_ising_validation.csv"
    validation_df.to_csv(validation_path, index=False)

    print()
    print("=== Ising Validation ===")
    print("Saved validation results to:", validation_path)
    print("Maximum absolute error:", max_abs_error)

    if max_abs_error < 1e-9:
        print("Validation PASSED: Ising energy matches QUBO energy.")
    else:
        print("Validation FAILED: Ising energy does not match QUBO energy.")

    print()
    print("=== Best solution by Ising energy ===")
    best_by_ising = validation_df.sort_values("energy_ising").iloc[0]
    print(best_by_ising)

    print()
    print("=== Top 10 solutions by Ising energy ===")
    top_10 = validation_df.sort_values("energy_ising").head(10)
    print(top_10[[
        "bitstring",
        "spinstring",
        "energy_qubo",
        "energy_ising",
        "error"
    ]])


if __name__ == "__main__":
    main()
