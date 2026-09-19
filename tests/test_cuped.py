"""Unit tests for the CUPED variance reduction engine."""

import unittest
import numpy as np

from ab_testing_platform.cuped import CUPEDEngine
from ab_testing_platform.models import CUPEDResult


class TestCUPEDEngine(unittest.TestCase):
    """Test suite for CUPEDEngine."""

    def test_cuped_reduces_variance_when_correlated(self):
        """When pre-experiment covariate X is correlated with Y, variance must strictly decrease."""
        y_c, y_t, x_c, x_t = CUPEDEngine.simulate_cuped_data(
            n_control=2000,
            n_treatment=2000,
            baseline_cvr=0.10,
            true_lift=0.02,
            correlation=0.65,
            random_seed=42,
        )
        res: CUPEDResult = CUPEDEngine.compute(y_c, y_t, x_c, x_t, alpha=0.05)

        self.assertIsInstance(res, CUPEDResult)
        self.assertGreater(res.correlation, 0.40)
        self.assertLess(res.adjusted_variance, res.raw_variance)
        self.assertGreater(res.variance_reduction_pct, 15.0)
        self.assertGreater(res.sample_size_savings_pct, 15.0)

    def test_cuped_preserves_unbiased_treatment_effect(self):
        """CUPED adjusted lift must remain an unbiased estimator of true lift."""
        true_lift = 0.025
        lifts = []
        for seed in range(5):
            y_c, y_t, x_c, x_t = CUPEDEngine.simulate_cuped_data(
                n_control=3000,
                n_treatment=3000,
                baseline_cvr=0.10,
                true_lift=true_lift,
                correlation=0.70,
                random_seed=seed,
            )
            res = CUPEDEngine.compute(y_c, y_t, x_c, x_t)
            lifts.append(res.adjusted_lift)

        mean_adjusted_lift = np.mean(lifts)
        self.assertAlmostEqual(mean_adjusted_lift, true_lift, delta=0.01)

    def test_cuped_zero_correlation_falls_back_gracefully(self):
        """When correlation is near zero, adjusted variance is roughly equal to raw variance."""
        rng = np.random.default_rng(123)
        y_c = rng.binomial(1, 0.1, size=1000).astype(float)
        y_t = rng.binomial(1, 0.12, size=1000).astype(float)
        x_c = rng.standard_normal(size=1000)
        x_t = rng.standard_normal(size=1000)

        res = CUPEDEngine.compute(y_c, y_t, x_c, x_t)
        self.assertAlmostEqual(res.adjusted_lift, res.raw_lift, places=3)
        self.assertLess(abs(res.adjusted_variance - res.raw_variance), 0.001)

    def test_invalid_lengths_raise_error(self):
        """Mismatched Y and X lengths must raise ValueError."""
        with self.assertRaises(ValueError):
            CUPEDEngine.compute(
                np.array([1.0, 0.0]),
                np.array([1.0, 0.0]),
                np.array([1.0]),  # length 1 vs 2
                np.array([1.0, 0.0]),
            )


if __name__ == "__main__":
    unittest.main()
