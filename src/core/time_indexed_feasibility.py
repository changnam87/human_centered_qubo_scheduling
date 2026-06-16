from src.core.time_indexed_variables import get_x_time


def decode_time_indexed_solution(bitstring, instance, var_to_index):
    """
    Decode a time-indexed bitstring into selected assignments.

    Returns
    -------
    schedule : dict
        Example:
        {
            "O11": [{"resource": "M", "start": 0, "duration": 1, "end": 1}],
            ...
        }
    """
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]
    processing_time = instance["processing_time"]

    schedule = {}

    for operation in operations:
        selected = []

        for resource in resources:
            for time in time_slots:
                x = get_x_time(bitstring, operation, resource, time, var_to_index)

                if x == 1:
                    duration = processing_time[operation][resource]
                    end_time = time + duration

                    selected.append({
                        "resource": resource,
                        "start": time,
                        "duration": duration,
                        "end": end_time
                    })

        schedule[operation] = selected

    return schedule


def check_assignment_start_once(bitstring, instance, var_to_index):
    """
    Each operation must start exactly once across all resources and time slots.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    violations = []

    for operation in operations:
        count = 0

        for resource in resources:
            for time in time_slots:
                count += get_x_time(bitstring, operation, resource, time, var_to_index)

        if count != 1:
            violations.append({
                "operation": operation,
                "start_count": count,
                "message": f"{operation} starts {count} times, but must start exactly once."
            })

    return violations


def check_skill_compatibility(bitstring, instance, var_to_index):
    """
    Selected operation-resource-time assignments must be skill compatible.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]
    skill_compatibility = instance["skill_compatibility"]

    violations = []

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                x = get_x_time(bitstring, operation, resource, time, var_to_index)

                if x == 1 and skill_compatibility[operation][resource] == 0:
                    violations.append({
                        "operation": operation,
                        "resource": resource,
                        "time": time,
                        "message": f"{operation} is assigned to incompatible resource {resource} at time {time}."
                    })

    return violations


def check_horizon(bitstring, instance, var_to_index):
    """
    Selected operations must finish within the planning horizon.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]
    processing_time = instance["processing_time"]
    planning_horizon = instance["planning_horizon"]

    violations = []

    for operation in operations:
        for resource in resources:
            for time in time_slots:
                x = get_x_time(bitstring, operation, resource, time, var_to_index)

                if x == 1:
                    duration = processing_time[operation][resource]
                    end_time = time + duration

                    if end_time > planning_horizon:
                        violations.append({
                            "operation": operation,
                            "resource": resource,
                            "start": time,
                            "duration": duration,
                            "end": end_time,
                            "planning_horizon": planning_horizon,
                            "message": f"{operation} on {resource} ends at {end_time}, beyond horizon {planning_horizon}."
                        })

    return violations


def get_operation_start_end(schedule, operation):
    """
    Return start and end time for an operation if it has exactly one selected assignment.

    Returns
    -------
    tuple or None
        (start, end, resource) if exactly one assignment exists.
        None otherwise.
    """
    selected = schedule.get(operation, [])

    if len(selected) != 1:
        return None

    item = selected[0]
    return item["start"], item["end"], item["resource"]


def check_precedence(bitstring, instance, var_to_index):
    """
    Check precedence constraints.

    For each (before, after):
        end(before) <= start(after)
    """
    precedence = instance["precedence"]

    schedule = decode_time_indexed_solution(bitstring, instance, var_to_index)

    violations = []

    for before, after in precedence:
        before_info = get_operation_start_end(schedule, before)
        after_info = get_operation_start_end(schedule, after)

        # If operation is not uniquely assigned, assignment checker handles it.
        # Skip here to avoid duplicate confusing errors.
        if before_info is None or after_info is None:
            continue

        before_start, before_end, before_resource = before_info
        after_start, after_end, after_resource = after_info

        if before_end > after_start:
            violations.append({
                "before": before,
                "after": after,
                "before_start": before_start,
                "before_end": before_end,
                "after_start": after_start,
                "after_end": after_end,
                "message": f"Precedence violated: {before} ends at {before_end}, but {after} starts at {after_start}."
            })

    return violations


def intervals_overlap(start_a, end_a, start_b, end_b):
    """
    Return True if [start_a, end_a) overlaps with [start_b, end_b).
    """
    return start_a < end_b and start_b < end_a


def check_resource_overlap(bitstring, instance, var_to_index):
    """
    Check whether two selected operations overlap on the same resource.
    """
    schedule = decode_time_indexed_solution(bitstring, instance, var_to_index)
    operations = instance["operations"]

    violations = []

    selected_operations = []

    for operation in operations:
        selected = schedule[operation]

        # Only uniquely selected operations can be checked clearly.
        # Assignment-start checker handles missing/multiple starts.
        if len(selected) == 1:
            item = selected[0]
            selected_operations.append({
                "operation": operation,
                "resource": item["resource"],
                "start": item["start"],
                "end": item["end"]
            })

    for i in range(len(selected_operations)):
        for j in range(i + 1, len(selected_operations)):
            a = selected_operations[i]
            b = selected_operations[j]

            if a["resource"] != b["resource"]:
                continue

            if intervals_overlap(a["start"], a["end"], b["start"], b["end"]):
                violations.append({
                    "operation_a": a["operation"],
                    "operation_b": b["operation"],
                    "resource": a["resource"],
                    "a_start": a["start"],
                    "a_end": a["end"],
                    "b_start": b["start"],
                    "b_end": b["end"],
                    "message": (
                        f"Resource overlap: {a['operation']} and {b['operation']} "
                        f"overlap on {a['resource']}."
                    )
                })

    return violations


def check_time_indexed_feasibility(bitstring, instance, var_to_index):
    """
    Run all feasibility checks for Toy v2.

    Returns
    -------
    dict
        Feasibility report.
    """
    assignment_violations = check_assignment_start_once(bitstring, instance, var_to_index)
    skill_violations = check_skill_compatibility(bitstring, instance, var_to_index)
    horizon_violations = check_horizon(bitstring, instance, var_to_index)
    precedence_violations = check_precedence(bitstring, instance, var_to_index)
    resource_overlap_violations = check_resource_overlap(bitstring, instance, var_to_index)

    all_violations = (
        assignment_violations
        + skill_violations
        + horizon_violations
        + precedence_violations
        + resource_overlap_violations
    )

    feasible = len(all_violations) == 0

    return {
        "feasible": feasible,
        "num_violations": len(all_violations),
        "assignment_violations": assignment_violations,
        "skill_violations": skill_violations,
        "horizon_violations": horizon_violations,
        "precedence_violations": precedence_violations,
        "resource_overlap_violations": resource_overlap_violations,
        "all_violations": all_violations,
        "schedule": decode_time_indexed_solution(bitstring, instance, var_to_index)
    }
