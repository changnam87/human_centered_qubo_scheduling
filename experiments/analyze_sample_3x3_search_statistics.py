import sys
from pathlib import Path
from math import asin, sqrt, log, exp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import numpy as np
import pandas as pd


def wilson_ci(successes, n, z=1.96):
    """
    Wilson 95% CI for a binomial proportion.
    """
    if n == 0:
        return np.nan, np.nan

    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half_width = z * sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom

    return center - half_width, center + half_width


def cohen_h(p1, p2):
    """
    Cohen's h for difference between two proportions.
    """
    return 2 * asin(sqrt(p1)) - 2 * asin(sqrt(p2))


def odds_ratio_with_haldane(a, b, c, d):
    """
    Odds ratio with Haldane-Anscombe correction.

    Table:
        group1 feasible = a
        group1 infeasible = b
        group2 feasible = c
        group2 infeasible = d
    """
    a2 = a + 0.5
    b2 = b + 0.5
    c2 = c + 0.5
    d2 = d + 0.5

    return (a2 * d2) / (b2 * c2)


def risk_difference_ci(p1, n1, p2, n2, z=1.96):
    """
    Approximate CI for difference in proportions.
    """
    diff = p1 - p2
    se = sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
    return diff, diff - z * se, diff + z * se


def bootstrap_mean_ci(values, n_boot=5000, seed=2026):
    """
    Bootstrap 95% CI for the mean.
    """
    values = np.array(values, dtype=float)

    if len(values) == 0:
        return np.nan, np.nan, np.nan

    rng = np.random.default_rng(seed)

    boot_means = []

    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        boot_means.append(np.mean(sample))

    mean_value = float(np.mean(values))
    lower = float(np.percentile(boot_means, 2.5))
    upper = float(np.percentile(boot_means, 97.5))

    return mean_value, lower, upper


