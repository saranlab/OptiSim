"""
Anytime-valid (always-valid) inference for binary A/B tests.

Why this module exists
----------------------
A fixed-horizon test such as :meth:`StatsEngine.two_proportion_z_test` controls
the Type I error rate at ``alpha`` for **one** look, at **one** sample size that
was committed to before any data was seen. A dashboard cannot enforce that: the
user refreshes whenever they like. Under the null hypothesis the running
z-statistic is a random walk whose amplitude grows like ``sqrt(2 log log n)``,
so a fixed 1.96 threshold is crossed *eventually with probability one*. In
practice, twenty looks turns a nominal 5% false-positive rate into roughly 25%.

A confidence sequence solves this by making a stronger promise. An ordinary
95% confidence interval guarantees coverage at a single pre-specified ``n``::

    P( interval_n contains the truth ) = 0.95      for one chosen n

A confidence sequence guarantees coverage at *every* ``n`` at once::

    P( interval_n contains the truth for all n simultaneously ) >= 0.95

Because it is already valid at every sample size, stopping whenever you like -
including the moment the interval first excludes zero - cannot inflate the error
rate. Peeking becomes free.

The price is width. A fixed interval shrinks like ``1/sqrt(n)``; a confidence
sequence shrinks like ``sqrt(log log n / n)``. That extra ``log log n`` is
exactly the law of the iterated logarithm above - the cost of insuring against
every future look. Expect intervals roughly 1.3x-1.6x wider at the planned
sample size, in exchange for an error rate that is genuinely the advertised one.

Method
------
Asymptotic confidence sequence of Waudby-Smith and Ramdas, "Time-uniform
central limit theory and asymptotic confidence sequences". For an estimate
``delta_hat`` with per-observation variance ``sigma^2`` after ``n`` effective
observations::

    delta_hat +/- sigma * sqrt( (2(n rho^2 + 1)) / (n^2 rho^2)
                                * log( sqrt(n rho^2 + 1) / alpha ) )

``rho`` is a tuning constant that determines where the sequence is tightest. It
must be chosen from the *planned* sample size, not the current one - tuning it
to the data you have already seen is a form of peeking in itself.
"""

from __future__ import annotations

from math import exp, log, sqrt
from typing import Optional

from ab_testing_platform.math_utils import EPSILON, safe_divide
from ab_testing_platform.models import SequentialResult
from ab_testing_platform.validation import validate_count_data, validate_probability


