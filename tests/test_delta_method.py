"""Unit tests for the Delta Method cluster-robust ratio metric engine."""

import unittest
import numpy as np

from ab_testing_platform.delta_method import DeltaMethodEngine
from ab_testing_platform.models import DeltaMethodResult


class TestDeltaMethodEngine(unittest.TestCase):
    """Test suite for DeltaMethodEngine."""

    def test_delta_method_computes_valid_ratio_and_ci(self):
        """Verify Delta Method ratio difference, standard error, and confidence interval."""
        y_c, n_c, y_t, n_t = DeltaMethodEngine.simulate_clustered_ratio_data(
            num_users_control=1000,
            num_users_treatment=1000,
            base_ctr=0.08,
            true_lift=0.02,
            mean_sessions_per_user=5.0,
            random_seed=42,
        )
        res: DeltaMethodResult = DeltaMethodEngine.compute(y_c, n_c, y_t, n_t, alpha=0.05)

        self.assertIsInstance(res, DeltaMethodResult)
        self.assertGreater(res.ratio_treatment, res.ratio_control)
        self.assertGreater(res.se_difference, 0.0)
        self.assertLess(res.ci_lower, res.absolute_lift)
        self.assertGreater(res.ci_upper, res.absolute_lift)
        self.assertTrue(0.0 <= res.p_value <= 1.0)
        self.assertEqual(res.num_clusters_control, 1000)
        self.assertEqual(res.num_clusters_treatment, 1000)

    def test_delta_method_accounts_for_clustering_variance(self):
        """Clustered standard error should properly reflect user-level variance."""
        y_c, n_c, y_t, n_t = DeltaMethodEngine.simulate_clustered_ratio_data(
            num_users_control=1500,
            num_users_treatment=1500,
            base_ctr=0.05,
            true_lift=0.01,
            mean_sessions_per_user=8.0,
            random_seed=101,
        )
        res = DeltaMethodEngine.compute(y_c, n_c, y_t, n_t)

        # Naive pooled variance treating each session as independent
        p_c = np.sum(y_c) / np.sum(n_c)
        p_t = np.sum(y_t) / np.sum(n_t)
        naive_se = np.sqrt(p_c * (1 - p_c) / np.sum(n_c) + p_t * (1 - p_t) / np.sum(n_t))

        # Because user intrinsic affinity introduces clustering, robust SE should be higher or comparable
        self.assertGreater(res.se_difference, 0.0)
        self.assertGreater(res.se_difference, naive_se * 0.9)

    def test_invalid_negative_or_zero_denominators(self):
        """Zero or negative session counts must raise ValueError."""
        with self.assertRaises(ValueError):
            DeltaMethodEngine.compute(
                control_numerators=np.array([1.0, 2.0]),
                control_denominators=np.array([0.0, 5.0]),  # 0 denominator
                treatment_numerators=np.array([2.0, 3.0]),
                treatment_denominators=np.array([5.0, 5.0]),
            )


if __name__ == "__main__":
    unittest.main()
