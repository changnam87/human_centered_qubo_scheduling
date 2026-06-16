import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance, print_instance_summary
from src.core.variables import create_variable_mapping, print_variable_mapping
from src.core.qubo import build_qubo_matrix
from src.core.evaluate import evaluate_solution
from src.solvers.simulated_annealing import simulated_annealing_qubo


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


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

    print()
    print("=== Running simulated annealing ===")

    sa_result = simulated_annealing_qubo(
        Q=Q,
        constant_offset=constant_offset,
        num_reads=100,
        num_steps=1000,
        initial_temperature=10.0,
        final_temperature=0.01,
        seed=42
    )

    best_bitstring = sa_result["best_bitstring"]
    best_energy = sa_result["best_energy"]

    decoded = evaluate_solution(best_bitstring, instance, var_to_index)

    print()
    print("=== Best solution found by simulated annealing ===")
    print("Bitstring:", format_bitstring(best_bitstring))
    print("Energy:", best_energy)
    print("Feasible:", decoded["feasible"])
    print("Assignment:", decoded["assignment"])
    print("Processing cost:", decoded["processing"])
    print("Workload cost:", decoded["workload"])
    print("Ergonomic cost:", decoded["ergonomic"])
    print("Safety cost:", decoded["safety"])
    print("Original cost:", decoded["original_cost"])
    print("Assignment penalty:", decoded["assignment_penalty"])
    print("Skill penalty:", decoded["skill_penalty"])
    print("Robot utilization penalty:", decoded["robot_utilization_penalty"])
    print("Total penalty:", decoded["total_penalty"])
    print("Total cost:", decoded["total_cost"])

    # Save all SA read results
    rows = []

    for result in sa_result["all_results"]:
        bitstring = result["best_bitstring"]
        decoded_read = evaluate_solution(bitstring, instance, var_to_index)

        rows.append({
            "read": result["read"],
            "bitstring": format_bitstring(bitstring),
            "energy": result["best_energy"],
            "feasible": decoded_read["feasible"],
            "assignment": str(decoded_read["assignment"]),
            "processing": decoded_read["processing"],
            "workload": decoded_read["workload"],
            "ergonomic": decoded_read["ergonomic"],
            "safety": decoded_read["safety"],
            "original_cost": decoded_read["original_cost"],
            "assignment_penalty": decoded_read["assignment_penalty"],
            "skill_penalty": decoded_read["skill_penalty"],
            "robot_utilization_penalty": decoded_read["robot_utilization_penalty"],
            "total_penalty": decoded_read["total_penalty"],
            "total_cost": decoded_read["total_cost"]
        })

    df = pd.DataFrame(rows)

    output_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_simulated_annealing_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print("Saved simulated annealing results to:", output_path)

    # Compare against brute-force optimum if available
    brute_force_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_bruteforce_results.csv"

    if brute_force_path.exists():
        bf_df = pd.read_csv(brute_force_path, dtype={"bitstring": str})
        brute_force_best = bf_df.sort_values("total_cost").iloc[0]

        print()
        print("=== Comparison with brute force ===")
        print("Brute-force best bitstring:", brute_force_best["bitstring"])
        print("Brute-force best total cost:", brute_force_best["total_cost"])
        print("SA best bitstring:", format_bitstring(best_bitstring))
        print("SA best energy:", best_energy)

        gap = best_energy - float(brute_force_best["total_cost"])

        print("Absolute gap:", gap)

        if abs(gap) < 1e-9:
            print("SA matched the brute-force optimum.")
        else:
            print("SA did not match the brute-force optimum in this run.")

    else:
        print()
        print("Brute-force result file not found.")
        print("Run this first for comparison:")
        print("python experiments/run_toy_bruteforce.py")


if __name__ == "__main__":
    main()
