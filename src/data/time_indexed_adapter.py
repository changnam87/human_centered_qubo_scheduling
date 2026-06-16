import json
from pathlib import Path


def estimate_planning_horizon(instance, buffer_factor=1.5):
    """
    Estimate a reasonable planning horizon for a time-indexed scheduling model.

    We use the sum of the minimum compatible processing times over all operations
    and multiply it by a buffer factor.

    This is conservative enough for small benchmark-derived instances.
    """
    operations = instance["operations"]
    resources = instance["resources"]
    processing_time = instance["processing_time"]
    skill_compatibility = instance["skill_compatibility"]

    total_min_processing_time = 0

    for operation in operations:
        compatible_times = []

        for resource in resources:
            if skill_compatibility[operation][resource] == 1:
                compatible_times.append(processing_time[operation][resource])

        if not compatible_times:
            raise ValueError(f"No compatible resource found for operation {operation}")

        total_min_processing_time += min(compatible_times)

    horizon = int(round(buffer_factor * total_min_processing_time))

    # Ensure horizon is at least large enough for small instances
    horizon = max(horizon, total_min_processing_time)

    return horizon


def add_time_indexed_fields(instance, planning_horizon=None, buffer_factor=1.5):
    """
    Add planning_horizon and time_slots to an augmented benchmark instance.

    Parameters
    ----------
    instance : dict
        Human-centered augmented instance.
    planning_horizon : int or None
        If provided, use this horizon directly.
        If None, estimate horizon automatically.
    buffer_factor : float
        Used only when planning_horizon is None.

    Returns
    -------
    dict
        Updated instance with time-indexed fields.
    """
    updated = dict(instance)

    if planning_horizon is None:
        planning_horizon = estimate_planning_horizon(
            instance,
            buffer_factor=buffer_factor
        )

    updated["planning_horizon"] = planning_horizon
    updated["time_slots"] = list(range(planning_horizon))

    updated["time_indexed_adapter"] = {
        "planning_horizon_method": "sum_min_compatible_processing_time_times_buffer",
        "buffer_factor": buffer_factor
    }

    return updated


def load_json(path):
    path = Path(path)

    with open(path, "r") as f:
        return json.load(f)


def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path


def print_time_indexed_instance_summary(instance):
    print("=== Time-indexed augmented instance summary ===")
    print("Instance:", instance["instance_name"])
    print("Operations:", len(instance["operations"]))
    print("Resources:", len(instance["resources"]))
    print("Machines:", len(instance.get("machines", [])))
    print("Workers:", len(instance.get("workers", [])))
    print("Robots:", len(instance.get("robots", [])))
    print("Planning horizon:", instance["planning_horizon"])
    print("Time slots:", len(instance["time_slots"]))
    print("Binary variables:", len(instance["operations"]) * len(instance["resources"]) * len(instance["time_slots"]))
