
## Observed Merge and Validation Result

The sample_4x4 streamed sparse QUBO merge completed successfully.

The unmerged streamed coefficient file contained 8,872,562 coefficient rows.

After grouping by unique (i,j) pairs and summing duplicate coefficients, the merged sparse QUBO contained 8,218,171 unique nonzero pairs.

This corresponds to a reduction ratio of approximately 0.926, or about 7.4% fewer rows.

The merge completed in approximately 10.3 seconds using chunked processing.

The merged QUBO energy validation also passed.

Across six sampled assignments, the merged QUBO energy matched the direct representative objective with maximum absolute error approximately 1.14e-13 and mean absolute error approximately 6.63e-14.

This confirms that the compact merged sparse QUBO representation is energy-consistent with the intended sample_4x4 representative objective.

The large merged coefficient CSV remains a local ignored artifact, while scripts and summary files are tracked in Git.
