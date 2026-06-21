"""End-to-end usage example for the A/B testing platform."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ab_testing_platform import (
    BayesianEngine,
    ExperimentSimulator,
    StatsEngine,
    ThompsonSamplingBandit,
    format_percentage,
)


def main() -> None:
    baseline_conversion_rate = 0.10
    expected_lift = 0.12
    alpha = 0.05
    beta = 0.20

    print("\nA/B Testing & Statistical Simulation Platform")
    print("=" * 52)

    # Frequentist pre-test power analysis.
    required_n = StatsEngine.required_sample_size_per_variation(
        baseline_conversion_rate=baseline_conversion_rate,
        minimum_detectable_effect=expected_lift,
        alpha=alpha,
        beta=beta,
    )
    print(f"\nRequired sample size per variation: {required_n:,}")

    # Monte Carlo experiment simulation.
    simulator = ExperimentSimulator(random_seed=42)
    experiment = simulator.simulate_ab_test(
        sample_size_per_group=required_n,
        baseline_conversion_rate=baseline_conversion_rate,
        expected_lift=expected_lift,
    )
    print("\nSimulated experiment:")
    print(
        f"  A: {experiment.conversions_a:,}/{experiment.sample_size_a:,} "
        f"({format_percentage(experiment.conversion_rate_a)})"
    )
    print(
        f"  B: {experiment.conversions_b:,}/{experiment.sample_size_b:,} "
        f"({format_percentage(experiment.conversion_rate_b)})"
    )

    # Frequentist post-test inference.
    frequentist_result = StatsEngine.two_proportion_z_test(
        conversions_a=experiment.conversions_a,
        sample_size_a=experiment.sample_size_a,
        conversions_b=experiment.conversions_b,
        sample_size_b=experiment.sample_size_b,
        alpha=alpha,
    )
    print("\nFrequentist inference:")
    print(f"  Absolute lift: {format_percentage(frequentist_result.absolute_lift)}")
    print(f"  Relative lift: {format_percentage(frequentist_result.relative_lift)}")
    print(f"  z-statistic: {frequentist_result.z_statistic:.4f}")
    print(f"  p-value: {frequentist_result.p_value:.6f}")
    print(f"  Significant at alpha={alpha}: {frequentist_result.is_significant}")
    print(
        "  95% CI for absolute lift: "
        f"[{format_percentage(frequentist_result.ci_lower)}, "
        f"{format_percentage(frequentist_result.ci_upper)}]"
    )

    # Bayesian Beta-Binomial inference.
    bayesian_engine = BayesianEngine(
        prior_alpha=1.0,
        prior_beta=1.0,
        posterior_samples=250_000,
        random_seed=42,
    )
    bayesian_result = bayesian_engine.analyze(
        conversions_a=experiment.conversions_a,
        sample_size_a=experiment.sample_size_a,
        conversions_b=experiment.conversions_b,
        sample_size_b=experiment.sample_size_b,
    )
    print("\nBayesian inference:")
    print(
        "  Posterior mean A/B: "
        f"{format_percentage(bayesian_result.posterior_mean_a)} / "
        f"{format_percentage(bayesian_result.posterior_mean_b)}"
    )
    print(f"  Prob(B > A): {format_percentage(bayesian_result.probability_b_better)}")
    print(
        "  Expected loss if choose A: "
        f"{format_percentage(bayesian_result.expected_loss_choose_a)}"
    )
    print(
        "  Expected loss if choose B: "
        f"{format_percentage(bayesian_result.expected_loss_choose_b)}"
    )
    print(
        "  95% credible interval for absolute lift: "
        f"[{format_percentage(bayesian_result.credible_interval_uplift[0])}, "
        f"{format_percentage(bayesian_result.credible_interval_uplift[1])}]"
    )

    # Thompson Sampling dynamic traffic allocation demo.
    bandit = ThompsonSamplingBandit(
        true_conversion_rates={
            "A": baseline_conversion_rate,
            "B": baseline_conversion_rate * (1.0 + expected_lift),
        },
        random_seed=42,
    )
    bandit_summary = bandit.run(n_rounds=20_000)
    print("\nThompson Sampling bandit simulation:")
    for arm in sorted(bandit_summary.pulls):
        print(
            f"  Arm {arm}: pulls={bandit_summary.pulls[arm]:,}, "
            f"allocation={format_percentage(bandit_summary.allocation_rates[arm])}, "
            f"observed CVR={format_percentage(bandit_summary.conversion_rates[arm])}"
        )
    print(f"  Cumulative reward: {bandit_summary.cumulative_reward:,}")
    print(f"  Expected regret vs always-best arm: {bandit_summary.regret:.2f}")


if __name__ == "__main__":
    main()
