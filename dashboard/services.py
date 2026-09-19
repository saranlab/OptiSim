"""Application service layer for running dashboard analyses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

import numpy as np

from ab_testing_platform import (
    BayesianEngine,
    ContextualBanditResult,
    CUPEDEngine,
    CUPEDResult,
    DeltaMethodEngine,
    DeltaMethodResult,
    ExperimentSimulator,
    LinUCBBandit,
    SequentialTest,
    StatsEngine,
    ThompsonSamplingBandit,
)


@dataclass(frozen=True)
class DashboardAnalysis:
    """Serializable analysis result consumed by the Django template."""

    required_sample_size: int
    experiment: Dict[str, Any]
    frequentist: Dict[str, Any]
    sequential: Dict[str, Any]
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
        baseline_conversion_rate: float = 10.0,
        expected_lift: float = 12.0,
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
        # The lift field is a *planned* minimum detectable effect in both modes:
        # what the experiment was designed to catch, decided before seeing data.
        planned_mde = (
            abs(float(expected_lift)) / 100.0 if expected_lift is not None else None
        )

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

            # Sample size is a *design* question, so it must be driven by the
            # effect the user cares about detecting - never by the effect they
            # happened to observe. Feeding the observed lift back in as the MDE
            # is circular: a lucky result reports a small "required" n precisely
            # when the evidence is weakest.
            required_n = 0
            if planned_mde and planned_mde > 0.0001:
                try:
                    required_n = StatsEngine.required_sample_size_per_variation(
                        baseline_conversion_rate=cvr_a,
                        minimum_detectable_effect=planned_mde,
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

        # Anytime-valid inference. This is what the recommendation acts on: it
        # stays valid no matter how many times the dashboard has been refreshed.
        #
        # The sequence is narrowest around the horizon it is tuned to, so the
        # tuning constant is only anchored to `required_n` in planning mode,
        # where that number is a genuine pre-declared plan. In real-data mode the
        # user pastes counts from a test whose horizon they never told us - the
        # MDE field belongs to the planning form - so anchoring to it would make
        # the interval conservative for a reason unrelated to their experiment.
        # There the engine falls back to the observed sample size.
        planned_horizon = required_n if (mode != "real" and required_n > 0) else None
        sequential_result = SequentialTest.confidence_sequence(
            conversions_a=conversions_a,
            sample_size_a=sample_size_a,
            conversions_b=conversions_b,
            sample_size_b=sample_size_b,
            alpha=alpha,
            planned_sample_size=planned_horizon,
        )

        # Progress is always measured against the sizing target on screen, which
        # is not necessarily the horizon the sequence was tuned to.
        plan_progress = (
            min(1.0, sequential_result.effective_sample_size / required_n)
            if required_n > 0
            else 1.0
        )

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
        seq_dict = asdict(sequential_result)
        seq_dict["progress"] = sequential_result.progress
        seq_dict["conservative_gross_uplift"] = (
            traffic * sequential_result.ci_lower * rev_per_conv
        )
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

        # ------------------------------------------------------------------
        # Recommendation Engine
        #
        # The verdict is driven by the *sequential* result, never the
        # fixed-horizon p-value. A dashboard is refreshed at will, and a
        # fixed-horizon test only controls alpha for a single pre-committed
        # look; acting on it repeatedly pushes the real false-positive rate to
        # roughly 25%. The confidence sequence is valid at every sample size at
        # once, so the verdict below is safe to act on the moment it appears.
        #
        # There is also exactly one decision rule. Falling back to a Bayesian
        # threshold whenever the frequentist test fails is two shots at the same
        # data; the frequentist and Bayesian panels remain on screen as
        # description, but they no longer trigger a recommendation.
        # ------------------------------------------------------------------
        prob_b_better = bayesian_result.probability_b_better
        seq_p = sequential_result.always_valid_p_value
        seq_lift = sequential_result.absolute_lift
        progress = plan_progress

        if not sequential_result.is_conclusive:
            rec_status = "warning"
            if progress < 1.0:
                remaining = max(0, required_n - int(sequential_result.effective_sample_size))
                rec_title = "Not Yet Conclusive - Keep Collecting"
                rec_message = (
                    f"The always-valid interval for the lift is "
                    f"[{sequential_result.ci_lower:+.2%}, {sequential_result.ci_upper:+.2%}], "
                    f"which still contains zero, so no effect has been established. "
                    f"You are at {progress:.0%} of the planned {required_n:,} users per "
                    f"variation (~{remaining:,} to go). Because this interval is "
                    f"anytime-valid, you may check back as often as you like without "
                    f"inflating the false-positive rate - checking early costs you nothing."
                )
            else:
                rec_title = "No Effect Detected - Stop the Test"
                rec_message = (
                    f"The planned sample of {required_n:,} users per variation is complete "
                    f"and the always-valid interval "
                    f"[{sequential_result.ci_lower:+.2%}, {sequential_result.ci_upper:+.2%}] "
                    f"still contains zero. This is a genuine flat result, not a lack of data. "
                    f"Retain Control (A) and invest the traffic in a bolder hypothesis; "
                    f"running longer chases noise rather than signal."
                )
        elif sequential_result.direction == "b_better":
            # The lift is only reported on winning tests, and conditioning on a
            # win selects for overestimates (the winner's curse). Quote the
            # interval's lower bound as the defensible floor for any business case.
            conservative_gross = traffic * sequential_result.ci_lower * rev_per_conv
            conservative_net = conservative_gross - setup_cost
            if conservative_net < 0 and net_benefit < 0:
                rec_status = "warning"
                rec_title = "Real Effect, but Financially Unviable"
                rec_message = (
                    f"Variant B is a genuine winner (always-valid p = {seq_p:.5f}, lift "
                    f"{seq_lift:+.2%}, interval [{sequential_result.ci_lower:+.2%}, "
                    f"{sequential_result.ci_upper:+.2%}]). However the projected gross uplift "
                    f"of ${gross_uplift:,.2f} over {traffic:,} users does not cover the "
                    f"${setup_cost:,.2f} setup cost (net ${net_benefit:,.2f}). "
                    f"Advise against deployment at current traffic and conversion value."
                )
            else:
                rec_status = "success"
                rec_title = "Deploy Variant B"
                rec_message = (
                    f"Variant B beats the control with an always-valid p-value of {seq_p:.5f} "
                    f"(α = {alpha}); the anytime-valid interval "
                    f"[{sequential_result.ci_lower:+.2%}, {sequential_result.ci_upper:+.2%}] "
                    f"excludes zero, so this holds regardless of how often the test was "
                    f"checked. Bayesian posterior agrees at {prob_b_better:.1%}. "
                    f"Point estimate of net benefit is ${net_benefit:,.2f} (ROI {roi:.1f}%); "
                    f"plan against the conservative floor of ${conservative_net:,.2f}, since "
                    f"lifts measured on winning tests are biased upward."
                )
        else:
            rec_status = "danger"
            rec_title = "Retain Control (A)"
            rec_message = (
                f"Variant B is genuinely worse: always-valid p = {seq_p:.5f} with an interval "
                f"of [{sequential_result.ci_lower:+.2%}, {sequential_result.ci_upper:+.2%}], "
                f"entirely below zero. Bayesian probability that A is better is "
                f"{1.0 - prob_b_better:.1%}. Do not deploy Variant B."
            )

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
            sequential=seq_dict,
            bayesian=asdict(bayesian_result),
            bandit=bandit_data,
            mode=mode,
            recommendation=recommendation_dict,
            chart_data=chart_data,
            financials=financials_dict,
        )

    @staticmethod
    def run_cuped_analysis(
        n_control: int = 5000,
        n_treatment: int = 5000,
        baseline_cvr: float = 0.10,
        true_lift: float = 0.015,
        correlation: float = 0.60,
        alpha: float = 0.05,
        random_seed: int = 42,
    ) -> tuple[CUPEDResult, Dict[str, Any]]:
        """Run a CUPED variance-reduction analysis with synthetic or provided data."""
        y_c, y_t, x_c, x_t = CUPEDEngine.simulate_cuped_data(
            n_control=n_control,
            n_treatment=n_treatment,
            baseline_cvr=baseline_cvr,
            true_lift=true_lift,
            correlation=correlation,
            random_seed=random_seed,
        )
        result = CUPEDEngine.compute(y_c, y_t, x_c, x_t, alpha=alpha)
        chart_data = {
            "raw_control": y_c[:500].tolist(),
            "raw_treatment": y_t[:500].tolist(),
            "x_control": x_c[:500].tolist(),
            "x_treatment": x_t[:500].tolist(),
        }
        return result, chart_data

    @staticmethod
    def run_delta_method_analysis(
        num_users_control: int = 1000,
        num_users_treatment: int = 1000,
        base_ctr: float = 0.08,
        true_lift: float = 0.015,
        mean_sessions: float = 5.0,
        alpha: float = 0.05,
        random_seed: int = 42,
    ) -> tuple[DeltaMethodResult, Dict[str, Any]]:
        """Run Delta Method ratio metric test on clustered user session observations."""
        y_c, n_c, y_t, n_t = DeltaMethodEngine.simulate_clustered_ratio_data(
            num_users_control=num_users_control,
            num_users_treatment=num_users_treatment,
            base_ctr=base_ctr,
            true_lift=true_lift,
            mean_sessions_per_user=mean_sessions,
            random_seed=random_seed,
        )
        result = DeltaMethodEngine.compute(y_c, n_c, y_t, n_t, alpha=alpha)
        # Naive calculation treating sessions independently (anti-pattern)
        sum_y_c, sum_n_c = float(np.sum(y_c)), float(np.sum(n_c))
        sum_y_t, sum_n_t = float(np.sum(y_t)), float(np.sum(n_t))
        p_c = sum_y_c / sum_n_c
        p_t = sum_y_t / sum_n_t
        naive_se = np.sqrt(p_c * (1.0 - p_c) / sum_n_c + p_t * (1.0 - p_t) / sum_n_t)

        comparison = {
            "naive_se": float(naive_se),
            "robust_se": float(result.se_difference),
            "variance_inflation_factor": float(result.se_difference / naive_se) if naive_se > 0 else 1.0,
        }
        return result, comparison

    @staticmethod
    def run_contextual_bandit_simulation(
        n_rounds: int = 2000,
        context_dim: int = 3,
        alpha: float = 1.0,
        random_seed: int = 42,
    ) -> ContextualBanditResult:
        """Run LinUCB contextual bandit simulation."""
        return LinUCBBandit.simulate(
            n_rounds=n_rounds,
            context_dim=context_dim,
            alpha=alpha,
            random_seed=random_seed,
        )
