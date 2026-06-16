import json
from pathlib import Path


def load_instance(instance_path):
    """
    Load a scheduling instance from a JSON file.

    Parameters
    ----------
    instance_path : str or Path
        Path to the JSON instance file.

    Returns
    -------
    dict
        Instance data.
    """
    instance_path = Path(instance_path)

    with open(instance_path, "r") as f:
        instance = json.load(f)

    return instance


def print_instance_summary(instance):
    """
    Print a short summary of the instance.
    """
    print("=== Instance Summary ===")
    print("Instance name:", instance["instance_name"])
    print("Description:", instance["description"])
    print("Jobs:", list(instance["jobs"].keys()))
    print("Operations:", instance["operations"])
    print("Resources:", instance["resources"])
    print("Number of operations:", len(instance["operations"]))
    print("Number of resources:", len(instance["resources"]))
    print("Number of binary variables:", len(instance["operations"]) * len(instance["resources"]))
