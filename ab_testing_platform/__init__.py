"""
A/B Testing & Statistical Simulation Platform.

Notebook-friendly public API for simulation, frequentist inference, Bayesian
inference, and Thompson Sampling bandit experiments.
"""

from ab_testing_platform.bandits import ThompsonSamplingBandit
from ab_testing_platform.bayesian import BayesianEngine
from ab_testing_platform.formatting import format_percentage
from ab_testing_platform.frequentist import StatsEngine
from ab_testing_platform.models import (
    BanditRound,
    BanditSummary,
    BayesianResult,
    ExperimentData,
    FrequentistResult,
)
from ab_testing_platform.simulation import ExperimentSimulator
from ab_testing_platform.validation import ValidationError

__all__ = [
    "BanditRound",
    "BanditSummary",
    "BayesianEngine",
    "BayesianResult",
    "ExperimentData",
    "ExperimentSimulator",
    "FrequentistResult",
    "StatsEngine",
    "ThompsonSamplingBandit",
    "ValidationError",
    "format_percentage",
]
