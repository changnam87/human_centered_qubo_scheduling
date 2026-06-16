from src.core.variables import get_x


def compute_assignment_penalty(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    P_assignment = instance["penalties"]["P_assignment"]

    penalty = 0

    for operation in operations:
        assigned_count = 0

        for resource in resources:
            assigned_count += get_x(bitstring, operation, resource, var_to_index)

        violation = assigned_count - 1
        penalty += violation ** 2

    return P_assignment * penalty


def compute_skill_penalty(bitstring, instance, var_to_index):
    operations = instance["operations"]
    resources = instance["resources"]
    skill_compatibility = instance["skill_compatibility"]
    P_skill = instance["penalties"]["P_skill"]

    penalty = 0

    for operation in operations:
        for resource in resources:
            x = get_x(bitstring, operation, resource, var_to_index)

            if skill_compatibility[operation][resource] == 0:
                penalty += x

    return P_skill * penalty


def compute_robot_utilization_penalty(bitstring, instance, var_to_index):
    """
    QUBO-compatible robot utilization penalty.

    Instead of using a conditional rule such as:
        if robot_use == 0: penalty
        else: penalty = 0

    we use a quadratic target-utilization penalty:
        P_robot * (robot_use - target)^2

    For toy_v1:
        target = 1

    This means the model prefers using the robot for approximately one operation.
    """
    operations = instance["operations"]

    P_robot = instance["penalties"]["P_robot_utilization"]
    target = instance["penalties"]["robot_utilization_target"]

    robot_use = 0

    for operation in operations:
        robot_use += get_x(bitstring, operation, "R", var_to_index)

    violation = robot_use - target
    penalty = P_robot * (violation ** 2)

    return penalty


def compute_total_penalty(bitstring, instance, var_to_index):
    assignment_penalty = compute_assignment_penalty(bitstring, instance, var_to_index)
    skill_penalty = compute_skill_penalty(bitstring, instance, var_to_index)
    robot_utilization_penalty = compute_robot_utilization_penalty(
        bitstring,
        instance,
        var_to_index
    )

    total_penalty = (
        assignment_penalty
        + skill_penalty
        + robot_utilization_penalty
    )

    return {
        "assignment_penalty": assignment_penalty,
        "skill_penalty": skill_penalty,
        "robot_utilization_penalty": robot_utilization_penalty,
        "total_penalty": total_penalty
    }
