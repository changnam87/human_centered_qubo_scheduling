import numpy as np


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


def get_safety_risk(instance):
    if "robot_safety_risk" in instance:
        return instance["robot_safety_risk"]
    return instance["safety_risk"]


def add_linear(Q, i, value):
    Q[i, i] += value


def add_quadratic(Q, i, j, value):
    if i == j:
        Q[i, i] += value
    else:
        Q[i, j] += value / 2.0
        Q[j, i] += value / 2.0


def intervals_overlap(start_a, end_a, start_b, end_b):
    return start_a < end_b and start_b < end_a


def build_time_indexed_qubo_matrix(instance, var_to_index, human_reward=0.0):
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    workers = get_workers(instance)
    robots = get_robots(instance)

    n = len(operations) * len(resources) * len(time_slots)
    Q = np.zeros((n, n))
    constant_offset = 0.0

    processing_cost = instance["processing_cost"]
    processing_time = instance["processing_time"]
    workload_score = instance["workload_score"]
    ergonomic_risk = instance["ergonomic_risk"]
    safety_risk = get_safety_risk(instance)
    skill_compatibility = instance["skill_compatibility"]
    precedence = instance["precedence"]
    planning_horizon = instance["planning_horizon"]

    lambda_processing = instance["weights"]["lambda_processing"]
    lambda_start_time = instance["weights"]["lambda_start_time"]
    lambda_workload = instance["weights"]["lambda_workload"]
    lambda_ergonomic = instance["weights"]["lambda_ergonomic"]
    lambda_safety = instance["weights"]["lambda_safety"]

    P_assignment_start = instance["penalties"]["P_assignment_start"]
    P_skill = instance["penalties"]["P_skill"]
    P_precedence = instance["penalties"]["P_precedence"]
    P_resource_overlap = instance["penalties"]["P_resource_overlap"]
    P_robot = instance["penalties"]["P_robot_utilization"]
    robot_target = instance["penalties"]["robot_utilization_target"]

    # 1. Processing cost
    for operation in operations:
        for resource in resources:
            for time in time_slots:
                i = var_to_index[(operation, resource, time)]
                coeff = lambda_processing * processing_cost[operation][resource]
                add_linear(Q, i, coeff)

    # 2. Start-time cost
    for operation in operations:
        for resource in resources:
            for time in time_slots:
                i = var_to_index[(operation, resource, time)]
                coeff = lambda_start_time * time
                add_linear(Q, i, coeff)

    # 3. Workload cost for all human workers
    for operation in operations:
        for worker in workers:
            for time in time_slots:
                i = var_to_index[(operation, worker, time)]
                coeff = lambda_workload * workload_score[operation]
                add_linear(Q, i, coeff)

    # 4. Ergonomic risk cost for all human workers
    for operation in operations:
        for worker in workers:
            for time in time_slots:
                i = var_to_index[(operation, worker, time)]
                coeff = lambda_ergonomic * ergonomic_risk[operation]
                add_linear(Q, i, coeff)

    # 4b. Soft human-involvement reward for all human workers
    #
    # Because the QUBO minimizes the objective, a positive reward is
    # implemented as a negative linear coefficient on human-assignment
    # variables.
    if human_reward != 0.0:
        for operation in operations:
            for worker in workers:
                for time in time_slots:
                    i = var_to_index[(operation, worker, time)]
                    coeff = -human_reward
                    add_linear(Q, i, coeff)

    # 5. Safety cost for all robots
    for operation in operations:
        for robot in robots:
            for time in time_slots:
                i = var_to_index[(operation, robot, time)]
                coeff = lambda_safety * safety_risk[operation]
                add_linear(Q, i, coeff)

    # 6. Assignment-start penalty
    for operation in operations:
        indices = []

        for resource in resources:
            for time in time_slots:
                indices.append(var_to_index[(operation, resource, time)])

        for i in indices:
            add_linear(Q, i, -P_assignment_start)

        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i = indices[a]
                j = indices[b]
                add_quadratic(Q, i, j, 2 * P_assignment_start)

        constant_offset += P_assignment_start

    # 7. Skill compatibility penalty
    for operation in operations:
        for resource in resources:
            for time in time_slots:
                if skill_compatibility[operation][resource] == 0:
                    i = var_to_index[(operation, resource, time)]
                    add_linear(Q, i, P_skill)

    # 8. Horizon penalty
    for operation in operations:
        for resource in resources:
            for time in time_slots:
                duration = processing_time[operation][resource]
                end_time = time + duration

                if end_time > planning_horizon:
                    violation = end_time - planning_horizon
                    coeff = P_resource_overlap * (violation ** 2)
                    i = var_to_index[(operation, resource, time)]
                    add_linear(Q, i, coeff)

    # 9. Precedence penalty
    for before, after in precedence:
        for before_resource in resources:
            for before_time in time_slots:
                before_duration = processing_time[before][before_resource]
                before_end = before_time + before_duration
                i = var_to_index[(before, before_resource, before_time)]

                for after_resource in resources:
                    for after_time in time_slots:
                        if before_end > after_time:
                            j = var_to_index[(after, after_resource, after_time)]
                            add_quadratic(Q, i, j, P_precedence)

    # 10. Resource-overlap penalty
    for a in range(len(operations)):
        for b in range(a + 1, len(operations)):
            operation_a = operations[a]
            operation_b = operations[b]

            for resource in resources:
                for time_a in time_slots:
                    duration_a = processing_time[operation_a][resource]
                    start_a = time_a
                    end_a = start_a + duration_a
                    i = var_to_index[(operation_a, resource, time_a)]

                    for time_b in time_slots:
                        duration_b = processing_time[operation_b][resource]
                        start_b = time_b
                        end_b = start_b + duration_b

                        if intervals_overlap(start_a, end_a, start_b, end_b):
                            j = var_to_index[(operation_b, resource, time_b)]
                            add_quadratic(Q, i, j, P_resource_overlap)

    # 11. Robot-utilization penalty for all robots
    robot_indices = []

    for operation in operations:
        for robot in robots:
            for time in time_slots:
                robot_indices.append(var_to_index[(operation, robot, time)])

    if len(robot_indices) > 0:
        linear_coeff = P_robot * (1 - 2 * robot_target)

        for i in robot_indices:
            add_linear(Q, i, linear_coeff)

        for a in range(len(robot_indices)):
            for b in range(a + 1, len(robot_indices)):
                i = robot_indices[a]
                j = robot_indices[b]
                add_quadratic(Q, i, j, 2 * P_robot)

        constant_offset += P_robot * (robot_target ** 2)

    return Q, constant_offset


def time_indexed_qubo_energy(bitstring, Q, constant_offset=0.0):
    x = np.array(bitstring, dtype=float)
    return float(x @ Q @ x + constant_offset)
