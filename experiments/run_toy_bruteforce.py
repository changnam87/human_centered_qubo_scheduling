import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.core.instance import load_instance, print_instance_summary
from src.core.variables import create_variable_mapping, print_variable_mapping
from src.solvers.bruteforce import solve_bruteforce


def format_bitstring(bitstring):
    return "".join(str(int(v)) for v in bitstring)


def format_bitstring_tuple(bitstring):
    return "(" + ", ".join(str(int(v)) for v in bitstring) + ")"


def format_bitstring_for_excel(bitstring):
    bitstring_text = format_bitstring(bitstring)
    return f'="{bitstring_text}"'


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
    print("=== Running brute-force enumeration ===")

    results = solve_bruteforce(instance, var_to_index)

    best_qubo_solution = results["best_qubo_solution"]
    best_feasible_solution = results["best_feasible_solution"]

    print()
    print("=== Best solution by total QUBO-like cost ===")
    print("Bitstring:", format_bitstring(best_qubo_solution["bitstring"]))
    print("Bitstring tuple:", format_bitstring_tuple(best_qubo_solution["bitstring"]))
    print("Feasible:", best_qubo_solution["feasible"])
    print("Assignment:", best_qubo_solution["assignment"])
    print("Processing cost:", best_qubo_solution["processing"])
    print("Workload cost:", best_qubo_solution["workload"])
    print("Ergonomic cost:", best_qubo_solution["ergonomic"])
    print("Safety cost:", best_qubo_solution["safety"])
    print("Original cost:", best_qubo_solution["original_cost"])
    print("Robot utilization penalty:", best_qubo_solution["robot_utilization_penalty"])
    print("Total penalty:", best_qubo_solution["total_penalty"])
    print("Total cost:", best_qubo_solution["total_cost"])

    print()
    print("=== Best feasible solution by original cost ===")
    print("Bitstring:", format_bitstring(best_feasible_solution["bitstring"]))
    print("Bitstring tuple:", format_bitstring_tuple(best_feasible_solution["bitstring"]))
    print("Feasible:", best_feasible_solution["feasible"])
    print("Assignment:", best_feasible_solution["assignment"])
    print("Processing cost:", best_feasible_solution["processing"])
    print("Workload cost:", best_feasible_solution["workload"])
    print("Ergonomic cost:", best_feasible_solution["ergonomic"])
    print("Safety cost:", best_feasible_solution["safety"])
    print("Original cost:", best_feasible_solution["original_cost"])
    print("Robot utilization penalty:", best_feasible_solution["robot_utilization_penalty"])
    print("Total penalty:", best_feasible_solution["total_penalty"])
    print("Total cost:", best_feasible_solution["total_cost"])

    print()
    print("=== Top 10 solutions by total QUBO-like cost ===")

    top_10 = results["all_results_sorted"][:10]

    for rank, result in enumerate(top_10, start=1):
        print()
        print(f"Rank {rank}")
        print("Bitstring:", format_bitstring(result["bitstring"]))
        print("Bitstring tuple:", format_bitstring_tuple(result["bitstring"]))
        print("Feasible:", result["feasible"])
        print("Assignment:", result["assignment"])
        print("Original cost:", result["original_cost"])
        print("Penalty:", result["total_penalty"])
        print("Total cost:", result["total_cost"])

    rows = []

    for result in results["all_results_sorted"]:
        row = {
            "bitstring": format_bitstring(result["bitstring"]),
            "bitstring_tuple": format_bitstring_tuple(result["bitstring"]),
            "bitstring_excel": format_bitstring_for_excel(result["bitstring"]),
            "feasible": result["feasible"],
            "assignment": str(result["assignment"]),
            "processing": result["processing"],
            "workload": result["workload"],
            "ergonomic": result["ergonomic"],
            "safety": result["safety"],
            "original_cost": result["original_cost"],
            "assignment_penalty": result["assignment_penalty"],
            "skill_penalty": result["skill_penalty"],
            "robot_utilization_penalty": result["robot_utilization_penalty"],
            "total_penalty": result["total_penalty"],
            "total_cost": result["total_cost"]
        }

        rows.append(row)

    df = pd.DataFrame(rows)

    output_path = PROJECT_ROOT / "results" / "tables" / "toy_v1_bruteforce_results.csv"
    df.to_csv(output_path, index=False)

    print()
    print("Saved results to:", output_path)
    print()
    print("When reading this CSV in pandas, use:")
    print('pd.read_csv(path, dtype={"bitstring": str})')


if __name__ == "__main__":
    main()
