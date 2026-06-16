from src.core.variables import get_x


def compute_processing_cost(bitstring, instance, var_to_index):
    total = 0

    operations = instance["operations"]
    resources = instance["resources"]
    processing_cost = instance["processing_cost"]

    for operation in operations:
        for resource in resources:
            x = get_x(bitstring, operation, resource, var_to_index)
            total += processing_cost[operation][resource] * x

    return total


def compute_workload_cost(bitstring, instance, var_to_index):
    total = 0

    operations = instance["operations"]
    workload_score = instance["workload_score"]
    lambda_workload = instance["weights"]["lambda_workload"]

    for operation in operations:
        x_human = get_x(bitstring, operation, "H", var_to_index)
        total += workload_score[operation] * x_human

    return lambda_workload * total


def compute_ergonomic_cost(bitstring, instance, var_to_index):
    total = 0

    operations = instance["operations"]
    ergonomic_risk = instance["ergonomic_risk"]
    lambda_ergonomic = instance["weights"]["lambda_ergonomic"]

    for operation in operations:
        x_human = get_x(bitstring, operation, "H", var_to_index)
        total += ergonomic_risk[operation] * x_human

    return lambda_ergonomic * total


def compute_safety_cost(bitstring, instance, var_to_index):
    total = 0

    operations = instance["operations"]
    robot_safety_risk = instance["robot_safety_risk"]
    lambda_safety = instance["weights"]["lambda_safety"]

    for operation in operations:
        x_robot = get_x(bitstring, operation, "R", var_to_index)
        total += robot_safety_risk[operation] * x_robot

    return lambda_safety * total


def compute_original_cost(bitstring, instance, var_to_index):
    processing = compute_processing_cost(bitstring, instance, var_to_index)
    workload = compute_workload_cost(bitstring, instance, var_to_index)
    ergonomic = compute_ergonomic_cost(bitstring, instance, var_to_index)
    safety = compute_safety_cost(bitstring, instance, var_to_index)

    original_cost = processing + workload + ergonomic + safety

    return {
        "processing": processing,
        "workload": workload,
        "ergonomic": ergonomic,
        "safety": safety,
        "original_cost": original_cost
    }
