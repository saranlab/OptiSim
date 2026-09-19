"""
CUPED (Controlled-experiment Using Pre-Experiment Data) Engine.

Implements the variance reduction technique from:
Deng, A., Xu, Y., Kohavi, R., & Walker, T. (2013).
Improving the Sensitivity of Online A/B Tests by Utilizing Pre-Experiment Data.
Proceedings of the Sixth ACM International Conference on Web Search and Data Mining (WSDM '13).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from ab_testing_platform.math_utils import safe_divide
from ab_testing_platform.models import CUPEDResult


class CUPEDEngine:
    """Calculates variance-reduced treatment effects using pre-experiment covariates."""

    @staticmethod
    def compute(
        y_control: np.ndarray,
        y_treatment: np.ndarray,
        x_control: np.ndarray,
        x_treatment: np.ndarray,
        alpha: float = 0.05,
    ) -> CUPEDResult:
        """
        Compute CUPED adjusted treatment effect and variance reduction.

        Parameters
        ----------
        y_control : np.ndarray
            Outcome metric observed during experiment for Control.
        y_treatment : np.ndarray
            Outcome metric observed during experiment for Treatment.
        x_control : np.ndarray
            Pre-experiment covariate (e.g. historical metric) for Control.
        x_treatment : np.ndarray
            Pre-experiment covariate for Treatment.
        alpha : float
            Significance level (default 0.05).
        """
        y_c = np.asarray(y_control, dtype=float)
        y_t = np.asarray(y_treatment, dtype=float)
        x_c = np.asarray(x_control, dtype=float)
        x_t = np.asarray(x_treatment, dtype=float)

        if len(y_c) != len(x_c) or len(y_t) != len(x_t):
            raise ValueError("Lengths of outcome Y and pre-experiment covariate X must match.")
        if len(y_c) < 2 or len(y_t) < 2:
            raise ValueError("Each arm must have at least 2 samples for variance estimation.")

        n_c = len(y_c)
        n_t = len(y_t)

        # Raw metrics
        raw_mean_c = float(np.mean(y_c))
        raw_mean_t = float(np.mean(y_t))
        raw_lift = raw_mean_t - raw_mean_c

        var_y_c = float(np.var(y_c, ddof=1))
        var_y_t = float(np.var(y_t, ddof=1))
        raw_var = (var_y_c / n_c) + (var_y_t / n_t)

        # Pooled sample for optimal theta estimation across both arms
        y_all = np.concatenate([y_c, y_t])
        x_all = np.concatenate([x_c, x_t])

        var_x = float(np.var(x_all, ddof=1))
        if var_x < 1e-12:
            theta = 0.0
            correlation = 0.0
        else:
            cov_xy = float(np.cov(y_all, x_all, ddof=1)[0, 1])
            theta = cov_xy / var_x
            var_y = float(np.var(y_all, ddof=1))
            std_prod = np.sqrt(var_x * var_y)
            correlation = float(cov_xy / std_prod) if std_prod > 1e-12 else 0.0

        mean_x_all = float(np.mean(x_all))

        # Adjusted outcomes: Y_adj = Y - theta * (X - mean(X))
        y_c_adj = y_c - theta * (x_c - mean_x_all)
        y_t_adj = y_t - theta * (x_t - mean_x_all)

        adj_mean_c = float(np.mean(y_c_adj))
        adj_mean_t = float(np.mean(y_t_adj))
        adj_lift = adj_mean_t - adj_mean_c

        var_adj_c = float(np.var(y_c_adj, ddof=1))
        var_adj_t = float(np.var(y_t_adj, ddof=1))
        adj_var = (var_adj_c / n_c) + (var_adj_t / n_t)

        # Variance reduction ratio: 1 - Var(adj) / Var(raw)
        if raw_var > 1e-12:
            variance_reduction_pct = max(0.0, min(100.0, (1.0 - (adj_var / raw_var)) * 100.0))
        else:
            variance_reduction_pct = 0.0

        sample_size_savings_pct = variance_reduction_pct

        # Confidence interval and p-value on adjusted lift
        se_adj = np.sqrt(adj_var) if adj_var > 0 else 1e-6
        z_crit = stats.norm.ppf(1.0 - alpha / 2.0)
        ci_lower = float(adj_lift - z_crit * se_adj)
        ci_upper = float(adj_lift + z_crit * se_adj)

        z_stat = float(adj_lift / se_adj) if se_adj > 0 else 0.0
        p_value = float(2.0 * (1.0 - stats.norm.cdf(abs(z_stat))))
        is_sig = bool(p_value < alpha)

        return CUPEDResult(
            raw_mean_control=raw_mean_c,
            raw_mean_treatment=raw_mean_t,
            raw_lift=raw_lift,
            raw_variance=raw_var,
            adjusted_mean_control=adj_mean_c,
            adjusted_mean_treatment=adj_mean_t,
            adjusted_lift=adj_lift,
            adjusted_variance=adj_var,
            theta=theta,
            correlation=correlation,
            variance_reduction_pct=variance_reduction_pct,
            sample_size_savings_pct=sample_size_savings_pct,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            p_value=p_value,
            is_significant=is_sig,
        )

    @staticmethod
    def simulate_cuped_data(
        n_control: int = 5000,
        n_treatment: int = 5000,
        baseline_cvr: float = 0.10,
        true_lift: float = 0.015,
        correlation: float = 0.60,
        random_seed: int = 42,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate correlated synthetic pre-experiment and experiment data for CUPED.
        """
        rng = np.random.default_rng(random_seed)
        rho = float(np.clip(correlation, -0.99, 0.99))

        def _generate_arm(n: int, target_mean: float):
            # Generate bivariate standard normal with specified correlation
            mean = [0.0, 0.0]
            cov = [[1.0, rho], [rho, 1.0]]
            z = rng.multivariate_normal(mean, cov, size=n)
            # Pre-experiment covariate X and experiment outcome Y (e.g. user spend or activity)
            metric_scale = 0.05
            x = baseline_cvr + metric_scale * z[:, 0]
            y = target_mean + metric_scale * z[:, 1]
            return y, x

        y_c, x_c = _generate_arm(n_control, baseline_cvr)
        y_t, x_t = _generate_arm(n_treatment, baseline_cvr + true_lift)
        return y_c, y_t, x_c, x_t