def cohen_d(x, y):
    """
    Cohen's d for two independent samples.
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if len(x) < 2 or len(y) < 2:
        return np.nan

    nx = len(x)
    ny = len(y)

    sx = np.var(x, ddof=1)
    sy = np.var(y, ddof=1)

    pooled_sd = sqrt(((nx - 1) * sx + (ny - 1) * sy) / (nx + ny - 2))

    if pooled_sd == 0:
        return np.nan

    return (np.mean(x) - np.mean(y)) / pooled_sd


def cliffs_delta(x, y):
    """
    Cliff's delta for two samples.
    Positive value means x tends to be larger than y.
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if len(x) == 0 or len(y) == 0:
        return np.nan

    greater = 0
    less = 0

    for xi in x:
        greater += np.sum(xi > y)
        less += np.sum(xi < y)

    return (greater - less) / (len(x) * len(y))


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"

    comparison_path = tables_dir / "sample_3x3_augmented_search_method_comparison.csv"
    seeded_path = tables_dir / "sample_3x3_augmented_seeded_search_results.csv"
    random_sa_path = tables_dir / "sample_3x3_augmented_sa_results.csv"
    cpsat_path = tables_dir / "sample_3x3_augmented_cpsat_result.csv"

    required_files = [
        comparison_path,
        seeded_path,
        random_sa_path,
        cpsat_path
    ]

    print("=== Checking required files ===")

    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            return

    comparison_df = pd.read_csv(comparison_path)
    seeded_df = pd.read_csv(seeded_path, dtype={"bitstring": str})
    random_df = pd.read_csv(random_sa_path, dtype={"bitstring": str})
    cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})

    cpsat_cost = float(cpsat_df.iloc[0]["total_cost"])

    # ------------------------------------------------------------
    # Build read-level unified dataframe
    # ------------------------------------------------------------
    random_reads = random_df.copy()
    random_reads["method"] = "Random-bit SA"

    seeded_reads = seeded_df.copy()
    seeded_reads["method"] = seeded_reads["search_name"].map({
        "seeded_from_handcrafted": "Seeded search from handcrafted",
        "seeded_from_cpsat": "Seeded search from CP-SAT"
    })

    unified = pd.concat([
        random_reads,
        seeded_reads
    ], ignore_index=True)

    unified["feasible"] = unified["feasible"].astype(bool)
    unified["gap_to_cpsat"] = unified["total_cost"] - cpsat_cost

    # ------------------------------------------------------------
    # Feasibility proportion + Wilson CI
    # ------------------------------------------------------------
    feasibility_rows = []

    for method, group in unified.groupby("method"):
        n = len(group)
        successes = int(group["feasible"].sum())
        p = successes / n

        lower, upper = wilson_ci(successes, n)

        feasibility_rows.append({
            "analysis_type": "feasibility_proportion",
            "method": method,
            "n": n,
            "successes": successes,
            "feasibility_rate": p,
            "ci_lower": lower,
            "ci_upper": upper,
            "effect_size_name": None,
            "effect_size_value": None,
            "comparison": None,
            "notes": "Wilson 95% confidence interval for feasibility proportion."
        })

    # ------------------------------------------------------------
    # Pairwise feasibility effect sizes
    # Main comparison: random-bit SA vs seeded from handcrafted
    # Supplementary: random-bit SA vs seeded from CP-SAT
    # ------------------------------------------------------------
    method_stats = {}

    for method, group in unified.groupby("method"):
        n = len(group)
        successes = int(group["feasible"].sum())
        failures = n - successes
        p = successes / n

        method_stats[method] = {
            "n": n,
            "successes": successes,
            "failures": failures,
            "p": p
        }

    comparison_pairs = [
        ("Seeded search from handcrafted", "Random-bit SA", "main"),
        ("Seeded search from CP-SAT", "Random-bit SA", "warm-start_ablation")
    ]

    effect_rows = []

    for m1, m2, label in comparison_pairs:
        if m1 not in method_stats or m2 not in method_stats:
            continue

        s1 = method_stats[m1]
        s2 = method_stats[m2]

        rd, rd_low, rd_high = risk_difference_ci(
            s1["p"], s1["n"],
            s2["p"], s2["n"]
        )

        h = cohen_h(s1["p"], s2["p"])

        or_value = odds_ratio_with_haldane(
            s1["successes"],
            s1["failures"],
            s2["successes"],
            s2["failures"]
        )

        effect_rows.append({
            "analysis_type": "feasibility_effect_size",
            "method": None,
            "n": None,
            "successes": None,
            "feasibility_rate": None,
            "ci_lower": None,
            "ci_upper": None,
            "effect_size_name": "risk_difference",
            "effect_size_value": rd,
            "comparison": f"{m1} vs {m2}",
            "risk_difference_ci_lower": rd_low,
            "risk_difference_ci_upper": rd_high,
            "cohens_h": h,
            "odds_ratio_haldane": or_value,
            "comparison_type": label,
            "notes": "Risk difference, Cohen's h, and Haldane-corrected odds ratio."
        })

    # ------------------------------------------------------------
    # Feasible cost summaries with bootstrap CI
    # ------------------------------------------------------------
    cost_rows = []

    for method, group in unified.groupby("method"):
        feasible_group = group[group["feasible"] == True]

        values = feasible_group["total_cost"].dropna().values
        gaps = feasible_group["gap_to_cpsat"].dropna().values

        mean_cost, cost_low, cost_high = bootstrap_mean_ci(values)
        mean_gap, gap_low, gap_high = bootstrap_mean_ci(gaps)

        if len(values) > 0:
            best_cost = float(np.min(values))
            median_cost = float(np.median(values))
            sd_cost = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        else:
            best_cost = np.nan
            median_cost = np.nan
            sd_cost = np.nan

        cost_rows.append({
            "method": method,
            "n_total": len(group),
            "n_feasible": len(feasible_group),
            "best_feasible_cost": best_cost,
            "mean_feasible_cost": mean_cost,
            "mean_cost_ci_lower": cost_low,
            "mean_cost_ci_upper": cost_high,
            "median_feasible_cost": median_cost,
            "sd_feasible_cost": sd_cost,
            "mean_gap_to_cpsat": mean_gap,
            "mean_gap_ci_lower": gap_low,
            "mean_gap_ci_upper": gap_high
        })

    cost_summary_df = pd.DataFrame(cost_rows)

    # ------------------------------------------------------------
    # Continuous effect sizes for feasible cost/gap
    # Main comparison only: seeded handcrafted vs random-bit SA is impossible
    # because random-bit SA has no feasible reads.
    # Therefore compare seeded handcrafted vs seeded CP-SAT as warm-start effect.
    # ------------------------------------------------------------
    continuous_effect_rows = []

    hc_values = unified[
        (unified["method"] == "Seeded search from handcrafted")
        & (unified["feasible"] == True)
    ]["total_cost"].values

    cpsat_seed_values = unified[
        (unified["method"] == "Seeded search from CP-SAT")
        & (unified["feasible"] == True)
    ]["total_cost"].values

    if len(hc_values) > 0 and len(cpsat_seed_values) > 0:
        continuous_effect_rows.append({
            "analysis_type": "cost_effect_size",
            "comparison": "Seeded search from handcrafted vs Seeded search from CP-SAT",
            "cohens_d": cohen_d(hc_values, cpsat_seed_values),
            "cliffs_delta": cliffs_delta(hc_values, cpsat_seed_values),
            "notes": "Computed on feasible reads only; warm-start comparison."
        })

    # ------------------------------------------------------------
    # Save outputs
    # ------------------------------------------------------------
    stats_df = pd.DataFrame(feasibility_rows + effect_rows)

    if continuous_effect_rows:
        continuous_effect_df = pd.DataFrame(continuous_effect_rows)
    else:
        continuous_effect_df = pd.DataFrame()

    stats_output = tables_dir / "sample_3x3_search_statistical_analysis.csv"
    cost_output = tables_dir / "sample_3x3_search_cost_summary_with_ci.csv"
    continuous_output = tables_dir / "sample_3x3_search_continuous_effect_sizes.csv"

    stats_df.to_csv(stats_output, index=False)
    cost_summary_df.to_csv(cost_output, index=False)
    continuous_effect_df.to_csv(continuous_output, index=False)

    print()
    print("=== Feasibility statistical analysis ===")
    print(stats_df)

    print()
    print("=== Feasible cost summary with bootstrap CI ===")
    print(cost_summary_df)

    print()
    print("=== Continuous effect sizes ===")
    print(continuous_effect_df)

    print()
    print("Saved:")
    print(stats_output)
    print(cost_output)
    print(continuous_output)


if __name__ == "__main__":
    main()
