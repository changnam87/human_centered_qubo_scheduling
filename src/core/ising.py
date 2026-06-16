import numpy as np


def qubo_to_ising(Q, constant_offset=0.0):
    """
    Convert QUBO matrix Q into Ising parameters.

    QUBO energy:
        E(x) = x^T Q x + constant_offset

    Ising substitution:
        x_i = (1 + z_i) / 2
        z_i in {-1, +1}

    Ising energy:
        H(z) = sum_i h_i z_i + sum_{i<j} J_ij z_i z_j + ising_offset

    Notes
    -----
    This function assumes Q is symmetric and energy is computed as x^T Q x.
    """

    Q = np.array(Q, dtype=float)
    n = Q.shape[0]

    h = np.zeros(n)
    J = np.zeros((n, n))
    ising_offset = float(constant_offset)

    # Diagonal terms:
    # Q_ii x_i = Q_ii * (1 + z_i)/2
    # contributes:
    #   offset += Q_ii/2
    #   h_i    += Q_ii/2
    for i in range(n):
        qii = Q[i, i]
        ising_offset += qii / 2.0
        h[i] += qii / 2.0

    # Off-diagonal terms:
    # Since Q is symmetric and E = x^T Q x,
    # for i<j, the effective QUBO coefficient is:
    #   q_eff = Q_ij + Q_ji = 2 Q_ij
    #
    # q_eff x_i x_j
    # = q_eff * (1 + z_i)(1 + z_j) / 4
    # = q_eff/4
    #   + q_eff/4 z_i
    #   + q_eff/4 z_j
    #   + q_eff/4 z_i z_j
    for i in range(n):
        for j in range(i + 1, n):
            q_eff = Q[i, j] + Q[j, i]

            if abs(q_eff) > 1e-12:
                ising_offset += q_eff / 4.0
                h[i] += q_eff / 4.0
                h[j] += q_eff / 4.0
                J[i, j] += q_eff / 4.0
                J[j, i] += q_eff / 4.0

    return h, J, ising_offset


def binary_to_spin(bitstring):
    """
    Convert binary bitstring x in {0,1} to spin vector z in {-1,+1}.

    Mapping:
        x = 0 -> z = -1
        x = 1 -> z = +1
    """
    x = np.array(bitstring, dtype=int)
    z = 2 * x - 1
    return z


def ising_energy(spins, h, J, ising_offset=0.0):
    """
    Compute Ising energy:
        H(z) = sum_i h_i z_i + sum_{i<j} J_ij z_i z_j + offset

    J is assumed symmetric, but we only sum i<j to avoid double counting.
    """
    z = np.array(spins, dtype=float)
    n = len(z)

    energy = float(ising_offset)

    for i in range(n):
        energy += h[i] * z[i]

    for i in range(n):
        for j in range(i + 1, n):
            energy += J[i, j] * z[i] * z[j]

    return float(energy)
