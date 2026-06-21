"""Typed result models for the A/B testing platform."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from ab_testing_platform.math_utils import safe_divide


@dataclass(frozen=True)
class ExperimentData:
    """Observed binary outcomes for two experiment variations."""

    group_a: np.ndarray
    group_b: np.ndarray

    @property
    def conversions_a(self) -> int:
        return int(np.sum(self.group_a))

    @property
    def conversions_b(self) -> int:
        return int(np.sum(self.group_b))

    @property
    def sample_size_a(self) -> int:
        return int(self.group_a.size)

    @property
    def sample_size_b(self) -> int:
        return int(self.group_b.size)

    @property
    def conversion_rate_a(self) -> float:
        return safe_divide(self.conversions_a, self.sample_size_a)

    @property
    def conversion_rate_b(self) -> float:
        return safe_divide(self.conversions_b, self.sample_size_b)


@dataclass(frozen=True)
class FrequentistResult:
    """Result of a two-sample z-test for independent proportions."""

    conversion_rate_a: float
    conversion_rate_b: float
    absolute_lift: float
    relative_lift: float
    z_statistic: float
    p_value: float
    is_significant: bool
    ci_lower: float
    ci_upper: float
    alpha: float


@dataclass(frozen=True)
class BayesianResult:
    """Posterior comparison metrics for a Bayesian A/B test."""

    posterior_mean_a: float
    posterior_mean_b: float
    probability_b_better: float
    expected_loss_choose_a: float
    expected_loss_choose_b: float
    expected_uplift: float
    credible_interval_uplift: Tuple[float, float]


@dataclass(frozen=True)
class BanditRound:
    """Single logged assignment from a Thompson Sampling simulation."""

    round_index: int
    chosen_arm: str
    reward: int
    posterior_alpha: float
    posterior_beta: float


@dataclass(frozen=True)
class BanditSummary:
    """Aggregate results from a Thompson Sampling simulation."""

    pulls: Dict[str, int]
    rewards: Dict[str, int]
    conversion_rates: Dict[str, float]
    allocation_rates: Dict[str, float]
    cumulative_reward: int
    regret: float
    history: List[BanditRound]
