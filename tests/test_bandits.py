import unittest

from ab_testing_platform import ThompsonSamplingBandit


class TestThompsonSamplingBandit(unittest.TestCase):
    def test_thompson_sampling_pull_counts_sum_to_rounds(self) -> None:
        bandit = ThompsonSamplingBandit({"A": 0.10, "B": 0.12}, random_seed=7)

        summary = bandit.run(n_rounds=500)

        self.assertEqual(sum(summary.pulls.values()), 500)
        self.assertEqual(len(summary.history), 500)
        self.assertEqual(summary.cumulative_reward, sum(summary.rewards.values()))


if __name__ == "__main__":
    unittest.main()
