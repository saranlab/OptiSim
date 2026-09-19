"""Multi-armed bandit simulation engines."""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional

import numpy as np

from ab_testing_platform.math_utils import safe_divide
from ab_testing_platform.models import BanditRound, BanditSummary, ContextualBanditResult
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

    def run(self, n_rounds: int, delay_rounds: int = 0) -> BanditSummary:
        """
        Simulate dynamic allocation for n_rounds user arrivals.

        Parameters
        ----------
        n_rounds : int
            Total user arrivals.
        delay_rounds : int
            Simulated feedback delay steps. If > 0, posterior updates are deferred
            to model realistic enterprise conversion lags.
        """
        if n_rounds <= 0:
            raise ValidationError("n_rounds must be positive.")
        if delay_rounds < 0:
            raise ValidationError("delay_rounds cannot be negative.")

        arms = list(self.true_conversion_rates.keys())
        posterior_alpha = {arm: self.prior_alpha for arm in arms}
        posterior_beta = {arm: self.prior_beta for arm in arms}
        pulls = {arm: 0 for arm in arms}
        rewards = {arm: 0 for arm in arms}
        history: List[BanditRound] = []

        best_rate = max(self.true_conversion_rates.values())
        cumulative_expected_reward = 0.0

        # Pending updates queue for delayed feedback: list of (apply_at_round, arm, reward)
        pending_queue: List[tuple[int, str, int]] = []

        for round_index in range(1, n_rounds + 1):
            # Apply delayed feedback updates that matured at or before this round
            if delay_rounds > 0 and pending_queue:
                matured = [item for item in pending_queue if item[0] <= round_index]
                for _, arm_to_update, rew in matured:
                    posterior_alpha[arm_to_update] += rew
                    posterior_beta[arm_to_update] += 1 - rew
                pending_queue = [item for item in pending_queue if item[0] > round_index]

            sampled_rates = {
                arm: self.rng.beta(posterior_alpha[arm], posterior_beta[arm])
                for arm in arms
            }
            chosen_arm = max(sampled_rates, key=sampled_rates.get)
            reward = int(self.rng.binomial(1, self.true_conversion_rates[chosen_arm]))

            pulls[chosen_arm] += 1
            rewards[chosen_arm] += reward
            cumulative_expected_reward += self.true_conversion_rates[chosen_arm]

            if delay_rounds == 0:
                posterior_alpha[chosen_arm] += reward
                posterior_beta[chosen_arm] += 1 - reward
            else:
                pending_queue.append((round_index + delay_rounds, chosen_arm, reward))

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


class LinUCBBandit:
    """
    Contextual Bandit using LinUCB with Disjoint Linear Models.

    Reference: Li, Chu, Langford, & Schapire (WSDM 2010).
    A Contextual-Bandit Approach to Personalized News Article Recommendation.
    """

    def __init__(
        self,
        arm_names: List[str],
        context_dim: int,
        alpha: float = 1.0,
        random_seed: Optional[int] = None,
    ) -> None:
        if not arm_names:
            raise ValidationError("At least one arm name is required.")
        if context_dim <= 0:
            raise ValidationError("context_dim must be positive.")

        self.arm_names = list(arm_names)
        self.d = context_dim
        self.alpha = float(alpha)
        self.rng = np.random.default_rng(random_seed)

        # Disjoint model matrices per arm: A = I_d, b = 0_d
        self.A = {arm: np.identity(self.d, dtype=float) for arm in self.arm_names}
        self.b = {arm: np.zeros((self.d, 1), dtype=float) for arm in self.arm_names}

    def select_arm(self, context: np.ndarray) -> str:
        """Select best arm for context vector x_t according to LinUCB index."""
        x = np.asarray(context, dtype=float).reshape((self.d, 1))
        best_arm = self.arm_names[0]
        max_p = -float("inf")

        for arm in self.arm_names:
            A_inv = np.linalg.inv(self.A[arm])
            theta_hat = A_inv @ self.b[arm]
            mean_est = float(np.squeeze(theta_hat.T @ x))
            ridge_width = float(np.sqrt(np.squeeze(x.T @ A_inv @ x)))
            ucb_score = mean_est + self.alpha * ridge_width

            if ucb_score > max_p:
                max_p = ucb_score
                best_arm = arm

        return best_arm

    def update(self, arm: str, context: np.ndarray, reward: float) -> None:
        """Update ridge regression parameters for the chosen arm."""
        x = np.asarray(context, dtype=float).reshape((self.d, 1))
        r = float(reward)
        self.A[arm] += x @ x.T
        self.b[arm] += r * x

    @classmethod
    def simulate(
        cls,
        n_rounds: int = 2000,
        context_dim: int = 3,
        alpha: float = 1.0,
        random_seed: int = 42,
    ) -> ContextualBanditResult:
        """Simulate contextual bandit routing against synthetic user profiles."""
        rng = np.random.default_rng(random_seed)
        arm_names = ["variant_a", "variant_b", "variant_c"]
        bandit = cls(arm_names, context_dim=context_dim, alpha=alpha, random_seed=random_seed)

        # True latent preference weights for each arm: theta*_a
        true_theta = {
            "variant_a": np.array([0.5, -0.2, 0.1]),
            "variant_b": np.array([0.1, 0.6, -0.1]),
            "variant_c": np.array([-0.2, 0.1, 0.7]),
        }

        cumulative_reward = 0.0
        cumulative_regret = 0.0
        pulls = {arm: 0 for arm in arm_names}
        arm_rewards = {arm: 0.0 for arm in arm_names}

        history_rounds: List[int] = []
        history_regrets: List[float] = []
        history_rewards: List[float] = []

        log_interval = max(1, n_rounds // 100)

        for t in range(1, n_rounds + 1):
            # Sample synthetic normalized user context (e.g. [mobile_user, returning_user, high_intent])
            ctx = rng.uniform(0.1, 1.0, size=context_dim)
            ctx = ctx / np.linalg.norm(ctx)

            # Compute true expected rewards for optimal arm
            expected_rewards = {
                arm: float(np.dot(true_theta[arm], ctx)) for arm in arm_names
            }
            optimal_arm = max(expected_rewards, key=expected_rewards.get)
            optimal_reward = expected_rewards[optimal_arm]

            # Bandit chooses arm
            chosen_arm = bandit.select_arm(ctx)
            chosen_expected = expected_rewards[chosen_arm]

            # Binary reward with probability based on logistic link or clipped linear
            prob = np.clip(0.5 + chosen_expected * 0.3, 0.05, 0.95)
            reward = float(rng.binomial(1, prob))

            bandit.update(chosen_arm, ctx, reward)

            pulls[chosen_arm] += 1
            arm_rewards[chosen_arm] += reward
            cumulative_reward += reward

            # Instantaneous expected regret
            instant_regret = max(0.0, optimal_reward - chosen_expected)
            cumulative_regret += instant_regret

            if t % log_interval == 0 or t == n_rounds:
                history_rounds.append(t)
                history_regrets.append(cumulative_regret)
                history_rewards.append(cumulative_reward)

        return ContextualBanditResult(
            rounds=n_rounds,
            num_arms=len(arm_names),
            context_dim=context_dim,
            cumulative_reward=cumulative_reward,
            cumulative_regret=cumulative_regret,
            arm_pull_counts=pulls,
            arm_rewards=arm_rewards,
            history_rounds=history_rounds,
            history_regrets=history_regrets,
            history_rewards=history_rewards,
        )
