import sys
from pathlib import Path
from math import sqrt, asin

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import numpy as np
import pandas as pd


def wilson_ci(successes, n, z=1.96):
    if n == 0:
        return np.nan, np.nan

    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom

    return center - half, center + half


def bootstrap_mean_ci(values, n_boot=5000, seed=2026):
    values = np.array(values, dtype=float)

    if len(values) == 0:
        return np.nan, np.nan, np.nan

    rng = np.random.default_rng(seed)
    boot_means = []

    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        boot_means.append(np.mean(sample))

    return (
        float(np.mean(values)),
        float(np.percentile(boot_means, 2.5)),
        float(np.percentile(boot_means, 97.5))
    )


def cohen_h(p1, p2):
    return 2 * asin(sqrt(p1)) - 2 * asin(sqrt(p2))


def cohen_d(x, y):
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


def odds_ratio_haldane(a, b, c, d):
    a += 0.5
    b += 0.5
    c += 0.5
    d += 0.5

    return (a * d) / (b * c)


def normal_two_sided_p_from_z(z_value):
    """
    Two-sided p-value from z using scipy if available, otherwise approximation.
    """
    try:
        from scipy.stats import norm
        return float(2 * (1 - norm.cdf(abs(z_value))))
    except Exception:
        # Approximation using error function
        import math
        cdf = 0.5 * (1 + math.erf(abs(z_value) / math.sqrt(2)))
        return float(2 * (1 - cdf))


def two_proportion_z_test(success1, n1, success2, n2):
    """
    Two-proportion z-test.
    H0: p1 = p2
    """
    p1 = success1 / n1
    p2 = success2 / n2

    pooled = (success1 + success2) / (n1 + n2)

    se = sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))

    if se == 0:
        return np.nan, np.nan

    z = (p1 - p2) / se
    p = normal_two_sided_p_from_z(z)

    return float(z), float(p)


def welch_t_test(x, y):
    """
    Welch's t-test.
    Returns t statistic and two-sided p-value.
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if len(x) < 2 or len(y) < 2:
        return np.nan, np.nan

    try:
        from scipy.stats import ttest_ind
        stat, p = ttest_ind(x, y, equal_var=False, nan_policy="omit")
        return float(stat), float(p)
    except Exception:
        return np.nan, np.nan


def mann_whitney_u_test(x, y):
    """
    Mann-Whitney U test.
    Returns U statistic and two-sided p-value.
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if len(x) == 0 or len(y) == 0:
        return np.nan, np.nan

    try:
        from scipy.stats import mannwhitneyu
        stat, p = mannwhitneyu(x, y, alternative="two-sided")
        return float(stat), float(p)
    except Exception:
        return np.nan, np.nan


def holm_bonferroni_correction(p_values, alpha=0.05):
    """
    Holm-Bonferroni correction.

    Returns adjusted p-values and reject flags in original order.
    """
    p_values = np.array(p_values, dtype=float)
    m = len(p_values)

    adjusted = np.full(m, np.nan)
    reject = np.full(m, False)

    valid_indices = np.where(~np.isnan(p_values))[0]
    valid_p = p_values[valid_indices]

    if len(valid_p) == 0:
        return adjusted, reject

    order = np.argsort(valid_p)
    sorted_indices = valid_indices[order]
    sorted_p = valid_p[order]

    # Holm adjusted p-values:
    # adj_p_i = max_{j<=i} ((m-j+1) * p_j), capped at 1
    running_max = 0.0

    for rank, idx in enumerate(sorted_indices):
        multiplier = len(valid_p) - rank
        adj_p = multiplier * p_values[idx]
        running_max = max(running_max, adj_p)
        adjusted[idx] = min(running_max, 1.0)

    # Holm rejection rule
    # Reject p_(i) while p_(i) <= alpha / (m - i + 1); stop after first failure.
    still_rejecting = True

    for rank, idx in enumerate(sorted_indices):
        threshold = alpha / (len(valid_p) - rank)

        if still_rejecting and p_values[idx] <= threshold:
            reject[idx] = True
        else:
            still_rejecting = False
            reject[idx] = False

    return adjusted, reject


