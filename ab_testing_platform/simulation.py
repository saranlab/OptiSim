"""Monte Carlo simulation for A/B experiments."""

from __future__ import annotations

from typing import Optional

import numpy as np

from ab_testing_platform.models import ExperimentData
from ab_testing_platform.validation import ValidationError, validate_probability


class ExperimentSimulator:
    """Monte Carlo simulator for binary user conversion behavior."""

    def __init__(self, random_seed: Optional[int] = None) -> None:
        self.rng = np.random.default_rng(random_seed)

    def simulate_ab_test(
        self,
        sample_size_per_group: int,
        baseline_conversion_rate: float,
        expected_lift: float,
    ) -> ExperimentData:
        """
        Simulate A/B conversion outcomes using Bernoulli draws.

        Args:
            sample_size_per_group: Number of users assigned to each group.
            baseline_conversion_rate: Conversion probability for Group A.
            expected_lift: Relative lift for Group B. Example: 0.10 means B is
                expected to convert 10% higher than A.

        Returns:
            ExperimentData containing 0/1 outcomes for Groups A and B.
        """

        if sample_size_per_group <= 0:
            raise ValidationError("sample_size_per_group must be positive.")
        validate_probability(baseline_conversion_rate, "baseline_conversion_rate")
        if expected_lift <= -1.0:
            raise ValidationError("expected_lift must be greater than -1.0.")

        treatment_rate = baseline_conversion_rate * (1.0 + expected_lift)
        validate_probability(treatment_rate, "derived treatment conversion rate")

        group_a = self.rng.binomial(1, baseline_conversion_rate, sample_size_per_group)
        group_b = self.rng.binomial(1, treatment_rate, sample_size_per_group)
        return ExperimentData(group_a=group_a.astype(int), group_b=group_b.astype(int))
