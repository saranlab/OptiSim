"""Frequentist power analysis and inference for binary A/B tests."""

from __future__ import annotations

from math import ceil, sqrt

import numpy as np

from ab_testing_platform.math_utils import EPSILON, NormalDistribution, safe_divide
from ab_testing_platform.models import FrequentistResult
from ab_testing_platform.validation import (
    ValidationError,
    validate_count_data,
    validate_probability,
)


class StatsEngine:
    """Frequentist power analysis and hypothesis testing for proportions."""

    @staticmethod
    def required_sample_size_per_variation(
        baseline_conversion_rate: float,
        minimum_detectable_effect: float,
        alpha: float = 0.05,
        beta: float = 0.20,
        two_sided: bool = True,
    ) -> int:
        """
        Estimate required sample size per variation for a two-proportion test.

        Args:
            baseline_conversion_rate: Current conversion probability.
            minimum_detectable_effect: Relative MDE. Example: 0.10 means a 10%
                relative lift over baseline.
            alpha: Type I error rate.
            beta: Type II error rate. Statistical power is 1 - beta.
            two_sided: Whether to use a two-sided alternative.

        Returns:
            Required users per variation, rounded up.
        """

        validate_probability(
            baseline_conversion_rate, "baseline_conversion_rate", inclusive=False
        )
        validate_probability(alpha, "alpha", inclusive=False)
        validate_probability(beta, "beta", inclusive=False)
        if minimum_detectable_effect <= 0:
            raise ValidationError("minimum_detectable_effect must be positive.")

        p1 = baseline_conversion_rate
        p2 = p1 * (1.0 + minimum_detectable_effect)
        validate_probability(p2, "baseline + MDE conversion rate", inclusive=False)

        delta = abs(p2 - p1)
        if delta < EPSILON:
            raise ValidationError("MDE produces a near-zero absolute effect.")

        alpha_quantile = 1.0 - alpha / 2.0 if two_sided else 1.0 - alpha
        z_alpha = NormalDistribution.ppf(alpha_quantile)
        z_power = NormalDistribution.ppf(1.0 - beta)
        pooled = (p1 + p2) / 2.0

        numerator = (
            z_alpha * sqrt(2.0 * pooled * (1.0 - pooled))
            + z_power * sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2))
        ) ** 2
        return int(ceil(numerator / (delta**2)))

    @staticmethod
    def calculate_statistical_power(
        p_a: float,
        sample_size_a: int,
        p_b: float,
        sample_size_b: int,
        alpha: float = 0.05,
    ) -> float:
        """
        Calculate the post-hoc statistical power of the two-proportion test.
        """
        if sample_size_a <= 0 or sample_size_b <= 0:
            return 0.0

        diff = abs(p_b - p_a)
        if diff < EPSILON:
            return alpha

        se = sqrt(
            max(
                safe_divide(p_a * (1.0 - p_a), sample_size_a)
                + safe_divide(p_b * (1.0 - p_b), sample_size_b),
                0.0,
            )
        )
        if se < EPSILON:
            return alpha

        z_crit = NormalDistribution.ppf(1.0 - alpha / 2.0)
        z_beta = (diff / se) - z_crit
        power = NormalDistribution.cdf(z_beta)
        return float(power)

    @staticmethod
    def two_proportion_z_test(
        conversions_a: int,
        sample_size_a: int,
        conversions_b: int,
        sample_size_b: int,
        alpha: float = 0.05,
        alternative: str = "two-sided",
    ) -> FrequentistResult:
        """
        Run a two-sample z-test for proportions and compute a Wald CI for lift.

        Args:
            conversions_a: Number of conversions in Group A.
            sample_size_a: Number of users in Group A.
            conversions_b: Number of conversions in Group B.
            sample_size_b: Number of users in Group B.
            alpha: Significance level.
            alternative: one of "two-sided", "greater", or "less".

        Returns:
            FrequentistResult with p-value, significance, and CI for B - A.
        """

        validate_count_data(conversions_a, sample_size_a, "A")
        validate_count_data(conversions_b, sample_size_b, "B")
        validate_probability(alpha, "alpha", inclusive=False)
        if alternative not in {"two-sided", "greater", "less"}:
            raise ValidationError('alternative must be "two-sided", "greater", or "less".')

        p_a = safe_divide(conversions_a, sample_size_a)
        p_b = safe_divide(conversions_b, sample_size_b)
        pooled = safe_divide(conversions_a + conversions_b, sample_size_a + sample_size_b)

        pooled_se = sqrt(
            max(
                pooled
                * (1.0 - pooled)
                * (safe_divide(1.0, sample_size_a) + safe_divide(1.0, sample_size_b)),
                0.0,
            )
        )
        z_statistic = safe_divide(p_b - p_a, pooled_se)

        if alternative == "two-sided":
            p_value = 2.0 * (1.0 - NormalDistribution.cdf(abs(z_statistic)))
            z_crit = NormalDistribution.ppf(1.0 - alpha / 2.0)
        elif alternative == "greater":
            p_value = 1.0 - NormalDistribution.cdf(z_statistic)
            z_crit = NormalDistribution.ppf(1.0 - alpha)
        else:
            p_value = NormalDistribution.cdf(z_statistic)
            z_crit = NormalDistribution.ppf(1.0 - alpha)

        unpooled_se = sqrt(
            max(
                safe_divide(p_a * (1.0 - p_a), sample_size_a)
                + safe_divide(p_b * (1.0 - p_b), sample_size_b),
                0.0,
            )
        )
        absolute_lift = p_b - p_a
        ci_lower = absolute_lift - z_crit * unpooled_se
        ci_upper = absolute_lift + z_crit * unpooled_se

        power = StatsEngine.calculate_statistical_power(
            p_a=p_a,
            sample_size_a=sample_size_a,
            p_b=p_b,
            sample_size_b=sample_size_b,
            alpha=alpha,
        )

        return FrequentistResult(
            conversion_rate_a=p_a,
            conversion_rate_b=p_b,
            absolute_lift=absolute_lift,
            relative_lift=safe_divide(absolute_lift, p_a),
            z_statistic=z_statistic,
            p_value=float(np.clip(p_value, 0.0, 1.0)),
            is_significant=bool(p_value < alpha),
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            alpha=alpha,
            power=power,
        )
