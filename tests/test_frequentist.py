import unittest

from ab_testing_platform import StatsEngine


class TestStatsEngine(unittest.TestCase):
    def test_power_analysis_returns_positive_integer(self) -> None:
        sample_size = StatsEngine.required_sample_size_per_variation(
            baseline_conversion_rate=0.10,
            minimum_detectable_effect=0.10,
            alpha=0.05,
            beta=0.20,
        )

        self.assertIsInstance(sample_size, int)
        self.assertGreater(sample_size, 0)


    def test_z_test_returns_bounded_p_value_and_lift_metrics(self) -> None:
        result = StatsEngine.two_proportion_z_test(
            conversions_a=100,
            sample_size_a=1_000,
            conversions_b=125,
            sample_size_b=1_000,
        )

        self.assertGreaterEqual(result.p_value, 0.0)
        self.assertLessEqual(result.p_value, 1.0)
        self.assertAlmostEqual(result.absolute_lift, 0.025)
        self.assertAlmostEqual(result.relative_lift, 0.25)
        self.assertLessEqual(result.ci_lower, result.absolute_lift)
        self.assertGreaterEqual(result.ci_upper, result.absolute_lift)


if __name__ == "__main__":
    unittest.main()
