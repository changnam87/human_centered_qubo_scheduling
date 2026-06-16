
## Observed Result

The full tiny QAOA parameter sensitivity experiment evaluated 45 parameter cases.

The tested grid covered reps = 1, 2, 3; maxiter = 50, 100, 200; and seeds = 123, 456, 789, 1001, 2025.

The known optimum was bitstring 101001 with energy 4.0.

The experiment produced 44 PASS cases, 1 PARTIAL_PASS case, 0 SKIPPED cases, and 0 FAIL cases.

The success_rate was approximately 0.9778.

The best selected case was run000_p1_it50_s123, using reps = 1, maxiter = 50, and seed = 123.

That case used StatevectorSampler and recovered qaoa_bitstring = 101001 with qaoa_energy = 4.0 and qaoa_gap_to_known = 0.0.

This confirms that the tiny QAOA software/simulator path is robust across the tested toy parameter grid.

This remains a toy software/simulator result only. It does not run quantum hardware and does not imply quantum advantage.
