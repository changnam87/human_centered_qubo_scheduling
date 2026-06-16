from itertools import product
from src.core.evaluate import evaluate_solution


def solve_bruteforce(instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]

    num_variables = len(operations) * len(resources)

    all_results = []

    for bitstring in product([0, 1], repeat=num_variables):
        result = evaluate_solution(bitstring, instance, var_to_index)
        all_results.append(result)

    all_results_sorted = sorted(all_results, key=lambda x: x["total_cost"])

    feasible_results = [r for r in all_results if r["feasible"]]
    feasible_results_sorted = sorted(feasible_results, key=lambda x: x["original_cost"])

    best_qubo_solution = all_results_sorted[0]
    best_feasible_solution = feasible_results_sorted[0]

    return {
        "all_results": all_results,
        "all_results_sorted": all_results_sorted,
        "feasible_results": feasible_results,
        "feasible_results_sorted": feasible_results_sorted,
        "best_qubo_solution": best_qubo_solution,
        "best_feasible_solution": best_feasible_solution
    }
