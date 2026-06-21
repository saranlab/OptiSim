"""Multi-armed bandit simulation engines."""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional

import numpy as np

from ab_testing_platform.math_utils import safe_divide
from ab_testing_platform.models import BanditRound, BanditSummary
from ab_testing_platform.validation import ValidationError, validate_probability


class ThompsonSamplingBandit:
    """Thompson Sampling simulator for dynamic traffic allocation."""

    def __init__(
        self,
        true_conversion_rates: Mapping[str, float],
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        random_seed: Optional[int] = None,
    ) -> None:
        if not true_conversion_rates:
            raise ValidationError("At least one arm is required.")
        if prior_alpha <= 0 or prior_beta <= 0:
            raise ValidationError("Beta prior parameters must be positive.")

        for arm, rate in true_conversion_rates.items():
            validate_probability(rate, f"true_conversion_rates[{arm!r}]")

        self.true_conversion_rates = dict(true_conversion_rates)
        self.prior_alpha = float(prior_alpha)
        self.prior_beta = float(prior_beta)
        self.rng = np.random.default_rng(random_seed)

    def run(self, n_rounds: int) -> BanditSummary:
        """
        Simulate dynamic allocation for n_rounds user arrivals.

        Each round samples a plausible conversion rate for every arm from its
        posterior, assigns traffic to the arm with the highest draw, observes a
        Bernoulli reward, and updates that arm's posterior.
        """

        if n_rounds <= 0:
            raise ValidationError("n_rounds must be positive.")

        arms = list(self.true_conversion_rates.keys())
        posterior_alpha = {arm: self.prior_alpha for arm in arms}
        posterior_beta = {arm: self.prior_beta for arm in arms}
        pulls = {arm: 0 for arm in arms}
        rewards = {arm: 0 for arm in arms}
        history: List[BanditRound] = []

        best_rate = max(self.true_conversion_rates.values())
        cumulative_expected_reward = 0.0

        for round_index in range(1, n_rounds + 1):
            sampled_rates = {
                arm: self.rng.beta(posterior_alpha[arm], posterior_beta[arm])
                for arm in arms
            }
            chosen_arm = max(sampled_rates, key=sampled_rates.get)
            reward = int(self.rng.binomial(1, self.true_conversion_rates[chosen_arm]))

            pulls[chosen_arm] += 1
            rewards[chosen_arm] += reward
            posterior_alpha[chosen_arm] += reward
            posterior_beta[chosen_arm] += 1 - reward
            cumulative_expected_reward += self.true_conversion_rates[chosen_arm]

            history.append(
                BanditRound(
                    round_index=round_index,
                    chosen_arm=chosen_arm,
                    reward=reward,
                    posterior_alpha=posterior_alpha[chosen_arm],
                    posterior_beta=posterior_beta[chosen_arm],
                )
            )

        conversion_rates: Dict[str, float] = {
            arm: safe_divide(rewards[arm], pulls[arm]) for arm in arms
        }
        allocation_rates: Dict[str, float] = {
            arm: safe_divide(pulls[arm], n_rounds) for arm in arms
        }
        regret = (best_rate * n_rounds) - cumulative_expected_reward

        return BanditSummary(
            pulls=pulls,
            rewards=rewards,
            conversion_rates=conversion_rates,
            allocation_rates=allocation_rates,
            cumulative_reward=sum(rewards.values()),
            regret=regret,
            history=history,
        )
