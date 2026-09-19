"""Typed result models for the A/B testing platform."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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
class SequentialResult:
    """
    Anytime-valid interval for the absolute lift, safe to inspect repeatedly.

    Unlike :class:`FrequentistResult`, every field here remains valid no matter
    how many times the experiment has already been looked at, so ``is_conclusive``
    can be acted on the moment it flips without inflating the error rate.
    """

    absolute_lift: float
    ci_lower: float
    ci_upper: float
    always_valid_p_value: float
    is_conclusive: bool
    direction: Optional[str]
    alpha: float
    effective_sample_size: float
    planned_sample_size: int

    @property
    def progress(self) -> float:
        """Fraction of the planned sample size collected so far, capped at 1.0."""

        return min(1.0, safe_divide(self.effective_sample_size, self.planned_sample_size))


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


@dataclass(frozen=True)
class CUPEDResult:
    """Results from Controlled-experiment Using Pre-Experiment Data (CUPED)."""

    raw_mean_control: float
    raw_mean_treatment: float
    raw_lift: float
    raw_variance: float
    adjusted_mean_control: float
    adjusted_mean_treatment: float
    adjusted_lift: float
    adjusted_variance: float
    theta: float
    correlation: float
    variance_reduction_pct: float
    sample_size_savings_pct: float
    ci_lower: float
    ci_upper: float
    p_value: float
    is_significant: bool


@dataclass(frozen=True)
class DeltaMethodResult:
    """Results of a cluster-robust ratio metric comparison using the Delta Method."""

    ratio_control: float
    ratio_treatment: float
    absolute_lift: float
    relative_lift: float
    se_control: float
    se_treatment: float
    se_difference: float
    z_statistic: float
    p_value: float
    ci_lower: float
    ci_upper: float
    is_significant: bool
    num_clusters_control: int
    num_clusters_treatment: int


@dataclass(frozen=True)
class ContextualBanditResult:
    """Summary of a Contextual Bandit (LinUCB) simulation run."""

    rounds: int
    num_arms: int
    context_dim: int
    cumulative_reward: float
    cumulative_regret: float
    arm_pull_counts: Dict[str, int]
    arm_rewards: Dict[str, float]
    history_rounds: List[int]
    history_regrets: List[float]
    history_rewards: List[float]


@dataclass(frozen=True)
class CandidateFeature:
    """A winning experiment variant / feature proposed for production deployment."""

    feature_id: str
    name: str
    category: str
    expected_value: float  # Annualized incremental value/revenue ($)
    cost: float  # Implementation & maintenance cost ($)
    latency_ms: float  # Server/API latency overhead (ms)
    effort_points: float  # Engineering effort (story points / person-weeks)
    risk_score: float = 0.0  # Operational risk factor in [0, 1]
    conflict_group: Optional[str] = None  # Mutual exclusion grouping (e.g. "checkout_flow")
    defensible_floor_value: Optional[float] = None  # Conservative lower-bound value ($)
    downstream_churn_risk: float = 0.0  # Retention risk factor in [0, 1]
    is_mandatory: bool = False  # Mandatory feature deployment (e.g. compliance requirement)


@dataclass(frozen=True)
class OptimizationResult:
    """Global optimum for the multi-dimensional knapsack feature roll-out."""

    selected_features: List[CandidateFeature]
    rejected_features: List[CandidateFeature]
    total_value: float
    total_cost: float
    total_latency_ms: float
    total_effort_points: float
    budget_utilization_pct: float
    latency_utilization_pct: float
    effort_utilization_pct: float
    is_feasible: bool
    status_message: str
    efficient_frontier: List[Dict[str, float]]
    is_robust: bool = False
    churn_penalty_deducted: float = 0.0


@dataclass(frozen=True)
class SubgroupMetric:
    """CATE estimation and inference for a specific user segment."""

    segment_name: str
    sample_size_a: int
    conversions_a: int
    cvr_a: float
    sample_size_b: int
    conversions_b: int
    cvr_b: float
    absolute_lift: float
    relative_lift: float
    se_difference: float
    z_score: float
    p_value: float
    ci_lower: float
    ci_upper: float
    is_significant: bool
    interaction_p_value: Optional[float] = None
    interaction_significant: bool = False


@dataclass(frozen=True)
class HTEAnalysisResult:
    """Heterogeneous Treatment Effect analysis across a segmentation dimension."""

    dimension: str
    overall_ate: float
    subgroups: List[SubgroupMetric]
    heterogeneity_p_value: float
    has_heterogeneity: bool
    top_performing_segment: str
    worst_performing_segment: str


@dataclass(frozen=True)
class GuardrailMetric:
    """Multi-metric guardrail tracking with FDR adjustment."""

    metric_name: str
    control_value: float
    treatment_value: float
    delta: float
    relative_change: float
    raw_p_value: float
    adjusted_p_value: float  # Benjamini-Hochberg corrected
    direction_favorable: str  # "lower" (e.g. latency, churn) or "higher" (e.g. rpm)
    threshold_pct: float  # Max allowable degradation percentage
    is_violated: bool
    status: str  # "PASS", "WARN", "FAIL"


@dataclass(frozen=True)
class GuardrailAuditResult:
    """Enterprise multi-metric guardrail audit with FDR control."""

    metrics: List[GuardrailMetric]
    fdr_alpha: float
    has_critical_violations: bool
    summary_verdict: str


