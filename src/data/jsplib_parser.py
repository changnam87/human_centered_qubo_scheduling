from pathlib import Path


def parse_jsplib_file(file_path, machine_prefix="M"):
    """
    Parse a simple JSPLib-style job-shop scheduling file.

    Expected format:
        num_jobs num_machines
        machine_0 processing_0 machine_1 processing_1 ...

    Example:
        3 3
        0 3 1 2 2 2
        0 2 2 1 1 4
        1 4 2 3 0 2

    Returns
    -------
    dict
        Base scheduling instance.
    """
    file_path = Path(file_path)

    with open(file_path, "r") as f:
        lines = [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    header = lines[0].split()
    num_jobs = int(header[0])
    num_machines = int(header[1])

    jobs = {}
    operations = []
    operation_to_job = {}
    operation_sequence_index = {}
    machine_requirement = {}
    processing_time = {}
    precedence = []

    machines = [f"{machine_prefix}{m}" for m in range(num_machines)]

    for job_id in range(num_jobs):
        line = lines[job_id + 1].split()
        values = [int(v) for v in line]

        if len(values) != 2 * num_machines:
            raise ValueError(
                f"Job {job_id} line should contain {2 * num_machines} values, "
                f"but found {len(values)}."
            )

        job_name = f"J{job_id}"
        jobs[job_name] = []

        previous_operation = None

        for seq in range(num_machines):
            machine_id = values[2 * seq]
            proc_time = values[2 * seq + 1]

            machine_name = f"{machine_prefix}{machine_id}"
            operation = f"O{job_id}_{seq}"

            operations.append(operation)
            jobs[job_name].append(operation)

            operation_to_job[operation] = job_name
            operation_sequence_index[operation] = seq
            machine_requirement[operation] = machine_name
            processing_time[operation] = {
                machine_name: proc_time
            }

            if previous_operation is not None:
                precedence.append([previous_operation, operation])

            previous_operation = operation

    instance = {
        "instance_name": file_path.stem,
        "source_format": "JSPLib-style",
        "num_jobs": num_jobs,
        "num_machines": num_machines,
        "jobs": jobs,
        "operations": operations,
        "machines": machines,
        "machine_requirement": machine_requirement,
        "processing_time": processing_time,
        "precedence": precedence,
        "operation_to_job": operation_to_job,
        "operation_sequence_index": operation_sequence_index
    }

    return instance


def print_jsplib_instance_summary(instance):
    print("=== JSPLib-style instance summary ===")
    print("Instance:", instance["instance_name"])
    print("Number of jobs:", instance["num_jobs"])
    print("Number of machines:", instance["num_machines"])
    print("Number of operations:", len(instance["operations"]))
    print("Machines:", instance["machines"])
    print("Operations:", instance["operations"])
    print()
    print("Precedence:")
    for before, after in instance["precedence"]:
        print(before, "->", after)
