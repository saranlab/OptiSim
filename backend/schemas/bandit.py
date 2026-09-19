"""Multi-armed and Contextual Bandit schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ThompsonSimRequest(BaseModel):
    true_conversion_rates: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping arm name to true underlying conversion rate (e.g. {'Arm_A': 0.12, 'Arm_B': 0.15})",
    )
    n_rounds: int = Field(1000, ge=10, le=50000, description="Total arrivals to simulate")
    delay_rounds: int = Field(0, ge=0, description="Simulated feedback delay in rounds")
    prior_alpha: float = Field(1.0, gt=0.0)
    prior_beta: float = Field(1.0, gt=0.0)
    random_seed: Optional[int] = Field(42, description="RNG seed for reproducible simulation")


class BanditRoundRecord(BaseModel):
    round_index: int
    chosen_arm: str
    reward: int
    posterior_alpha: float
    posterior_beta: float


class ThompsonSimResponse(BaseModel):
    pulls: Dict[str, int]
    rewards: Dict[str, int]
    conversion_rates: Dict[str, float]
    allocation_rates: Dict[str, float]
    cumulative_reward: int
    regret: float
    history_sample: List[BanditRoundRecord]


class LinUCBSimRequest(BaseModel):
    arm_names: List[str] = Field(..., min_length=2, description="Candidate arms (e.g. ['UI_Minimal', 'UI_Rich', 'UI_AI'])")
    n_rounds: int = Field(500, ge=10, le=5000, description="Number of user interactions to simulate")
    context_dim: int = Field(3, ge=1, le=20, description="Dimension of context feature vector")
    alpha: float = Field(1.0, gt=0.0, description="Exploration weight parameter")
    random_seed: Optional[int] = Field(42)


class LinUCBSimResponse(BaseModel):
    arm_pulls: Dict[str, int]
    arm_rewards: Dict[str, int]
    total_reward: int
    ctr: float
    message: str
