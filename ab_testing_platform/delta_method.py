"""
Delta Method Engine for Clustered / Ratio Metrics.

Implements cluster-robust variance estimation for ratio metrics from:
Deng, A., Lu, J., & Litz, J. (2018).
Trustworthy Analysis of Online A/B Tests: Pitfalls, challenges and solutions.
Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD '18).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from ab_testing_platform.math_utils import safe_divide
from ab_testing_platform.models import DeltaMethodResult


class DeltaMethodEngine:
    """Computes cluster-robust ratio metric inference using the Delta Method."""

    @staticmethod
    def compute(
        control_numerators: np.ndarray,
        control_denominators: np.ndarray,
        treatment_numerators: np.ndarray,
        treatment_denominators: np.ndarray,
        alpha: float = 0.05,
    ) -> DeltaMethodResult:
        """
        Compute cluster-robust difference in ratio metrics between treatment and control.

        Parameters
        ----------
        control_numerators : np.ndarray
            Per-user sum of numerators (e.g. user clicks or user revenue) in Control.
        control_denominators : np.ndarray
            Per-user sum of denominators (e.g. user sessions or user impressions) in Control.
        treatment_numerators : np.ndarray
            Per-user sum of numerators in Treatment.
        treatment_denominators : np.ndarray
            Per-user sum of denominators in Treatment.
        alpha : float
            Significance level (default 0.05).
        """
        y_c = np.asarray(control_numerators, dtype=float)
        n_c = np.asarray(control_denominators, dtype=float)
        y_t = np.asarray(treatment_numerators, dtype=float)
        n_t = np.asarray(treatment_denominators, dtype=float)

        if len(y_c) != len(n_c) or len(y_t) != len(n_t):
            raise ValueError("Numerator and denominator arrays must have equal lengths per arm.")
        if len(y_c) < 2 or len(y_t) < 2:
            raise ValueError("Must have at least 2 cluster observations per arm.")
        if np.any(n_c <= 0) or np.any(n_t <= 0):
            raise ValueError("Denominators must be strictly positive.")

        def _estimate_arm_ratio_var(y: np.ndarray, n: np.ndarray):
            m = len(y)
            sum_y = float(np.sum(y))
            sum_n = float(np.sum(n))
            mean_y = sum_y / m
            mean_n = sum_n / m

            ratio = sum_y / sum_n

            var_y = float(np.var(y, ddof=1))
            var_n = float(np.var(n, ddof=1))
            cov_yn = float(np.cov(y, n, ddof=1)[0, 1])

            # Delta method variance: Var(R) = (1 / (m * mean_n^2)) * (var_y - 2*ratio*cov_yn + ratio^2*var_n)
            var_ratio = (1.0 / (m * (mean_n**2))) * (var_y - 2.0 * ratio * cov_yn + (ratio**2) * var_n)
            var_ratio = max(1e-15, var_ratio)
            se_ratio = float(np.sqrt(var_ratio))
            return ratio, var_ratio, se_ratio

        r_c, var_c, se_c = _estimate_arm_ratio_var(y_c, n_c)
        r_t, var_t, se_t = _estimate_arm_ratio_var(y_t, n_t)

        abs_lift = r_t - r_c
        rel_lift = safe_divide(abs_lift, r_c)

        se_diff = float(np.sqrt(var_c + var_t))
        z_stat = float(abs_lift / se_diff) if se_diff > 0 else 0.0

        p_val = float(2.0 * (1.0 - stats.norm.cdf(abs(z_stat))))
        z_crit = float(stats.norm.ppf(1.0 - alpha / 2.0))

        ci_low = float(abs_lift - z_crit * se_diff)
        ci_high = float(abs_lift + z_crit * se_diff)
        is_sig = bool(p_val < alpha)

        return DeltaMethodResult(
            ratio_control=r_c,
            ratio_treatment=r_t,
            absolute_lift=abs_lift,
            relative_lift=rel_lift,
            se_control=se_c,
            se_treatment=se_t,
            se_difference=se_diff,
            z_statistic=z_stat,
            p_value=p_val,
            ci_lower=ci_low,
            ci_upper=ci_high,
            is_significant=is_sig,
            num_clusters_control=len(y_c),
            num_clusters_treatment=len(y_t),
        )

    @staticmethod
    def simulate_clustered_ratio_data(
        num_users_control: int = 1000,
        num_users_treatment: int = 1000,
        base_ctr: float = 0.08,
        true_lift: float = 0.015,
        mean_sessions_per_user: float = 5.0,
        random_seed: int = 42,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate user-level session counts and user-level click counts.
        """
        rng = np.random.default_rng(random_seed)

        def _generate_users(n_users: int, ctr: float):
            # Session count per user follows a Poisson + 1 distribution (min 1 session)
            sessions = rng.poisson(lam=mean_sessions_per_user - 1, size=n_users) + 1
            # User intrinsic propensity variation
            user_affinity = rng.beta(a=ctr * 20.0, b=(1.0 - ctr) * 20.0, size=n_users)
            # Clicks generated as Binomial(sessions, user_affinity)
            clicks = rng.binomial(n=sessions, p=user_affinity)
            return clicks.astype(float), sessions.astype(float)

        y_c, n_c = _generate_users(num_users_control, base_ctr)
        y_t, n_t = _generate_users(num_users_treatment, base_ctr + true_lift)
        return y_c, n_c, y_t, n_t
