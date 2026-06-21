"""Shared mathematical helpers."""

from __future__ import annotations

from math import erf, sqrt

import numpy as np

EPSILON = 1e-12


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide while protecting against zero denominators."""

    if abs(denominator) < EPSILON:
        return default
    return float(numerator) / float(denominator)


class NormalDistribution:
    """Numerically stable standard normal helpers without external dependencies."""

    @staticmethod
    def cdf(x: float) -> float:
        """Standard normal cumulative distribution function."""

        return 0.5 * (1.0 + erf(x / sqrt(2.0)))

    @staticmethod
    def ppf(probability: float) -> float:
        """
        Inverse standard normal CDF using Peter J. Acklam's approximation.

        The approximation is accurate enough for experiment sizing and
        inference reporting while avoiding a hard SciPy dependency.
        """

        from ab_testing_platform.validation import validate_probability

        validate_probability(probability, "probability", inclusive=False)

        a = [
            -3.969683028665376e01,
            2.209460984245205e02,
            -2.759285104469687e02,
            1.383577518672690e02,
            -3.066479806614716e01,
            2.506628277459239e00,
        ]
        b = [
            -5.447609879822406e01,
            1.615858368580409e02,
            -1.556989798598866e02,
            6.680131188771972e01,
            -1.328068155288572e01,
        ]
        c = [
            -7.784894002430293e-03,
            -3.223964580411365e-01,
            -2.400758277161838e00,
            -2.549732539343734e00,
            4.374664141464968e00,
            2.938163982698783e00,
        ]
        d = [
            7.784695709041462e-03,
            3.224671290700398e-01,
            2.445134137142996e00,
            3.754408661907416e00,
        ]

        lower_region = 0.02425
        upper_region = 1.0 - lower_region

        if probability < lower_region:
            q = sqrt(-2.0 * np.log(probability))
            return (
                (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
                / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
            )

        if probability <= upper_region:
            q = probability - 0.5
            r = q * q
            return (
                (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5])
                * q
                / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
            )

        q = sqrt(-2.0 * np.log(1.0 - probability))
        return -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
