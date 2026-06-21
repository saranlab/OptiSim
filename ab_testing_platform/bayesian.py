"""Bayesian Beta-Binomial inference for binary A/B tests."""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from ab_testing_platform.math_utils import safe_divide
from ab_testing_platform.models import BayesianResult
from ab_testing_platform.validation import (
    ValidationError,
    validate_count_data,
    validate_probability,
)


class BayesianEngine:
    """Beta-Binomial Bayesian inference engine for binary conversion tests."""

    def __init__(
        self,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        posterior_samples: int = 250_000,
        random_seed: Optional[int] = None,
    ) -> None:
        if prior_alpha <= 0 or prior_beta <= 0:
            raise ValidationError("Beta prior parameters must be positive.")
        if posterior_samples <= 0:
            raise ValidationError("posterior_samples must be positive.")

        self.prior_alpha = float(prior_alpha)
        self.prior_beta = float(prior_beta)
        self.posterior_samples = int(posterior_samples)
        self.rng = np.random.default_rng(random_seed)

    def analyze(
        self,
        conversions_a: int,
        sample_size_a: int,
        conversions_b: int,
        sample_size_b: int,
        credible_interval_mass: float = 0.95,
    ) -> BayesianResult:
        """
        Compare posterior conversion rates for A and B.

        Expected loss is reported in absolute conversion-rate units. For
        example, 0.002 means an expected loss of 0.2 percentage points.
        """

        validate_count_data(conversions_a, sample_size_a, "A")
        validate_count_data(conversions_b, sample_size_b, "B")
        validate_probability(
            credible_interval_mass, "credible_interval_mass", inclusive=False
        )

        alpha_a, beta_a = self._posterior_parameters(conversions_a, sample_size_a)
        alpha_b, beta_b = self._posterior_parameters(conversions_b, sample_size_b)

        posterior_a = self.rng.beta(alpha_a, beta_a, size=self.posterior_samples)
        posterior_b = self.rng.beta(alpha_b, beta_b, size=self.posterior_samples)
        uplift_samples = posterior_b - posterior_a
        lower_q = (1.0 - credible_interval_mass) / 2.0
        upper_q = 1.0 - lower_q

        return BayesianResult(
            posterior_mean_a=safe_divide(alpha_a, alpha_a + beta_a),
            posterior_mean_b=safe_divide(alpha_b, alpha_b + beta_b),
            probability_b_better=float(np.mean(posterior_b > posterior_a)),
            expected_loss_choose_a=float(np.mean(np.maximum(uplift_samples, 0.0))),
            expected_loss_choose_b=float(np.mean(np.maximum(-uplift_samples, 0.0))),
            expected_uplift=float(np.mean(uplift_samples)),
            credible_interval_uplift=(
                float(np.quantile(uplift_samples, lower_q)),
                float(np.quantile(uplift_samples, upper_q)),
            ),
        )

    def _posterior_parameters(
        self, conversions: int, sample_size: int
    ) -> Tuple[float, float]:
        failures = sample_size - conversions
        return self.prior_alpha + conversions, self.prior_beta + failures
