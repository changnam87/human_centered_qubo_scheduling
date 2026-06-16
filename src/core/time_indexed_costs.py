from src.core.time_indexed_variables import get_x_time


def get_workers(instance):
    if "workers" in instance:
        return instance["workers"]
    if "H" in instance["resources"]:
        return ["H"]
    return []


def get_robots(instance):
    if "robots" in instance:
        return instance["robots"]
    if "R" in instance["resources"]:
        return ["R"]
    return []


def compute_time_indexed_processing_cost(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    processing_cost = instance["processing_cost"]
    lambda_processing = instance["weights"]["lambda_processing"]

    total = 0.0

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                x = get_x_time(bitstring, operation, resource, time, var_to_index)
                total += lambda_processing * processing_cost[operation][resource] * x

    return total


def compute_time_indexed_start_time_cost(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    lambda_start_time = instance["weights"]["lambda_start_time"]

    total = 0.0

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                x = get_x_time(bitstring, operation, resource, time, var_to_index)
                total += lambda_start_time * time * x

    return total


def compute_time_indexed_workload_cost(bitstring, instance, var_to_index):
    operations = instance["operations"]
    time_slots = instance["time_slots"]
    workers = get_workers(instance)

    workload_score = instance["workload_score"]
    lambda_workload = instance["weights"]["lambda_workload"]

    total = 0.0

    for operation in operations:
        for worker in workers:
            for time in time_slots:
                x = get_x_time(bitstring, operation, worker, time, var_to_index)
                total += lambda_workload * workload_score[operation] * x

    return total


def compute_time_indexed_ergonomic_cost(bitstring, instance, var_to_index):
    operations = instance["operations"]
    time_slots = instance["time_slots"]
    workers = get_workers(instance)

    ergonomic_risk = instance["ergonomic_risk"]
    lambda_ergonomic = instance["weights"]["lambda_ergonomic"]

    total = 0.0

    for operation in operations:
        for worker in workers:
            for time in time_slots:
                x = get_x_time(bitstring, operation, worker, time, var_to_index)
                total += lambda_ergonomic * ergonomic_risk[operation] * x

    return total


def compute_time_indexed_safety_cost(bitstring, instance, var_to_index):
    operations = instance["operations"]
    time_slots = instance["time_slots"]
    robots = get_robots(instance)

    # Toy v2 used robot_safety_risk; augmented benchmark uses safety_risk.
    if "robot_safety_risk" in instance:
        safety_risk = instance["robot_safety_risk"]
    else:
        safety_risk = instance["safety_risk"]

    lambda_safety = instance["weights"]["lambda_safety"]

    total = 0.0

    for operation in operations:
        for robot in robots:
            for time in time_slots:
                x = get_x_time(bitstring, operation, robot, time, var_to_index)
                total += lambda_safety * safety_risk[operation] * x

    return total


def compute_time_indexed_original_cost(bitstring, instance, var_to_index):
    processing = compute_time_indexed_processing_cost(bitstring, instance, var_to_index)
    start_time = compute_time_indexed_start_time_cost(bitstring, instance, var_to_index)
    workload = compute_time_indexed_workload_cost(bitstring, instance, var_to_index)
    ergonomic = compute_time_indexed_ergonomic_cost(bitstring, instance, var_to_index)
    safety = compute_time_indexed_safety_cost(bitstring, instance, var_to_index)

    original_cost = processing + start_time + workload + ergonomic + safety

    return {
        "processing": processing,
        "start_time": start_time,
        "workload": workload,
        "ergonomic": ergonomic,
        "safety": safety,
        "original_cost": original_cost
    }
