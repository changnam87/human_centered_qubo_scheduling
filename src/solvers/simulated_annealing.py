import numpy as np
import random


def simulated_annealing_qubo(
    Q,
    constant_offset=0.0,
    num_reads=100,
    num_steps=1000,
    initial_temperature=10.0,
    final_temperature=0.01,
    seed=None
):
    """
    Simulated annealing solver for a QUBO problem.

    QUBO energy:
        E(x) = x^T Q x + constant_offset

    Parameters
    ----------
    Q : numpy.ndarray
        QUBO matrix.
    constant_offset : float
        Constant offset in the QUBO objective.
    num_reads : int
        Number of independent annealing runs.
    num_steps : int
        Number of temperature steps per run.
    initial_temperature : float
        Starting temperature.
    final_temperature : float
        Ending temperature.
    seed : int or None
        Random seed.

    Returns
    -------
    dict
        Best solution and all read results.
    """

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    Q = np.array(Q, dtype=float)
    n = Q.shape[0]

    all_results = []

    best_bitstring = None
    best_energy = float("inf")

    for read in range(num_reads):
        # Random initial bitstring
        x = np.random.randint(0, 2, size=n)
        current_energy = qubo_energy(x, Q, constant_offset)

        read_best_x = x.copy()
        read_best_energy = current_energy

        for step in range(num_steps):
            temperature = geometric_temperature(
                step,
                num_steps,
                initial_temperature,
                final_temperature
            )

            # Pick one random bit to flip
            flip_index = np.random.randint(0, n)

            x_new = x.copy()
            x_new[flip_index] = 1 - x_new[flip_index]

            new_energy = qubo_energy(x_new, Q, constant_offset)
            delta = new_energy - current_energy

            # Accept if better
            if delta <= 0:
                accept = True
            else:
                # Accept worse solution with probability exp(-delta / T)
                accept_probability = np.exp(-delta / temperature)
                accept = np.random.rand() < accept_probability

            if accept:
                x = x_new
                current_energy = new_energy

                if current_energy < read_best_energy:
                    read_best_x = x.copy()
                    read_best_energy = current_energy

        if read_best_energy < best_energy:
            best_energy = read_best_energy
            best_bitstring = read_best_x.copy()

        all_results.append({
            "read": read,
            "best_bitstring": tuple(int(v) for v in read_best_x),
            "best_energy": float(read_best_energy)
        })

    return {
        "best_bitstring": tuple(int(v) for v in best_bitstring),
        "best_energy": float(best_energy),
        "all_results": all_results
    }


def qubo_energy(bitstring, Q, constant_offset=0.0):
    """
    Compute QUBO energy:
        E(x) = x^T Q x + constant_offset
    """
    x = np.array(bitstring, dtype=float)
    return float(x @ Q @ x + constant_offset)


def geometric_temperature(
    step,
    num_steps,
    initial_temperature,
    final_temperature
):
    """
    Geometric cooling schedule.

    T(step) decreases smoothly from initial_temperature to final_temperature.
    """
    if num_steps <= 1:
        return final_temperature

    fraction = step / (num_steps - 1)

    temperature = initial_temperature * (
        final_temperature / initial_temperature
    ) ** fraction

    return temperature
