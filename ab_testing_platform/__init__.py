"""
A/B Testing & Statistical Simulation Platform.

Notebook-friendly public API for simulation, frequentist inference, Bayesian
inference, and Thompson Sampling bandit experiments.
"""

from ab_testing_platform.bandits import LinUCBBandit, ThompsonSamplingBandit
from ab_testing_platform.bayesian import BayesianEngine
from ab_testing_platform.cuped import CUPEDEngine
from ab_testing_platform.delta_method import DeltaMethodEngine
from ab_testing_platform.formatting import format_percentage
from ab_testing_platform.frequentist import StatsEngine
from ab_testing_platform.models import (
    BanditRound,
    BanditSummary,
    BayesianResult,
    CandidateFeature,
    ContextualBanditResult,
    CUPEDResult,
    DeltaMethodResult,
    ExperimentData,
    FrequentistResult,
    GuardrailAuditResult,
    GuardrailMetric,
    HTEAnalysisResult,
    OptimizationResult,
    SequentialResult,
    SubgroupMetric,
)
from ab_testing_platform.guardrails import GuardrailEngine
from ab_testing_platform.hte import HTEEngine
from ab_testing_platform.optimizer import PortfolioOptimizer
from ab_testing_platform.sequential import SequentialTest
from ab_testing_platform.simulation import ExperimentSimulator
from ab_testing_platform.validation import ValidationError

__all__ = [
    "BanditRound",
    "BanditSummary",
    "BayesianEngine",
    "BayesianResult",
    "CandidateFeature",
    "ContextualBanditResult",
    "CUPEDEngine",
    "CUPEDResult",
    "DeltaMethodEngine",
    "DeltaMethodResult",
    "ExperimentData",
    "ExperimentSimulator",
    "FrequentistResult",
    "GuardrailAuditResult",
    "GuardrailEngine",
    "GuardrailMetric",
    "HTEAnalysisResult",
    "HTEEngine",
    "LinUCBBandit",
    "OptimizationResult",
    "PortfolioOptimizer",
    "SequentialResult",
    "SequentialTest",
    "StatsEngine",
    "SubgroupMetric",
    "ThompsonSamplingBandit",
    "ValidationError",
    "format_percentage",
]
