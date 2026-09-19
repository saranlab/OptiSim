import unittest
import numpy as np

from ab_testing_platform import LinUCBBandit, ThompsonSamplingBandit
from ab_testing_platform.models import ContextualBanditResult


class TestThompsonSamplingBandit(unittest.TestCase):
    def test_thompson_sampling_pull_counts_sum_to_rounds(self) -> None:
        bandit = ThompsonSamplingBandit({"A": 0.10, "B": 0.12}, random_seed=7)

        summary = bandit.run(n_rounds=500)

        self.assertEqual(sum(summary.pulls.values()), 500)
        self.assertEqual(len(summary.history), 500)
        self.assertEqual(summary.cumulative_reward, sum(summary.rewards.values()))

    def test_delayed_feedback_runs_correctly(self) -> None:
        """Delayed feedback should accumulate rewards and defer posterior updates."""
        bandit = ThompsonSamplingBandit({"A": 0.10, "B": 0.15}, random_seed=42)
        summary = bandit.run(n_rounds=1000, delay_rounds=50)

        self.assertEqual(sum(summary.pulls.values()), 1000)
        self.assertEqual(summary.cumulative_reward, sum(summary.rewards.values()))
        self.assertGreater(summary.cumulative_reward, 50)


class TestLinUCBBandit(unittest.TestCase):
    def test_linucb_simulation_returns_valid_result(self) -> None:
        """LinUCB simulation should run and exhibit sub-linear regret growth."""
        res: ContextualBanditResult = LinUCBBandit.simulate(
            n_rounds=1000,
            context_dim=3,
            alpha=1.0,
            random_seed=42,
        )

        self.assertEqual(res.rounds, 1000)
        self.assertEqual(res.num_arms, 3)
        self.assertEqual(sum(res.arm_pull_counts.values()), 1000)
        self.assertGreater(res.cumulative_reward, 200)
        self.assertGreater(len(res.history_rounds), 10)
        self.assertGreater(res.history_regrets[-1], 0.0)


if __name__ == "__main__":
    unittest.main()
