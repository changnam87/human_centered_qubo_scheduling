from src.core.time_indexed_costs import compute_time_indexed_original_cost
from src.core.time_indexed_penalties import compute_time_indexed_total_penalty
from src.core.time_indexed_feasibility import check_time_indexed_feasibility


def evaluate_time_indexed_solution(bitstring, instance, var_to_index):
    """
    Evaluate a time-indexed scheduling solution.

    Returns original cost, penalties, total cost, and feasibility report.
    """
    cost_info = compute_time_indexed_original_cost(
        bitstring,
        instance,
        var_to_index
    )

    penalty_info = compute_time_indexed_total_penalty(
        bitstring,
        instance,
        var_to_index
    )

    feasibility_report = check_time_indexed_feasibility(
        bitstring,
        instance,
        var_to_index
    )

    total_cost = cost_info["original_cost"] + penalty_info["total_penalty"]

    return {
        "bitstring": tuple(int(v) for v in bitstring),
        "feasible": feasibility_report["feasible"],
        "num_violations": feasibility_report["num_violations"],
        "schedule": feasibility_report["schedule"],
        **cost_info,
        **penalty_info,
        "total_cost": total_cost,
        "violations": feasibility_report["all_violations"]
    }
