from src.core.time_indexed_variables import get_x_time
from src.core.time_indexed_feasibility import intervals_overlap


def get_robots(instance):
    if "robots" in instance:
        return instance["robots"]
    if "R" in instance["resources"]:
        return ["R"]
    return []


def compute_assignment_start_penalty(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    P = instance["penalties"]["P_assignment_start"]

    penalty = 0.0

    for operation in operations:
        count = 0

        for resource in resources:
            for time in time_slots:
                count += get_x_time(bitstring, operation, resource, time, var_to_index)

        violation = count - 1
        penalty += P * (violation ** 2)

    return penalty


def compute_time_indexed_skill_penalty(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    skill_compatibility = instance["skill_compatibility"]
    P = instance["penalties"]["P_skill"]

    penalty = 0.0

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                x = get_x_time(bitstring, operation, resource, time, var_to_index)

                if skill_compatibility[operation][resource] == 0:
                    penalty += P * x

    return penalty


def compute_horizon_penalty(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    processing_time = instance["processing_time"]
    planning_horizon = instance["planning_horizon"]

    P = instance["penalties"]["P_resource_overlap"]

    penalty = 0.0

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                x = get_x_time(bitstring, operation, resource, time, var_to_index)

                if x == 1:
                    duration = processing_time[operation][resource]
                    end_time = time + duration

                    if end_time > planning_horizon:
                        violation = end_time - planning_horizon
                        penalty += P * (violation ** 2)

    return penalty


def compute_precedence_penalty(bitstring, instance, var_to_index):
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    precedence = instance["precedence"]
    processing_time = instance["processing_time"]

    P = instance["penalties"]["P_precedence"]

    penalty = 0.0

    for before, after in precedence:
        for before_resource in resources:
            for before_time in time_slots:
                x_before = get_x_time(
                    bitstring,
                    before,
                    before_resource,
                    before_time,
                    var_to_index
                )

                if x_before == 0:
                    continue

                before_duration = processing_time[before][before_resource]
                before_end = before_time + before_duration

                for after_resource in resources:
                    for after_time in time_slots:
                        x_after = get_x_time(
                            bitstring,
                            after,
                            after_resource,
                            after_time,
                            var_to_index
                        )

                        if x_after == 0:
                            continue

                        if before_end > after_time:
                            penalty += P * x_before * x_after

    return penalty


def compute_resource_overlap_penalty(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    processing_time = instance["processing_time"]

    P = instance["penalties"]["P_resource_overlap"]

    penalty = 0.0

    for i in range(len(operations)):
        for j in range(i + 1, len(operations)):
            operation_a = operations[i]
            operation_b = operations[j]

            for resource in resources:
                for time_a in time_slots:
                    x_a = get_x_time(
                        bitstring,
                        operation_a,
                        resource,
                        time_a,
                        var_to_index
                    )

                    if x_a == 0:
                        continue

                    duration_a = processing_time[operation_a][resource]
                    start_a = time_a
                    end_a = start_a + duration_a

                    for time_b in time_slots:
                        x_b = get_x_time(
                            bitstring,
                            operation_b,
                            resource,
                            time_b,
                            var_to_index
                        )

                        if x_b == 0:
                            continue

                        duration_b = processing_time[operation_b][resource]
                        start_b = time_b
                        end_b = start_b + duration_b

                        if intervals_overlap(start_a, end_a, start_b, end_b):
                            penalty += P * x_a * x_b

    return penalty


def compute_time_indexed_robot_utilization_penalty(bitstring, instance, var_to_index):
    operations = instance["operations"]
    time_slots = instance["time_slots"]
    robots = get_robots(instance)

    P = instance["penalties"]["P_robot_utilization"]
    target = instance["penalties"]["robot_utilization_target"]

    robot_use = 0

    for operation in operations:
        for robot in robots:
            for time in time_slots:
                robot_use += get_x_time(bitstring, operation, robot, time, var_to_index)

    violation = robot_use - target

    return P * (violation ** 2)


def compute_time_indexed_total_penalty(bitstring, instance, var_to_index):
    assignment_start_penalty = compute_assignment_start_penalty(
        bitstring,
        instance,
        var_to_index
    )

    skill_penalty = compute_time_indexed_skill_penalty(
        bitstring,
        instance,
        var_to_index
    )

    horizon_penalty = compute_horizon_penalty(
        bitstring,
        instance,
        var_to_index
    )

    precedence_penalty = compute_precedence_penalty(
        bitstring,
        instance,
        var_to_index
    )

    resource_overlap_penalty = compute_resource_overlap_penalty(
        bitstring,
        instance,
        var_to_index
    )

    robot_utilization_penalty = compute_time_indexed_robot_utilization_penalty(
        bitstring,
        instance,
        var_to_index
    )

    total_penalty = (
        assignment_start_penalty
        + skill_penalty
        + horizon_penalty
        + precedence_penalty
        + resource_overlap_penalty
        + robot_utilization_penalty
    )

    return {
        "assignment_start_penalty": assignment_start_penalty,
        "skill_penalty": skill_penalty,
        "horizon_penalty": horizon_penalty,
        "precedence_penalty": precedence_penalty,
        "resource_overlap_penalty": resource_overlap_penalty,
        "robot_utilization_penalty": robot_utilization_penalty,
        "total_penalty": total_penalty
    }
