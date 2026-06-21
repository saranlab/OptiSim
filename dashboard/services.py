"""Application service layer for running dashboard analyses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

import numpy as np

from ab_testing_platform import (
    BayesianEngine,
    ExperimentSimulator,
    StatsEngine,
    ThompsonSamplingBandit,
)


@dataclass(frozen=True)
class DashboardAnalysis:
    """Serializable analysis result consumed by the Django template."""

    required_sample_size: int
    experiment: Dict[str, Any]
    frequentist: Dict[str, Any]
    bayesian: Dict[str, Any]
    bandit: Dict[str, Any] | None = None
    mode: str = "simulation"
    recommendation: Dict[str, Any] | None = None
    chart_data: Dict[str, Any] | None = None
    financials: Dict[str, Any] | None = None


class ExperimentDashboardService:
    """Coordinates platform engines for one dashboard request."""

    @staticmethod
    def run(
        baseline_conversion_rate: float = 0.10,
        expected_lift: float = 0.12,
        alpha: float = 0.05,
        beta: float = 0.20,
        posterior_samples: int = 100_000,
        bandit_rounds: int = 20_000,
        real_sample_size_a: int | None = None,
        real_conversions_a: int | None = None,
        real_sample_size_b: int | None = None,
        real_conversions_b: int | None = None,
        mode: str = "simulation",
        random_seed: int = 42,
        revenue_per_conversion: float = 10.0,
        implementation_cost: float = 500.0,
        projected_traffic: int = 100000,
    ) -> DashboardAnalysis:
        if mode == "simulation":
            baseline_conversion_rate = float(baseline_conversion_rate) / 100.0
            expected_lift = float(expected_lift) / 100.0

        if mode == "real":
            # Real Data / Inference Mode
            conversions_a = int(real_conversions_a if real_conversions_a is not None else 0)
            sample_size_a = int(real_sample_size_a if real_sample_size_a is not None else 1)
            conversions_b = int(real_conversions_b if real_conversions_b is not None else 0)
            sample_size_b = int(real_sample_size_b if real_sample_size_b is not None else 1)

            cvr_a = conversions_a / sample_size_a if sample_size_a > 0 else 0.0
            cvr_b = conversions_b / sample_size_b if sample_size_b > 0 else 0.0
            observed_lift = (cvr_b - cvr_a) / cvr_a if cvr_a > 0 else 0.0

            # Calculate required sample size post-hoc for the observed lift
            required_n = 0
            if observed_lift > 0.0001:
                try:
                    required_n = StatsEngine.required_sample_size_per_variation(
                        baseline_conversion_rate=cvr_a,
                        minimum_detectable_effect=observed_lift,
                        alpha=alpha,
                        beta=beta,
                    )
                except Exception:
                    required_n = 0

            frequentist_result = StatsEngine.two_proportion_z_test(
                conversions_a=conversions_a,
                sample_size_a=sample_size_a,
                conversions_b=conversions_b,
                sample_size_b=sample_size_b,
                alpha=alpha,
            )

            bayesian_result = BayesianEngine(
                posterior_samples=posterior_samples,
                random_seed=random_seed,
            ).analyze(
                conversions_a=conversions_a,
                sample_size_a=sample_size_a,
                conversions_b=conversions_b,
                sample_size_b=sample_size_b,
            )

            bandit_data = None
        else:
            # Plan & Simulate Mode
            required_n = StatsEngine.required_sample_size_per_variation(
                baseline_conversion_rate=baseline_conversion_rate,
                minimum_detectable_effect=abs(expected_lift),
                alpha=alpha,
                beta=beta,
            )

            simulator = ExperimentSimulator(random_seed=random_seed)
            experiment = simulator.simulate_ab_test(
                sample_size_per_group=required_n,
                baseline_conversion_rate=baseline_conversion_rate,
                expected_lift=expected_lift,
            )

            conversions_a = experiment.conversions_a
            sample_size_a = experiment.sample_size_a
            conversions_b = experiment.conversions_b
            sample_size_b = experiment.sample_size_b
            cvr_a = experiment.conversion_rate_a
            cvr_b = experiment.conversion_rate_b

            frequentist_result = StatsEngine.two_proportion_z_test(
                conversions_a=conversions_a,
                sample_size_a=sample_size_a,
                conversions_b=conversions_b,
                sample_size_b=sample_size_b,
                alpha=alpha,
            )

            bayesian_result = BayesianEngine(
                posterior_samples=posterior_samples,
                random_seed=random_seed,
            ).analyze(
                conversions_a=conversions_a,
                sample_size_a=sample_size_a,
                conversions_b=conversions_b,
                sample_size_b=sample_size_b,
            )

            treatment_rate = baseline_conversion_rate * (1.0 + expected_lift)
            bandit_summary = ThompsonSamplingBandit(
                {"A": baseline_conversion_rate, "B": treatment_rate},
                random_seed=random_seed,
            ).run(n_rounds=bandit_rounds)

            bandit_data = {
                "pulls": bandit_summary.pulls,
                "rewards": bandit_summary.rewards,
                "conversion_rates": bandit_summary.conversion_rates,
                "allocation_rates": bandit_summary.allocation_rates,
                "cumulative_reward": bandit_summary.cumulative_reward,
                "regret": bandit_summary.regret,
            }

        # Financial Impact & ROI Calculations
        rev_per_conv = float(revenue_per_conversion)
        setup_cost = float(implementation_cost)
        traffic = int(projected_traffic)

        gross_uplift = traffic * (cvr_b - cvr_a) * rev_per_conv
        net_benefit = gross_uplift - setup_cost
        roi = (net_benefit / setup_cost * 100.0) if setup_cost > 0 else 0.0

        financials_dict = {
            "revenue_per_conversion": rev_per_conv,
            "implementation_cost": setup_cost,
            "projected_traffic": traffic,
            "gross_uplift": gross_uplift,
            "net_benefit": net_benefit,
            "roi": roi,
        }

        # Calculate visualization variables
        freq_dict = asdict(frequentist_result)
        ci_lower = frequentist_result.ci_lower
        ci_upper = frequentist_result.ci_upper
        abs_lift = frequentist_result.absolute_lift

        # We want the track to scale dynamically based on the CI bounds, but always include 0.0
        bound_min = min(-0.01, ci_lower * 1.25)
        bound_max = max(0.01, ci_upper * 1.25)
        val_range = bound_max - bound_min
        if val_range < 1e-6:
            val_range = 0.02
            bound_min = -0.01
            bound_max = 0.01

        def to_percent(val: float) -> float:
            pct = (val - bound_min) / val_range * 100.0
            return float(np.clip(pct, 0.0, 100.0))

        freq_dict["visual_zero"] = to_percent(0.0)
        freq_dict["visual_lift"] = to_percent(abs_lift)
        freq_dict["visual_ci_lower"] = to_percent(ci_lower)
        freq_dict["visual_ci_upper"] = to_percent(ci_upper)
        freq_dict["visual_ci_width"] = freq_dict["visual_ci_upper"] - freq_dict["visual_ci_lower"]

        # Relative scaling for conversion rates comparison
        max_cvr = max(cvr_a, cvr_b, 0.01)
        experiment_dict = {
            "conversions_a": conversions_a,
            "conversions_b": conversions_b,
            "sample_size_a": sample_size_a,
            "sample_size_b": sample_size_b,
            "conversion_rate_a": cvr_a,
            "conversion_rate_b": cvr_b,
            "visual_width_a": float(np.clip((cvr_a / max_cvr) * 100.0, 5.0, 100.0)),
            "visual_width_b": float(np.clip((cvr_b / max_cvr) * 100.0, 5.0, 100.0)),
        }

        # Recommendation Engine details
        is_significant = frequentist_result.is_significant
        prob_b_better = bayesian_result.probability_b_better
        p_val = frequentist_result.p_value

        if sample_size_a < 100 or sample_size_b < 100:
            rec_status = "warning"
            rec_title = "Warning: Underpowered / Small Sample"
            rec_message = f"The sample size (A: {sample_size_a}, B: {sample_size_b}) is too small to draw reliable statistical conclusions. Continue running the test to gather more traffic."
        elif is_significant:
            if abs_lift > 0:
                if net_benefit < 0:
                    rec_status = "warning"
                    rec_title = "Significant but Financially Unviable"
                    rec_message = f"Variant B statistically outperformed the control (A) with a p-value of {p_val:.5f} (below α = {alpha}) and {prob_b_better:.2%} Bayesian probability. However, the expected gross uplift of ${gross_uplift:,.2f} over {traffic:,} projected users does not cover the setup cost of ${setup_cost:,.2f} (Net Loss: ${abs(net_benefit):,.2f}). Advise against deployment at current traffic/conversion value levels."
                else:
                    rec_status = "success"
                    rec_title = "Deploy Variant B"
                    rec_message = f"Variant B statistically outperformed the control (A) with a p-value of {p_val:.5f} (below α = {alpha}) and {prob_b_better:.2%} Bayesian probability. The observed relative lift is {frequentist_result.relative_lift:.2%}. It is financially viable with an expected net benefit of ${net_benefit:,.2f} (ROI: {roi:.1f}%)."
            else:
                rec_status = "danger"
                rec_title = "Retain Control (A)"
                rec_message = f"Variant B performed statistically worse than the control (A) with a p-value of {p_val:.5f} and {1.0 - prob_b_better:.2%} probability of A being better. Do not deploy Variant B."
        else:
            if prob_b_better >= 0.90:
                rec_status = "warning"
                rec_title = "Inconclusive (Bayesian Trend B > A)"
                rec_message = f"No frequentist significance yet (p = {p_val:.4f} > α = {alpha}), but Bayesian posterior probability indicates a {prob_b_better:.1%} chance that B is superior. We suggest continuing to collect data to verify this trend."
                if net_benefit < 0:
                    rec_message += f" Note: Even if B is superior, the projected net benefit is negative (${net_benefit:,.2f})."
            elif prob_b_better <= 0.10:
                rec_status = "warning"
                rec_title = "Inconclusive (Bayesian Trend A > B)"
                rec_message = f"No frequentist significance yet (p = {p_val:.4f} > α = {alpha}), but Bayesian posterior probability indicates a {(1.0 - prob_b_better):.1%} chance that Control A is superior. Consider halting the test or trying a new treatment."
            else:
                rec_status = "warning"
                rec_title = "Inconclusive - Keep Testing"
                rec_message = f"No statistically significant difference detected (p = {p_val:.4f} > α = {alpha}). Bayesian probability B > A is {prob_b_better:.1%}, showing high overlap between distributions. Continue testing."

        recommendation_dict = {
            "status": rec_status,
            "title": rec_title,
            "message": rec_message,
        }

        # Generate chart data
        chart_data = {
            "convergence": [],
            "bandit": [],
            "posterior": {
                "conv_a": conversions_a,
                "size_a": sample_size_a,
                "conv_b": conversions_b,
                "size_b": sample_size_b,
            }
        }

        if mode == "simulation":
            # 1. Convergence data (50 points)
            n_points = 50
            step = max(1, sample_size_a // n_points)
            for i in range(1, n_points + 1):
                idx = i * step
                if idx > sample_size_a:
                    idx = sample_size_a
                sub_a = experiment.group_a[:idx]
                sub_b = experiment.group_b[:idx]
                cum_cvr_a = float(np.sum(sub_a)) / idx if idx > 0 else 0.0
                cum_cvr_b = float(np.sum(sub_b)) / idx if idx > 0 else 0.0
                chart_data["convergence"].append({
                    "sample_size": idx,
                    "cvr_a": cum_cvr_a,
                    "cvr_b": cum_cvr_b
                })
                if idx == sample_size_a:
                    break

            # 2. Bandit regret history (50 points)
            if bandit_data is not None and bandit_summary is not None:
                bandit_step = max(1, bandit_rounds // n_points)
                cum_pulls = {"A": 0, "B": 0}
                cum_rewards = {"A": 0, "B": 0}
                cum_regret = 0.0
                best_rate = max(baseline_conversion_rate, treatment_rate)
                
                for idx, r in enumerate(bandit_summary.history):
                    cum_pulls[r.chosen_arm] += 1
                    cum_rewards[r.chosen_arm] += r.reward
                    
                    actual_rate = baseline_conversion_rate if r.chosen_arm == "A" else treatment_rate
                    cum_regret += (best_rate - actual_rate)
                    
                    if (idx + 1) % bandit_step == 0 or (idx + 1) == bandit_rounds:
                        chart_data["bandit"].append({
                            "round": idx + 1,
                            "cvr_a": float(cum_rewards["A"] / cum_pulls["A"]) if cum_pulls["A"] > 0 else 0.0,
                            "cvr_b": float(cum_rewards["B"] / cum_pulls["B"]) if cum_pulls["B"] > 0 else 0.0,
                            "regret": float(cum_regret)
                        })

        return DashboardAnalysis(
            required_sample_size=required_n,
            experiment=experiment_dict,
            frequentist=freq_dict,
            bayesian=asdict(bayesian_result),
            bandit=bandit_data,
            mode=mode,
            recommendation=recommendation_dict,
            chart_data=chart_data,
            financials=financials_dict,
        )
