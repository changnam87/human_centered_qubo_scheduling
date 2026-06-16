from src.core.variables import get_x


def is_assignment_feasible(bitstring, instance, var_to_index):
    """
    Feasible if:
    1. Each operation is assigned to exactly one resource.
    2. No operation is assigned to an incompatible resource.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    skill_compatibility = instance["skill_compatibility"]

    # Each operation must be assigned to exactly one resource
    for operation in operations:
        assigned_count = 0

        for resource in resources:
            assigned_count += get_x(bitstring, operation, resource, var_to_index)

        if assigned_count != 1:
            return False

    # Skill compatibility check
    for operation in operations:
        for resource in resources:
            x = get_x(bitstring, operation, resource, var_to_index)

            if x == 1 and skill_compatibility[operation][resource] == 0:
                return False

    return True
