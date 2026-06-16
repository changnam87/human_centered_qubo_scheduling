import json
import random
from pathlib import Path


def augment_with_human_centered_attributes(
    base_instance,
    num_workers=2,
    num_robots=1,
    seed=1
):
    """
    Add synthetic human-centered attributes to a parsed scheduling benchmark.

    This does not claim measured human data.
    It creates controlled synthetic attributes for computational benchmarking.
    """
    random.seed(seed)

    operations = base_instance["operations"]
    machines = base_instance["machines"]

    workers = [f"H{h}" for h in range(num_workers)]
    robots = [f"R{r}" for r in range(num_robots)]

    resources = machines + workers + robots

    workload_score = {}
    ergonomic_risk = {}
    skill_requirement = {}
    fatigue_coefficient = {}
    safety_risk = {}
    skill_compatibility = {}
    processing_time = {}
    processing_cost = {}

    for operation in operations:
        base_machine = base_instance["machine_requirement"][operation]
        base_processing_time = base_instance["processing_time"][operation][base_machine]

        # Synthetic human-centered attributes
        workload_score[operation] = random.randint(1, 10)
        ergonomic_risk[operation] = random.randint(1, 10)
        skill_requirement[operation] = random.randint(1, 3)
        fatigue_coefficient[operation] = round(random.uniform(0.05, 0.30), 3)
        safety_risk[operation] = random.randint(0, 3)

        processing_time[operation] = {}
        processing_cost[operation] = {}
        skill_compatibility[operation] = {}

        for resource in resources:
            if resource in machines:
                if resource == base_machine:
                    processing_time[operation][resource] = base_processing_time
                    processing_cost[operation][resource] = base_processing_time
                    skill_compatibility[operation][resource] = 1
                else:
                    processing_time[operation][resource] = 999
                    processing_cost[operation][resource] = 999
                    skill_compatibility[operation][resource] = 0

            elif resource.startswith("H"):
                # Human can perform some operations depending on synthetic skill.
                compatible = random.random() < 0.70

                if compatible:
                    human_time = max(1, int(round(base_processing_time * random.uniform(1.0, 1.8))))
                    processing_time[operation][resource] = human_time
                    processing_cost[operation][resource] = human_time
                    skill_compatibility[operation][resource] = 1
                else:
                    processing_time[operation][resource] = 999
                    processing_cost[operation][resource] = 999
                    skill_compatibility[operation][resource] = 0

            elif resource.startswith("R"):
                # Robot can perform some operations, but not all.
                compatible = random.random() < 0.50

                if compatible:
                    robot_time = max(1, int(round(base_processing_time * random.uniform(0.8, 1.4))))
                    processing_time[operation][resource] = robot_time
                    processing_cost[operation][resource] = robot_time
                    skill_compatibility[operation][resource] = 1
                else:
                    processing_time[operation][resource] = 999
                    processing_cost[operation][resource] = 999
                    skill_compatibility[operation][resource] = 0

    augmented = {
        "instance_name": base_instance["instance_name"] + "_human_centered_augmented",
        "base_instance_name": base_instance["instance_name"],
        "source_format": base_instance["source_format"],
        "augmentation_type": "synthetic_human_centered_attributes",
        "seed": seed,

        "jobs": base_instance["jobs"],
        "operations": operations,
        "machines": machines,
        "workers": workers,
        "robots": robots,
        "resources": resources,

        "precedence": base_instance["precedence"],
        "machine_requirement": base_instance["machine_requirement"],

        "processing_time": processing_time,
        "processing_cost": processing_cost,
        "skill_compatibility": skill_compatibility,

        "workload_score": workload_score,
        "ergonomic_risk": ergonomic_risk,
        "skill_requirement": skill_requirement,
        "fatigue_coefficient": fatigue_coefficient,
        "safety_risk": safety_risk,

        "weights": {
            "lambda_processing": 1.0,
            "lambda_start_time": 0.2,
            "lambda_workload": 0.5,
            "lambda_ergonomic": 0.7,
            "lambda_safety": 1.0
        },

        "penalties": {
            "P_assignment_start": 40,
            "P_skill": 40,
            "P_precedence": 50,
            "P_resource_overlap": 50,
            "P_robot_utilization": 5,
            "robot_utilization_target": 1
        }
    }

    return augmented


def save_augmented_instance(instance, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(instance, f, indent=2)

    return output_path


def print_augmented_summary(instance):
    print("=== Human-centered augmented instance summary ===")
    print("Instance:", instance["instance_name"])
    print("Base instance:", instance["base_instance_name"])
    print("Seed:", instance["seed"])
    print("Operations:", len(instance["operations"]))
    print("Machines:", len(instance["machines"]))
    print("Workers:", len(instance["workers"]))
    print("Robots:", len(instance["robots"]))
    print("Resources:", len(instance["resources"]))
    print("Resources:", instance["resources"])
