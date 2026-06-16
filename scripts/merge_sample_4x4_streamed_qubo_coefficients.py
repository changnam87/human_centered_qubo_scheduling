"""
Merge streamed sample_4x4 sparse QUBO coefficients.

Purpose
-------
The streaming exporter writes component-wise sparse QUBO rows directly to CSV.
The file is intentionally unmerged, so the same (i, j) pair may appear multiple
times across term groups.

This script reads the large streamed coefficient CSV in chunks and merges
duplicate (i, j) coefficients:

    Q_merged[i, j] = sum over all streamed rows with same (i, j)

Outputs:
1. merged sparse coefficient CSV
2. merge summary JSON
3. term reduction summary CSV

Important
---------
The original streamed coefficient CSV is large and ignored by Git.
The merged CSV may also be large and should usually be ignored by Git.
Commit scripts and summaries, not necessarily the large merged CSV.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_coefficients_stream.csv",
    )

    parser.add_argument(
        "--out",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_coefficients_merged.csv",
    )

    parser.add_argument(
        "--summary-out",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_merge_summary.json",
    )

    parser.add_argument(
        "--reduction-out",
        type=str,
        default="results/tables/sample_4x4_sparse_qubo_merge_reduction_summary.csv",
    )

    parser.add_argument("--chunksize", type=int, default=500000)
    parser.add_argument("--drop-tolerance", type=float, default=1e-12)

    args = parser.parse_args()

    input_path = Path(args.input)
    out_path = Path(args.out)
    summary_out = Path(args.summary_out)
    reduction_out = Path(args.reduction_out)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input streamed coefficient CSV not found: {input_path}"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    reduction_out.parent.mkdir(parents=True, exist_ok=True)

    start_wall = time.time()

    merged: Dict[Tuple[int, int], float] = defaultdict(float)

    total_input_rows = 0
    chunk_count = 0

    term_group_counts = defaultdict(int)

    usecols = ["i", "j", "coefficient", "term_group"]

    print("=== Merging streamed sparse QUBO coefficients ===")
    print(f"Input: {input_path}")
    print(f"Output: {out_path}")
    print(f"Chunksize: {args.chunksize}")

    for chunk in pd.read_csv(input_path, usecols=usecols, chunksize=args.chunksize):
        chunk_count += 1
        total_input_rows += len(chunk)

        if chunk_count % 5 == 0 or chunk_count == 1:
            print(f"Processing chunk {chunk_count}, total rows read = {total_input_rows}")

        # Count term groups.
        group_counts = chunk["term_group"].value_counts()
        for term_group, count in group_counts.items():
            term_group_counts[str(term_group)] += int(count)

        # Group inside chunk first.
        grouped = (
            chunk.groupby(["i", "j"], as_index=False)["coefficient"]
            .sum()
        )

        for row in grouped.itertuples(index=False):
            i = int(row.i)
            j = int(row.j)
            coeff = float(row.coefficient)

            if i <= j:
                key = (i, j)
            else:
                key = (j, i)

            merged[key] += coeff

    # Drop near-zero merged coefficients.
    merged_nonzero = {
        key: coeff
        for key, coeff in merged.items()
        if abs(coeff) > args.drop_tolerance
    }

    # Write merged CSV.
    with out_path.open("w") as f:
        f.write("i,j,coefficient\n")

        for (i, j), coeff in sorted(merged_nonzero.items()):
            f.write(f"{i},{j},{coeff}\n")

    elapsed = time.time() - start_wall

    total_merged_rows_before_drop = len(merged)
    total_merged_rows_after_drop = len(merged_nonzero)

    reduction_ratio_after_drop = (
        total_merged_rows_after_drop / total_input_rows
        if total_input_rows > 0
        else None
    )

    summary = {
        "experiment": "sample_4x4_sparse_qubo_duplicate_merge",
        "input_csv": str(input_path),
        "output_csv": str(out_path),
        "total_input_rows": total_input_rows,
        "chunk_count": chunk_count,
        "chunksize": args.chunksize,
        "unique_pairs_before_drop": total_merged_rows_before_drop,
        "unique_pairs_after_drop": total_merged_rows_after_drop,
        "drop_tolerance": args.drop_tolerance,
        "reduction_ratio_after_drop": reduction_ratio_after_drop,
        "term_group_counts": dict(term_group_counts),
        "elapsed_seconds": elapsed,
        "note": "Merged CSV may be large and should usually be treated as a local artifact.",
    }

    summary_out.write_text(json.dumps(summary, indent=2))

    reduction_df = pd.DataFrame(
        [
            {
                "metric": "total_input_rows",
                "value": total_input_rows,
            },
            {
                "metric": "unique_pairs_before_drop",
                "value": total_merged_rows_before_drop,
            },
            {
                "metric": "unique_pairs_after_drop",
                "value": total_merged_rows_after_drop,
            },
            {
                "metric": "reduction_ratio_after_drop",
                "value": reduction_ratio_after_drop,
            },
            {
                "metric": "elapsed_seconds",
                "value": elapsed,
            },
        ]
    )

    reduction_df.to_csv(reduction_out, index=False)

    print("=== Merge complete ===")
    print(f"total_input_rows = {total_input_rows}")
    print(f"unique_pairs_before_drop = {total_merged_rows_before_drop}")
    print(f"unique_pairs_after_drop = {total_merged_rows_after_drop}")
    print(f"reduction_ratio_after_drop = {reduction_ratio_after_drop}")
    print(f"elapsed_seconds = {elapsed:.2f}")
    print(f"saved merged CSV = {out_path}")
    print(f"saved summary = {summary_out}")
    print(f"saved reduction summary = {reduction_out}")


if __name__ == "__main__":
    main()
