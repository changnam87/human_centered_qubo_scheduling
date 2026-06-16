import random
import math
from copy import deepcopy

from src.core.time_indexed_evaluate import evaluate_time_indexed_solution


def build_candidate_starts(instance):
    """
    Build feasible candidate starts for each operation based on:
    - skill compatibility
    - horizon feasibility

    This does not check precedence or resource overlap.
    Those are handled by the evaluator penalty.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]
    processing_time = instance["processing_time"]
    skill_compatibility = instance["skill_compatibility"]
    planning_horizon = instance["planning_horizon"]

    candidates = {}

    for operation in operations:
        candidates[operation] = []

        for resource in resources:
            if skill_compatibility[operation][resource] == 0:
                continue

            for time in time_slots:
                duration = processing_time[operation][resource]
                end_time = time + duration

                if end_time <= planning_horizon:
                    candidates[operation].append((resource, time))

        if len(candidates[operation]) == 0:
            raise ValueError(f"No valid candidate start found for {operation}")

    return candidates


def bitstring_to_assignment(bitstring, instance, var_to_index):
    """
    Convert bitstring to operation -> (resource, time).

    Assumes each operation has exactly one selected start.
    If multiple are selected, the first is used.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    assignment = {}

    for operation in operations:
        selected = []

        for resource in resources:
            for time in time_slots:
                idx = var_to_index[(operation, resource, time)]
                if bitstring[idx] == 1:
                    selected.append((resource, time))

        if len(selected) > 0:
            assignment[operation] = selected[0]
        else:
            assignment[operation] = None

    return assignment


def assignment_to_bitstring(assignment, instance, var_to_index):
    """
    Convert operation -> (resource, time) assignment into full bitstring.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    time_slots = instance["time_slots"]

    num_variables = len(operations) * len(resources) * len(time_slots)
    bitstring = [0] * num_variables

    for operation, value in assignment.items():
        if value is None:
            continue

        resource, time = value
        idx = var_to_index[(operation, resource, time)]
        bitstring[idx] = 1

    return bitstring


def random_feasible_assignment_seed(instance, candidates, seed=None):
    """
    Create assignment-start-valid random solution.

    It guarantees each operation starts exactly once and uses only compatible
    resource/time candidates, but may violate precedence/resource overlap.
    """
    if seed is not None:
        random.seed(seed)

    assignment = {}

    for operation in instance["operations"]:
        assignment[operation] = random.choice(candidates[operation])

    return assignment


def geometric_temperature(step, num_steps, initial_temperature, final_temperature):
    if num_steps <= 1:
        return final_temperature

    fraction = step / (num_steps - 1)
    return initial_temperature * (final_temperature / initial_temperature) ** fraction


def seeded_time_indexed_local_search(
    instance,
    var_to_index,
    seed_bitstring=None,
    num_reads=20,
    num_steps=1000,
    initial_temperature=10.0,
    final_temperature=0.01,
    random_seed=2026
):
    """
    Structure-aware seeded local search / annealing.

    Move type:
        Pick one operation.
        Reassign it to one compatible resource-time candidate.

    This preserves:
        each operation starts exactly once
        skill compatibility
        horizon feasibility

    It searches over schedule structure rather than arbitrary 1836-bit flips.
    """
    random.seed(random_seed)

    candidates = build_candidate_starts(instance)

    all_results = []

    global_best_bitstring = None
    global_best_result = None
    global_best_cost = float("inf")

    for read in range(num_reads):
        if seed_bitstring is not None and read == 0:
            current_assignment = bitstring_to_assignment(
                seed_bitstring,
                instance,
                var_to_index
            )
        elif seed_bitstring is not None:
            # Start from seed, then perturb a few operations
            current_assignment = bitstring_to_assignment(
                seed_bitstring,
                instance,
                var_to_index
            )

            num_perturb = max(1, len(instance["operations"]) // 4)

            for _ in range(num_perturb):
                operation = random.choice(instance["operations"])
                current_assignment[operation] = random.choice(candidates[operation])
        else:
            current_assignment = random_feasible_assignment_seed(
                instance,
                candidates
            )

        current_bitstring = assignment_to_bitstring(
            current_assignment,
            instance,
            var_to_index
        )

        current_result = evaluate_time_indexed_solution(
            current_bitstring,
            instance,
            var_to_index
        )

        current_cost = current_result["total_cost"]

        read_best_assignment = deepcopy(current_assignment)
        read_best_bitstring = current_bitstring[:]
        read_best_result = current_result
        read_best_cost = current_cost

        for step in range(num_steps):
            temperature = geometric_temperature(
                step,
                num_steps,
                initial_temperature,
                final_temperature
            )

            new_assignment = deepcopy(current_assignment)

            operation = random.choice(instance["operations"])
            old_value = new_assignment[operation]
            new_value = random.choice(candidates[operation])

            # Avoid no-op if possible
            if len(candidates[operation]) > 1:
                while new_value == old_value:
                    new_value = random.choice(candidates[operation])

            new_assignment[operation] = new_value

            new_bitstring = assignment_to_bitstring(
                new_assignment,
                instance,
                var_to_index
            )

            new_result = evaluate_time_indexed_solution(
                new_bitstring,
                instance,
                var_to_index
            )

            new_cost = new_result["total_cost"]

            delta = new_cost - current_cost

            if delta <= 0:
                accept = True
            else:
                accept_probability = math.exp(-delta / max(temperature, 1e-12))
                accept = random.random() < accept_probability

            if accept:
                current_assignment = new_assignment
                current_bitstring = new_bitstring
                current_result = new_result
                current_cost = new_cost

                if current_cost < read_best_cost:
                    read_best_assignment = deepcopy(current_assignment)
                    read_best_bitstring = current_bitstring[:]
                    read_best_result = current_result
                    read_best_cost = current_cost

        if read_best_cost < global_best_cost:
            global_best_bitstring = read_best_bitstring[:]
            global_best_result = read_best_result
            global_best_cost = read_best_cost

        all_results.append({
            "read": read,
            "best_bitstring": tuple(int(v) for v in read_best_bitstring),
            "best_cost": float(read_best_cost),
            "feasible": read_best_result["feasible"],
            "num_violations": read_best_result["num_violations"],
            "total_penalty": read_best_result["total_penalty"],
            "result": read_best_result
        })

    return {
        "best_bitstring": tuple(int(v) for v in global_best_bitstring),
        "best_cost": float(global_best_cost),
        "best_result": global_best_result,
        "all_results": all_results
    }
