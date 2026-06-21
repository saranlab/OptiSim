import unittest

from ab_testing_platform import BayesianEngine


class TestBayesianEngine(unittest.TestCase):
    def test_bayesian_analysis_returns_valid_probabilities_and_interval(self) -> None:
        engine = BayesianEngine(posterior_samples=10_000, random_seed=7)

        result = engine.analyze(
            conversions_a=100,
            sample_size_a=1_000,
            conversions_b=125,
            sample_size_b=1_000,
        )

        self.assertGreaterEqual(result.probability_b_better, 0.0)
        self.assertLessEqual(result.probability_b_better, 1.0)
        self.assertGreaterEqual(result.posterior_mean_a, 0.0)
        self.assertLessEqual(result.posterior_mean_a, 1.0)
        self.assertGreaterEqual(result.posterior_mean_b, 0.0)
        self.assertLessEqual(result.posterior_mean_b, 1.0)
        self.assertLessEqual(
            result.credible_interval_uplift[0], result.credible_interval_uplift[1]
        )


if __name__ == "__main__":
    unittest.main()
