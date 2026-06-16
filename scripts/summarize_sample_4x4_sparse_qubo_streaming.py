"""
Summarize sample_4x4 sparse QUBO streaming export.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def main() -> None:
    summary_path = Path("results/tables/sample_4x4_sparse_qubo_streaming_summary.json")
    summary = json.loads(summary_path.read_text())

    counts = summary["term_group_counts"]

    rows = []

    for term_group, count in counts.items():
        rows.append(
            {
                "term_group": term_group,
                "streamed_rows": count,
                "share_of_total": count / summary["total_streamed_rows"],
            }
        )

    df = pd.DataFrame(rows).sort_values("streamed_rows", ascending=False)

    out_path = Path("results/tables/sample_4x4_sparse_qubo_streaming_term_group_summary.csv")
    df.to_csv(out_path, index=False)

    compact = {
        "num_variables": summary["num_variables"],
        "num_human_variables": summary["num_human_variables"],
        "constant": summary["constant"],
        "total_streamed_rows": summary["total_streamed_rows"],
        "elapsed_seconds": summary["elapsed_seconds"],
        "output_csv": summary["output_csv"],
    }

    compact_path = Path("results/tables/sample_4x4_sparse_qubo_streaming_compact_summary.json")
    compact_path.write_text(json.dumps(compact, indent=2))

    print("=== sample_4x4 sparse QUBO streaming summary ===")
    print(df.to_string(index=False))
    print(f"Saved term group summary: {out_path}")
    print(f"Saved compact summary: {compact_path}")


if __name__ == "__main__":
    main()
