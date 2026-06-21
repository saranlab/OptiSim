import numpy as np
import unittest

from ab_testing_platform import ExperimentSimulator, ValidationError


class TestExperimentSimulator(unittest.TestCase):
    def test_simulation_returns_binary_arrays_of_requested_size(self) -> None:
        simulator = ExperimentSimulator(random_seed=7)

        experiment = simulator.simulate_ab_test(
            sample_size_per_group=1_000,
            baseline_conversion_rate=0.10,
            expected_lift=0.15,
        )

        self.assertEqual(experiment.sample_size_a, 1_000)
        self.assertEqual(experiment.sample_size_b, 1_000)
        self.assertTrue(set(np.unique(experiment.group_a)).issubset({0, 1}))
        self.assertTrue(set(np.unique(experiment.group_b)).issubset({0, 1}))


    def test_simulation_rejects_invalid_parameters(self) -> None:
        simulator = ExperimentSimulator(random_seed=7)

        with self.assertRaises(ValidationError):
            simulator.simulate_ab_test(
                sample_size_per_group=0,
                baseline_conversion_rate=0.10,
                expected_lift=0.15,
            )

        with self.assertRaises(ValidationError):
            simulator.simulate_ab_test(
                sample_size_per_group=100,
                baseline_conversion_rate=1.50,
                expected_lift=0.15,
            )


if __name__ == "__main__":
    unittest.main()
