import numpy as np


def add_linear(Q, i, value):
    """
    Add a linear term value * x_i to QUBO matrix.

    Since x_i is binary, x_i^2 = x_i.
    Therefore, a linear term is stored on the diagonal Q[i, i].
    """
    Q[i, i] += value


def add_quadratic(Q, i, j, value):
    """
    Add a quadratic term value * x_i * x_j to QUBO matrix.

    We compute energy as:
        E(x) = x^T Q x

    For i != j, x^T Q x counts both Q[i,j] and Q[j,i].
    Therefore, we split the coefficient equally.
    """
    if i == j:
        Q[i, i] += value
    else:
        Q[i, j] += value / 2.0
        Q[j, i] += value / 2.0


def build_qubo_matrix(instance, var_to_index):
    """
    Build QUBO matrix Q for the toy human-centered assignment problem.

    Energy:
        E(x) = x^T Q x + constant_offset

    Terms included:
    1. Processing cost
    2. Human workload cost
    3. Human ergonomic risk cost
    4. Robot safety cost
    5. Assignment feasibility penalty
    6. Skill compatibility penalty
    7. Robot utilization penalty

    Robot utilization penalty:
        P_robot * (sum_o x[o,R] - target)^2
    """
    operations = instance["operations"]
    resources = instance["resources"]

    n = len(operations) * len(resources)
    Q = np.zeros((n, n))
    constant_offset = 0.0

    processing_cost = instance["processing_cost"]
    workload_score = instance["workload_score"]
    ergonomic_risk = instance["ergonomic_risk"]
    robot_safety_risk = instance["robot_safety_risk"]
    skill_compatibility = instance["skill_compatibility"]

    lambda_workload = instance["weights"]["lambda_workload"]
    lambda_ergonomic = instance["weights"]["lambda_ergonomic"]
    lambda_safety = instance["weights"]["lambda_safety"]

    P_assignment = instance["penalties"]["P_assignment"]
    P_skill = instance["penalties"]["P_skill"]
    P_robot = instance["penalties"]["P_robot_utilization"]
    robot_target = instance["penalties"]["robot_utilization_target"]

    # ============================================================
    # 1. Processing cost
    # ============================================================
    # sum_o sum_r c[o,r] x[o,r]
    for operation in operations:
        for resource in resources:
            i = var_to_index[(operation, resource)]
            add_linear(Q, i, processing_cost[operation][resource])

    # ============================================================
    # 2. Human workload cost
    # ============================================================
    # lambda_workload * sum_o workload[o] x[o,H]
    for operation in operations:
        i = var_to_index[(operation, "H")]
        add_linear(Q, i, lambda_workload * workload_score[operation])

    # ============================================================
    # 3. Human ergonomic risk cost
    # ============================================================
    # lambda_ergonomic * sum_o ergonomic[o] x[o,H]
    for operation in operations:
        i = var_to_index[(operation, "H")]
        add_linear(Q, i, lambda_ergonomic * ergonomic_risk[operation])

    # ============================================================
    # 4. Robot safety cost
    # ============================================================
    # lambda_safety * sum_o safety[o] x[o,R]
    for operation in operations:
        i = var_to_index[(operation, "R")]
        add_linear(Q, i, lambda_safety * robot_safety_risk[operation])

    # ============================================================
    # 5. Assignment feasibility penalty
    # ============================================================
    # For each operation:
    #     P_assignment * (sum_r x[o,r] - 1)^2
    #
    # Expanded:
    #     P_assignment * [
    #       sum_r x[o,r]
    #       + 2 sum_{r<r'} x[o,r]x[o,r']
    #       - 2 sum_r x[o,r]
    #       + 1
    #     ]
    #
    # Since x_i^2 = x_i:
    #     linear coefficient: -P_assignment
    #     pairwise coefficient: 2P_assignment
    #     constant offset: P_assignment
    for operation in operations:
        indices = []

        for resource in resources:
            indices.append(var_to_index[(operation, resource)])

        for i in indices:
            add_linear(Q, i, -P_assignment)

        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i = indices[a]
                j = indices[b]
                add_quadratic(Q, i, j, 2 * P_assignment)

        constant_offset += P_assignment

    # ============================================================
    # 6. Skill compatibility penalty
    # ============================================================
    # P_skill * sum_o sum_r (1 - skill[o,r]) x[o,r]
    for operation in operations:
        for resource in resources:
            if skill_compatibility[operation][resource] == 0:
                i = var_to_index[(operation, resource)]
                add_linear(Q, i, P_skill)

    # ============================================================
    # 7. Robot utilization penalty
    # ============================================================
    # P_robot * (sum_o x[o,R] - robot_target)^2
    #
    # Let S = sum_o x[o,R].
    #
    # P_robot * (S - target)^2
    # = P_robot * (S^2 - 2 target S + target^2)
    #
    # Since S^2 = sum_i x_i + 2 sum_{i<j} x_i x_j:
    #
    # linear coefficient for each robot variable:
    #     P_robot * (1 - 2 target)
    #
    # quadratic coefficient for each pair of robot variables:
    #     2 * P_robot
    #
    # constant offset:
    #     P_robot * target^2
    robot_indices = []

    for operation in operations:
        robot_indices.append(var_to_index[(operation, "R")])

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


def qubo_energy(bitstring, Q, constant_offset=0.0):
    """
    Compute QUBO energy:
        E(x) = x^T Q x + constant_offset
    """
    x = np.array(bitstring, dtype=float)
    return float(x @ Q @ x + constant_offset)


def print_qubo_matrix(Q, variable_names):
    """
    Print QUBO matrix with variable labels.
    """
    print("=== QUBO Matrix Q ===")
    print("Variables:")
    for i, name in enumerate(variable_names):
        print(i, name)

    print()
    print(Q)
