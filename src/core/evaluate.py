from src.core.costs import compute_original_cost
from src.core.penalties import compute_total_penalty
from src.core.feasibility import is_assignment_feasible
from src.core.variables import get_x


def decode_solution(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]

    assignment = {}

    for operation in operations:
        selected_resources = []

        for resource in resources:
            if get_x(bitstring, operation, resource, var_to_index) == 1:
                selected_resources.append(resource)

        assignment[operation] = selected_resources

    return assignment


def evaluate_solution(bitstring, instance, var_to_index):
    cost_info = compute_original_cost(bitstring, instance, var_to_index)
    penalty_info = compute_total_penalty(bitstring, instance, var_to_index)

    total_cost = cost_info["original_cost"] + penalty_info["total_penalty"]

    feasible = is_assignment_feasible(bitstring, instance, var_to_index)
    assignment = decode_solution(bitstring, instance, var_to_index)

    result = {
        "bitstring": bitstring,
        "feasible": feasible,
        "assignment": assignment,
        **cost_info,
        **penalty_info,
        "total_cost": total_cost
    }

    return result
