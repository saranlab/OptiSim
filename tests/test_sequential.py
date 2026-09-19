"""
Calibration tests for anytime-valid inference.

These differ in kind from the rest of the suite. Most tests here assert the
*shape* of a result - that a value is an int, or lies in [0, 1]. A statistical
engine needs something stronger: proof that its error rates are the ones it
advertises. Every test below simulates many experiments where the ground truth
is known and checks the long-run frequency of a wrong answer.

The headline test is :meth:`test_confidence_sequence_survives_continuous_peeking`.
It is the exact scenario that breaks a fixed-horizon z-test.
"""

from __future__ import annotations

import unittest

import numpy as np

from ab_testing_platform import SequentialTest, StatsEngine


def _aa_trials(rng, trials, n_max, base_rate):
    """Cumulative conversions for `trials` A/A experiments (B identical to A)."""

    a = rng.binomial(1, base_rate, size=(trials, n_max))
    b = rng.binomial(1, base_rate, size=(trials, n_max))
    return np.cumsum(a, axis=1), np.cumsum(b, axis=1)


class TestSequentialCalibration(unittest.TestCase):
    """Does the confidence sequence deliver the error rate it promises?"""

    TRIALS = 600
    N_MAX = 6_000
    BASE_RATE = 0.10
    ALPHA = 0.05
    N_LOOKS = 15

    def setUp(self) -> None:
        self.rng = np.random.default_rng(20240115)
        self.looks = np.linspace(
            self.N_MAX // self.N_LOOKS, self.N_MAX, self.N_LOOKS
        ).astype(int)

    def test_confidence_sequence_survives_continuous_peeking(self) -> None:
        """
        The core guarantee: repeated looks must not inflate the error rate.

        A and B are identical, so any conclusive verdict is a false positive. We
        stop at the first look that declares a winner - the exact behaviour a
        dashboard user exhibits - and require the long-run rate to stay at alpha.
        """

        cum_a, cum_b = _aa_trials(self.rng, self.TRIALS, self.N_MAX, self.BASE_RATE)

        false_positives = 0
        for trial in range(self.TRIALS):
            for n in self.looks:
                result = SequentialTest.confidence_sequence(
                    conversions_a=int(cum_a[trial, n - 1]),
                    sample_size_a=int(n),
                    conversions_b=int(cum_b[trial, n - 1]),
                    sample_size_b=int(n),
                    alpha=self.ALPHA,
                    planned_sample_size=self.N_MAX,
                )
                if result.is_conclusive:
                    false_positives += 1
                    break

        rate = false_positives / self.TRIALS
        self.assertLessEqual(
            rate,
            self.ALPHA,
            f"Anytime-valid guarantee violated: {rate:.1%} false positives "
            f"across {self.N_LOOKS} looks, budget was {self.ALPHA:.0%}.",
        )

    def test_fixed_horizon_test_fails_the_same_scenario(self) -> None:
        """
        Documents *why* the sequential engine exists.

        This is not a defect in `two_proportion_z_test` - it is the correct
        behaviour of a fixed-horizon test used outside its contract. If this
        test ever starts passing at 5%, the peeking pattern below has changed
        and the guarantees in `sequential.py` should be re-derived.
        """

        cum_a, cum_b = _aa_trials(self.rng, self.TRIALS, self.N_MAX, self.BASE_RATE)

        false_positives = 0
        for trial in range(self.TRIALS):
            for n in self.looks:
                if StatsEngine.two_proportion_z_test(
                    conversions_a=int(cum_a[trial, n - 1]),
                    sample_size_a=int(n),
                    conversions_b=int(cum_b[trial, n - 1]),
                    sample_size_b=int(n),
                    alpha=self.ALPHA,
                ).is_significant:
                    false_positives += 1
                    break

        self.assertGreater(
            false_positives / self.TRIALS,
            2.0 * self.ALPHA,
            "Peeking with a fixed-horizon test is expected to inflate alpha.",
        )

    def test_fixed_horizon_test_is_calibrated_at_a_single_look(self) -> None:
        """The z-test is correct when used as intended: exactly one look."""

        cum_a, cum_b = _aa_trials(self.rng, self.TRIALS, self.N_MAX, self.BASE_RATE)
        n = self.N_MAX

        false_positives = sum(
            StatsEngine.two_proportion_z_test(
                int(cum_a[t, n - 1]), n, int(cum_b[t, n - 1]), n, alpha=self.ALPHA
            ).is_significant
            for t in range(self.TRIALS)
        )

        # Binomial noise at 600 trials; 2.5x alpha is a generous upper bound.
        self.assertLess(false_positives / self.TRIALS, 2.5 * self.ALPHA)

    def test_confidence_sequence_covers_the_true_lift_under_peeking(self) -> None:
        """Coverage must hold at every look simultaneously, not just the last."""

        p_a, p_b = 0.10, 0.13
        true_lift = p_b - p_a
        trials, n_max = 300, 4_000
        looks = np.linspace(n_max // 10, n_max, 10).astype(int)

        cum_a = np.cumsum(self.rng.binomial(1, p_a, size=(trials, n_max)), axis=1)
        cum_b = np.cumsum(self.rng.binomial(1, p_b, size=(trials, n_max)), axis=1)

        missed = 0
        for trial in range(trials):
            for n in looks:
                result = SequentialTest.confidence_sequence(
                    int(cum_a[trial, n - 1]), int(n),
                    int(cum_b[trial, n - 1]), int(n),
                    alpha=self.ALPHA, planned_sample_size=n_max,
                )
                if not (result.ci_lower <= true_lift <= result.ci_upper):
                    missed += 1
                    break

        self.assertLessEqual(missed / trials, self.ALPHA)


class TestSequentialBehaviour(unittest.TestCase):
    """Ordinary unit tests for the sequential engine."""

    def test_detects_a_large_genuine_effect(self) -> None:
        result = SequentialTest.confidence_sequence(
            conversions_a=1_000, sample_size_a=20_000,
            conversions_b=1_600, sample_size_b=20_000,
            alpha=0.05, planned_sample_size=20_000,
        )

        self.assertTrue(result.is_conclusive)
        self.assertEqual(result.direction, "b_better")
        self.assertGreater(result.ci_lower, 0.0)
        self.assertLess(result.always_valid_p_value, 0.05)

    def test_detects_a_genuine_regression(self) -> None:
        result = SequentialTest.confidence_sequence(
            conversions_a=1_600, sample_size_a=20_000,
            conversions_b=1_000, sample_size_b=20_000,
            alpha=0.05, planned_sample_size=20_000,
        )

        self.assertTrue(result.is_conclusive)
        self.assertEqual(result.direction, "a_better")
        self.assertLess(result.ci_upper, 0.0)

    def test_is_wider_than_the_fixed_horizon_interval(self) -> None:
        """The price of unlimited looks is a wider interval. Verify we pay it."""

        args = dict(
            conversions_a=1_000, sample_size_a=10_000,
            conversions_b=1_100, sample_size_b=10_000, alpha=0.05,
        )
        sequential = SequentialTest.confidence_sequence(
            **args, planned_sample_size=10_000
        )
        fixed = StatsEngine.two_proportion_z_test(**args)

        self.assertGreater(
            sequential.ci_upper - sequential.ci_lower,
            fixed.ci_upper - fixed.ci_lower,
        )

    def test_tiny_samples_are_never_conclusive(self) -> None:
        result = SequentialTest.confidence_sequence(
            conversions_a=0, sample_size_a=5,
            conversions_b=3, sample_size_b=5,
            alpha=0.05, planned_sample_size=10_000,
        )

        self.assertFalse(result.is_conclusive)
        self.assertIsNone(result.direction)

    def test_degenerate_zero_variance_data_is_not_a_winner(self) -> None:
        """Zero conversions everywhere carries no evidence of anything."""

        result = SequentialTest.confidence_sequence(
            conversions_a=0, sample_size_a=1_000,
            conversions_b=0, sample_size_b=1_000,
            alpha=0.05, planned_sample_size=1_000,
        )

        self.assertFalse(result.is_conclusive)
        self.assertEqual(result.always_valid_p_value, 1.0)

    def test_evidence_accumulates_monotonically_for_a_real_effect(self) -> None:
        """More data at a fixed effect size must strengthen the conclusion."""

        p_values = [
            SequentialTest.confidence_sequence(
                conversions_a=int(0.10 * n), sample_size_a=n,
                conversions_b=int(0.13 * n), sample_size_b=n,
                alpha=0.05, planned_sample_size=50_000,
            ).always_valid_p_value
            for n in (2_000, 10_000, 50_000)
        ]

        self.assertGreater(p_values[0], p_values[1])
        self.assertGreater(p_values[1], p_values[2])

    def test_handles_unequal_arm_sizes(self) -> None:
        result = SequentialTest.confidence_sequence(
            conversions_a=500, sample_size_a=5_000,
            conversions_b=1_300, sample_size_b=10_000,
            alpha=0.05, planned_sample_size=10_000,
        )

        self.assertTrue(result.is_conclusive)
        self.assertGreater(result.effective_sample_size, 0.0)
        self.assertLessEqual(result.progress, 1.0)


if __name__ == "__main__":
    unittest.main()