def main():
    tables_dir = PROJECT_ROOT / "results" / "tables"

    summary_path = tables_dir / "sample_3x3_augmented_batch_seeded_search_summary.csv"
    read_path = tables_dir / "sample_3x3_augmented_batch_seeded_search_results.csv"
    cpsat_path = tables_dir / "sample_3x3_augmented_batch_cpsat_results.csv"

    required_files = [
        summary_path,
        read_path,
        cpsat_path
    ]

    print("=== Checking required files ===")

    for path in required_files:
        if path.exists():
            print("Found:", path)
        else:
            print("Missing:", path)
            return

    summary_df = pd.read_csv(summary_path)
    read_df = pd.read_csv(read_path, dtype={"bitstring": str})
    cpsat_df = pd.read_csv(cpsat_path, dtype={"bitstring": str})

    # ------------------------------------------------------------
    # Method-level read-based statistics
    # ------------------------------------------------------------
    method_rows = []

    for search_name, group in read_df.groupby("search_name"):
        n = len(group)
        feasible = int(group["feasible"].sum())
        feasibility_rate = feasible / n
        ci_low, ci_high = wilson_ci(feasible, n)

        feasible_group = group[group["feasible"] == True]

        best_gap_values = summary_df[
            summary_df["search_name"] == search_name
        ]["best_gap_to_cpsat"].dropna().values

        mean_gap_values = feasible_group["gap_to_cpsat"].dropna().values
        cost_values = feasible_group["total_cost"].dropna().values

        mean_gap, mean_gap_low, mean_gap_high = bootstrap_mean_ci(mean_gap_values)
        mean_cost, mean_cost_low, mean_cost_high = bootstrap_mean_ci(cost_values)

        if len(best_gap_values) > 0:
            best_gap_mean, best_gap_low, best_gap_high = bootstrap_mean_ci(best_gap_values)
            best_gap_min = float(np.min(best_gap_values))
            best_gap_max = float(np.max(best_gap_values))
        else:
            best_gap_mean = np.nan
            best_gap_low = np.nan
            best_gap_high = np.nan
            best_gap_min = np.nan
            best_gap_max = np.nan

        method_rows.append({
            "search_name": search_name,
            "total_reads": n,
            "feasible_reads": feasible,
            "feasibility_rate": feasibility_rate,
            "feasibility_ci_lower": ci_low,
            "feasibility_ci_upper": ci_high,
            "num_instances": group["seed"].nunique(),
            "mean_feasible_cost": mean_cost,
            "mean_feasible_cost_ci_lower": mean_cost_low,
            "mean_feasible_cost_ci_upper": mean_cost_high,
            "mean_gap_to_cpsat": mean_gap,
            "mean_gap_ci_lower": mean_gap_low,
            "mean_gap_ci_upper": mean_gap_high,
            "mean_best_gap_to_cpsat_across_instances": best_gap_mean,
            "best_gap_ci_lower": best_gap_low,
            "best_gap_ci_upper": best_gap_high,
            "min_best_gap_to_cpsat": best_gap_min,
            "max_best_gap_to_cpsat": best_gap_max
        })

    method_summary_df = pd.DataFrame(method_rows)

    # ------------------------------------------------------------
    # Effect sizes between methods
    # ------------------------------------------------------------
    random_name = "structure_aware_random_seed"
    cpsat_name = "structure_aware_cpsat_seed"

    effect_rows = []
    test_rows = []

    if random_name in read_df["search_name"].unique() and cpsat_name in read_df["search_name"].unique():
        g1 = read_df[read_df["search_name"] == random_name]
        g2 = read_df[read_df["search_name"] == cpsat_name]

        n1 = len(g1)
        n2 = len(g2)

        f1 = int(g1["feasible"].sum())
        f2 = int(g2["feasible"].sum())

        p1 = f1 / n1
        p2 = f2 / n2

        risk_diff = p1 - p2

        or_value = odds_ratio_haldane(
            f1,
            n1 - f1,
            f2,
            n2 - f2
        )

        z_feas, p_feas = two_proportion_z_test(f1, n1, f2, n2)

        effect_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "feasibility_rate",
            "group1_value": p1,
            "group2_value": p2,
            "difference": risk_diff,
            "cohens_h": cohen_h(p1, p2),
            "odds_ratio_haldane": or_value,
            "notes": "Positive difference means random-seed structure-aware search had higher feasibility."
        })

        test_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "feasibility_rate",
            "test": "two_proportion_z_test",
            "statistic": z_feas,
            "raw_p_value": p_feas,
            "notes": "Read-level feasibility comparison."
        })

        # Continuous comparison using feasible read-level gap
        gap1 = g1[g1["feasible"] == True]["gap_to_cpsat"].dropna().values
        gap2 = g2[g2["feasible"] == True]["gap_to_cpsat"].dropna().values

        t_gap, p_gap_t = welch_t_test(gap1, gap2)
        u_gap, p_gap_u = mann_whitney_u_test(gap1, gap2)

        effect_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "gap_to_cpsat_feasible_reads",
            "group1_value": float(np.mean(gap1)) if len(gap1) > 0 else np.nan,
            "group2_value": float(np.mean(gap2)) if len(gap2) > 0 else np.nan,
            "difference": float(np.mean(gap1) - np.mean(gap2)) if len(gap1) > 0 and len(gap2) > 0 else np.nan,
            "cohens_d": cohen_d(gap1, gap2),
            "cliffs_delta": cliffs_delta(gap1, gap2),
            "notes": "Positive difference means random-seed search had larger CP-SAT gap."
        })

        test_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "gap_to_cpsat_feasible_reads",
            "test": "welch_t_test",
            "statistic": t_gap,
            "raw_p_value": p_gap_t,
            "notes": "Read-level feasible gap comparison."
        })

        test_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "gap_to_cpsat_feasible_reads",
            "test": "mann_whitney_u_test",
            "statistic": u_gap,
            "raw_p_value": p_gap_u,
            "notes": "Nonparametric read-level feasible gap comparison."
        })

        # Instance-level best gap comparison
        s1 = summary_df[summary_df["search_name"] == random_name]["best_gap_to_cpsat"].dropna().values
        s2 = summary_df[summary_df["search_name"] == cpsat_name]["best_gap_to_cpsat"].dropna().values

        t_best, p_best_t = welch_t_test(s1, s2)
        u_best, p_best_u = mann_whitney_u_test(s1, s2)

        effect_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "best_gap_to_cpsat_instance_level",
            "group1_value": float(np.mean(s1)) if len(s1) > 0 else np.nan,
            "group2_value": float(np.mean(s2)) if len(s2) > 0 else np.nan,
            "difference": float(np.mean(s1) - np.mean(s2)) if len(s1) > 0 and len(s2) > 0 else np.nan,
            "cohens_d": cohen_d(s1, s2),
            "cliffs_delta": cliffs_delta(s1, s2),
            "notes": "Computed across 10 augmentation seeds using best gap per instance."
        })

        test_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "best_gap_to_cpsat_instance_level",
            "test": "welch_t_test",
            "statistic": t_best,
            "raw_p_value": p_best_t,
            "notes": "Instance-level best gap comparison across seeds."
        })

        test_rows.append({
            "comparison": f"{random_name} vs {cpsat_name}",
            "metric": "best_gap_to_cpsat_instance_level",
            "test": "mann_whitney_u_test",
            "statistic": u_best,
            "raw_p_value": p_best_u,
            "notes": "Nonparametric instance-level best gap comparison across seeds."
        })

    effect_df = pd.DataFrame(effect_rows)
    test_df = pd.DataFrame(test_rows)

    # ------------------------------------------------------------
    # Holm-Bonferroni correction across all hypothesis tests
    # ------------------------------------------------------------
    if len(test_df) > 0:
        adjusted, reject = holm_bonferroni_correction(
            test_df["raw_p_value"].values,
            alpha=0.05
        )

        test_df["holm_adjusted_p_value"] = adjusted
        test_df["significant_after_holm_0_05"] = reject
        test_df["multiple_comparison_method"] = "Holm-Bonferroni"
        test_df["family"] = "batch_search_method_tests"

    # ------------------------------------------------------------
    # CP-SAT baseline distribution
    # ------------------------------------------------------------
    cpsat_costs = cpsat_df["total_cost"].dropna().values
    cpsat_mean, cpsat_low, cpsat_high = bootstrap_mean_ci(cpsat_costs)

    cpsat_summary = pd.DataFrame([{
        "num_instances": len(cpsat_df),
        "num_optimal": int((cpsat_df["status"] == "OPTIMAL").sum()),
        "num_feasible": int(cpsat_df["feasible"].sum()),
        "mean_total_cost": cpsat_mean,
        "mean_total_cost_ci_lower": cpsat_low,
        "mean_total_cost_ci_upper": cpsat_high,
        "min_total_cost": float(np.min(cpsat_costs)),
        "max_total_cost": float(np.max(cpsat_costs)),
        "std_total_cost": float(np.std(cpsat_costs, ddof=1)),
        "mean_wall_time": float(cpsat_df["wall_time"].mean())
    }])

    # ------------------------------------------------------------
    # Save outputs
    # ------------------------------------------------------------
    method_output = tables_dir / "sample_3x3_batch_search_statistical_summary.csv"
    effect_output = tables_dir / "sample_3x3_batch_search_effect_sizes.csv"
    cpsat_output = tables_dir / "sample_3x3_batch_cpsat_distribution_summary.csv"
    tests_output = tables_dir / "sample_3x3_batch_search_hypothesis_tests.csv"

    method_summary_df.to_csv(method_output, index=False)
    effect_df.to_csv(effect_output, index=False)
    cpsat_summary.to_csv(cpsat_output, index=False)
    test_df.to_csv(tests_output, index=False)

    print()
    print("=== Batch search statistical summary ===")
    print(method_summary_df)

    print()
    print("=== Batch search effect sizes ===")
    print(effect_df)

    print()
    print("=== Batch hypothesis tests with Holm-Bonferroni correction ===")
    print(test_df)

    print()
    print("=== Batch CP-SAT distribution summary ===")
    print(cpsat_summary)

    print()
    print("Saved:")
    print(method_output)
    print(effect_output)
    print(cpsat_output)
    print(tests_output)


if __name__ == "__main__":
    main()