class SequentialTest:
    """Always-valid confidence sequences for the difference of two proportions."""

    @staticmethod
    def tuning_parameter(planned_sample_size: int, alpha: float = 0.05) -> float:
        """
        Choose ``rho`` so the confidence sequence is narrowest near the planned n.

        Args:
            planned_sample_size: Per-variation sample size the experiment was
                designed for. Use the output of
                :meth:`StatsEngine.required_sample_size_per_variation`.
            alpha: Design significance level.

        Returns:
            The tuning constant ``rho``.
        """

        validate_probability(alpha, "alpha", inclusive=False)
        n_star = max(int(planned_sample_size), 1)
        log_alpha_term = -2.0 * log(alpha)
        return sqrt((log_alpha_term + log(log_alpha_term + 1.0)) / n_star)

    @staticmethod
    def _effective_sample_size(
        var_a: float, n_a: int, var_b: float, n_b: int
    ) -> float:
        """
        Collapse two unequal arms into one effective sample size.

        The published formula is stated for a single sample of size ``n`` with
        per-observation variance ``sigma^2``. Writing the variance of the
        difference as ``sigma_pooled^2 / n_eff`` with
        ``sigma_pooled^2 = var_a + var_b`` recovers ``n_eff == n`` when the arms
        are balanced and equally variable, and degrades sensibly when they
        are not.
        """

        variance_of_difference = safe_divide(var_a, n_a) + safe_divide(var_b, n_b)
        if variance_of_difference < EPSILON:
            return float(min(n_a, n_b))
        return (var_a + var_b) / variance_of_difference

    @staticmethod
    def confidence_sequence(
        conversions_a: int,
        sample_size_a: int,
        conversions_b: int,
        sample_size_b: int,
        alpha: float = 0.05,
        planned_sample_size: Optional[int] = None,
    ) -> SequentialResult:
        """
        Compute an anytime-valid interval for the absolute lift ``p_b - p_a``.

        Unlike a Wald interval, this one may be inspected as often as desired -
        after every visitor if you like - without inflating the false-positive
        rate beyond ``alpha``.

        Args:
            conversions_a: Conversions observed in the control arm.
            sample_size_a: Users assigned to the control arm.
            conversions_b: Conversions observed in the treatment arm.
            sample_size_b: Users assigned to the treatment arm.
            alpha: Design significance level, held fixed across all looks.
            planned_sample_size: Per-variation sample size the test was designed
                for. Defaults to the current effective sample size, which makes
                the sequence tightest right now; prefer passing the planned
                value so the tuning constant does not depend on observed data.

        Returns:
            A :class:`SequentialResult` carrying the interval, an always-valid
            p-value, and a decision that is safe to act on at any time.
        """

        validate_count_data(conversions_a, sample_size_a, "A")
        validate_count_data(conversions_b, sample_size_b, "B")
        validate_probability(alpha, "alpha", inclusive=False)

        p_a = safe_divide(conversions_a, sample_size_a)
        p_b = safe_divide(conversions_b, sample_size_b)
        absolute_lift = p_b - p_a

        var_a = p_a * (1.0 - p_a)
        var_b = p_b * (1.0 - p_b)
        pooled_variance = var_a + var_b

        n_eff = SequentialTest._effective_sample_size(
            var_a, sample_size_a, var_b, sample_size_b
        )
        n_star = planned_sample_size if planned_sample_size else max(int(n_eff), 1)
        rho = SequentialTest.tuning_parameter(n_star, alpha)

        half_width = SequentialTest._half_width(pooled_variance, n_eff, rho, alpha)

        # A degenerate arm (no variance in either group) leaves nothing to
        # measure; widen the interval to cover zero rather than call a false win.
        if pooled_variance < EPSILON:
            half_width = max(half_width, abs(absolute_lift))

        is_conclusive = abs(absolute_lift) > half_width
        if not is_conclusive:
            direction = None
        else:
            direction = "b_better" if absolute_lift > 0 else "a_better"

        return SequentialResult(
            absolute_lift=absolute_lift,
            ci_lower=absolute_lift - half_width,
            ci_upper=absolute_lift + half_width,
            always_valid_p_value=SequentialTest._always_valid_p_value(
                absolute_lift, pooled_variance, n_eff, rho
            ),
            is_conclusive=is_conclusive,
            direction=direction,
            alpha=alpha,
            effective_sample_size=n_eff,
            planned_sample_size=int(n_star),
        )

    @staticmethod
    def _half_width(
        pooled_variance: float, n_eff: float, rho: float, alpha: float
    ) -> float:
        """Half-width of the asymptotic confidence sequence at ``n_eff``."""

        if n_eff < 1.0 or rho < EPSILON:
            return float("inf")

        boundary = (2.0 * (n_eff * rho**2 + 1.0)) / (n_eff**2 * rho**2)
        log_term = log(sqrt(n_eff * rho**2 + 1.0) / alpha)
        return sqrt(pooled_variance) * sqrt(boundary * log_term)

    @staticmethod
    def _always_valid_p_value(
        absolute_lift: float, pooled_variance: float, n_eff: float, rho: float
    ) -> float:
        """
        Smallest alpha at which the sequence would exclude zero, with rho fixed.

        Inverting the half-width for ``alpha`` gives a closed form. Unlike a
        fixed-horizon p-value this quantity is a valid decision statistic at
        every sample size, so thresholding it at 0.05 at any moment - or at
        many moments - keeps the false-positive rate at 5%.
        """

        if pooled_variance < EPSILON or n_eff < 1.0 or rho < EPSILON:
            return 1.0

        root = sqrt(n_eff * rho**2 + 1.0)
        exponent = (absolute_lift**2 * n_eff**2 * rho**2) / (
            2.0 * pooled_variance * (n_eff * rho**2 + 1.0)
        )
        # exp() underflows to 0.0 under overwhelming evidence, the correct limit.
        p_value = root * exp(-exponent) if exponent < 700.0 else 0.0
        return float(min(max(p_value, 0.0), 1.0))
