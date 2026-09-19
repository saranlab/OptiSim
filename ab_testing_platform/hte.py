"""
Heterogeneous Treatment Effects (HTE) & Subgroup Slicing Engine.

Calculates Conditional Average Treatment Effects (CATE), Cochran's Q test
for treatment effect heterogeneity, and segment-specific interaction tests.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
from scipy import stats

from ab_testing_platform.models import HTEAnalysisResult, SubgroupMetric


class HTEEngine:
    """Engine for estimating and evaluating Heterogeneous Treatment Effects (CATE)."""

    @staticmethod
    def analyze_subgroups(
        dimension: str,
        subgroup_data: List[Dict[str, any]],
        alpha: float = 0.05,
    ) -> HTEAnalysisResult:
        """
        Analyze treatment effect across subgroups along a specified dimension.

        Parameters
        ----------
        dimension: str
            Name of the slicing dimension (e.g. 'device', 'user_tier', 'geo').
        subgroup_data: List[Dict]
            List of dicts, each with keys:
            - 'name': str
            - 'sample_size_a': int
            - 'conversions_a': int
            - 'sample_size_b': int
            - 'conversions_b': int
        alpha: float
            Significance level (default 0.05).
        """
        if not subgroup_data:
            raise ValueError("subgroup_data cannot be empty")

        z_crit = stats.norm.ppf(1.0 - alpha / 2.0)

        # 1. Compute overall pooled ATE across all segments
        total_n_a = sum(s["sample_size_a"] for s in subgroup_data)
        total_c_a = sum(s["conversions_a"] for s in subgroup_data)
        total_n_b = sum(s["sample_size_b"] for s in subgroup_data)
        total_c_b = sum(s["conversions_b"] for s in subgroup_data)

        overall_p_a = total_c_a / max(1, total_n_a)
        overall_p_b = total_c_b / max(1, total_n_b)
        overall_ate = overall_p_b - overall_p_a
        overall_var = (
            overall_p_a * (1.0 - overall_p_a) / max(1, total_n_a)
            + overall_p_b * (1.0 - overall_p_b) / max(1, total_n_b)
        )
        overall_se = float(np.sqrt(max(1e-12, overall_var)))

        # 2. Evaluate each subgroup
        subgroups: List[SubgroupMetric] = []
        taus: List[float] = []
        weights: List[float] = []

        for item in subgroup_data:
            name = item["name"]
            na = int(item["sample_size_a"])
            ca = int(item["conversions_a"])
            nb = int(item["sample_size_b"])
            cb = int(item["conversions_b"])

            pa = ca / max(1, na)
            pb = cb / max(1, nb)
            abs_lift = pb - pa
            rel_lift = (abs_lift / pa) if pa > 0 else 0.0

            # Variance of difference in proportions
            var_diff = (pa * (1.0 - pa) / max(1, na)) + (pb * (1.0 - pb) / max(1, nb))
            se_diff = float(np.sqrt(max(1e-12, var_diff)))

            # Z-test for subgroup significance
            z_score = abs_lift / se_diff
            p_val = float(2.0 * (1.0 - stats.norm.cdf(abs(z_score))))
            ci_lower = float(abs_lift - z_crit * se_diff)
            ci_upper = float(abs_lift + z_crit * se_diff)
            is_sig = bool(p_val < alpha)

            # Interaction test: is this subgroup's lift different from overall ATE?
            se_interaction = float(np.sqrt(max(1e-12, se_diff**2 + overall_se**2)))
            z_interaction = (abs_lift - overall_ate) / se_interaction
            p_interaction = float(2.0 * (1.0 - stats.norm.cdf(abs(z_interaction))))
            is_interaction_sig = bool(p_interaction < alpha)

            taus.append(abs_lift)
            weights.append(1.0 / max(1e-9, se_diff**2))

            subgroups.append(
                SubgroupMetric(
                    segment_name=name,
                    sample_size_a=na,
                    conversions_a=ca,
                    cvr_a=float(pa),
                    sample_size_b=nb,
                    conversions_b=cb,
                    cvr_b=float(pb),
                    absolute_lift=float(abs_lift),
                    relative_lift=float(rel_lift),
                    se_difference=float(se_diff),
                    z_score=float(z_score),
                    p_value=float(p_val),
                    ci_lower=float(ci_lower),
                    ci_upper=float(ci_upper),
                    is_significant=is_sig,
                    interaction_p_value=float(p_interaction),
                    interaction_significant=is_interaction_sig,
                )
            )

        # 3. Cochran's Q test for heterogeneity
        # Q = sum w_i * (tau_i - tau_w)^2 ~ chi^2(k - 1)
        w_arr = np.array(weights)
        t_arr = np.array(taus)
        weighted_mean_tau = np.sum(w_arr * t_arr) / np.sum(w_arr)
        q_stat = float(np.sum(w_arr * (t_arr - weighted_mean_tau) ** 2))
        df = max(1, len(subgroups) - 1)
        hetero_p_val = float(1.0 - stats.chi2.cdf(q_stat, df=df))
        has_heterogeneity = bool(hetero_p_val < alpha and len(subgroups) > 1)

        # Sort to find top and worst segments
        sorted_subgroups = sorted(subgroups, key=lambda s: s.absolute_lift, reverse=True)
        top_segment = sorted_subgroups[0].segment_name
        worst_segment = sorted_subgroups[-1].segment_name

        return HTEAnalysisResult(
            dimension=dimension,
            overall_ate=float(overall_ate),
            subgroups=subgroups,
            heterogeneity_p_value=float(hetero_p_val),
            has_heterogeneity=has_heterogeneity,
            top_performing_segment=top_segment,
            worst_performing_segment=worst_segment,
        )

    @staticmethod
    def get_default_device_subgroups(
        base_n_a: int = 10000,
        base_n_b: int = 10000,
        base_cvr_a: float = 0.10,
        base_lift: float = 0.12,
    ) -> List[Dict[str, any]]:
        """Generate realistic device segment allocations with heterogeneous effects."""
        # Mobile: 55% traffic, strong positive lift (+18%)
        # Desktop: 35% traffic, moderate positive lift (+6%)
        # Tablet: 10% traffic, slightly negative/noisy lift (-2%)
        mobile_n_a = int(base_n_a * 0.55)
        mobile_n_b = int(base_n_b * 0.55)
        mobile_cvr_a = base_cvr_a * 0.90
        mobile_cvr_b = mobile_cvr_a * (1.0 + base_lift * 1.5)

        desktop_n_a = int(base_n_a * 0.35)
        desktop_n_b = int(base_n_b * 0.35)
        desktop_cvr_a = base_cvr_a * 1.20
        desktop_cvr_b = desktop_cvr_a * (1.0 + base_lift * 0.5)

        tablet_n_a = int(base_n_a * 0.10)
        tablet_n_b = int(base_n_b * 0.10)
        tablet_cvr_a = base_cvr_a * 1.05
        tablet_cvr_b = tablet_cvr_a * 0.98

        return [
            {
                "name": "Mobile (iOS / Android)",
                "sample_size_a": mobile_n_a,
                "conversions_a": int(mobile_n_a * mobile_cvr_a),
                "sample_size_b": mobile_n_b,
                "conversions_b": int(mobile_n_b * mobile_cvr_b),
            },
            {
                "name": "Desktop (Web)",
                "sample_size_a": desktop_n_a,
                "conversions_a": int(desktop_n_a * desktop_cvr_a),
                "sample_size_b": desktop_n_b,
                "conversions_b": int(desktop_n_b * desktop_cvr_b),
            },
            {
                "name": "Tablet",
                "sample_size_a": tablet_n_a,
                "conversions_a": int(tablet_n_a * tablet_cvr_a),
                "sample_size_b": tablet_n_b,
                "conversions_b": int(tablet_n_b * tablet_cvr_b),
            },
        ]
