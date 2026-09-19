"""Operations Research: Multi-Constraint 0-1 Knapsack and Robust Optimization schemas."""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CandidateFeatureInput(BaseModel):
    feature_id: str = Field(..., description="Unique identifier (e.g. 'EXP_SEARCH_V2')")
    name: str = Field(..., description="Human-readable feature name")
    category: str = Field("Core", description="Business domain or engineering category")
    expected_value: float = Field(..., description="Projected annual impact / unlocked ARR ($)")
    cost: float = Field(..., ge=0.0, description="Cloud infrastructure / maintenance cost ($)")
    latency_ms: float = Field(..., description="Net latency impact in ms (can be negative for optimizations)")
    effort_points: float = Field(..., ge=0.0, description="Engineering story points")
    defensible_floor_value: Optional[float] = Field(None, description="Conservative 95% lower bound value ($)")
    downstream_churn_risk: float = Field(0.0, ge=0.0, description="Projected downstream churn risk penalty ($)")
    is_mandatory: bool = Field(False, description="Must be deployed (e.g. compliance requirement)")
    mutual_exclusive_group: Optional[str] = Field(None, description="Group tag: at most 1 feature in group can be picked")


class PortfolioOptimizeRequest(BaseModel):
    features: List[CandidateFeatureInput] = Field(..., min_length=1, description="Candidate features pool")
    max_budget: float = Field(10000.0, ge=0.0, description="Maximum budget SLA ($)")
    max_latency_ms: float = Field(50.0, description="Maximum aggregated latency budget (ms)")
    max_effort_points: float = Field(40.0, ge=0.0, description="Maximum sprint engineering capacity")
    robust_mode: bool = Field(True, description="True for Conservative Defensible Floor; False for Naive Expected Value")
    churn_penalty_weight: float = Field(1.0, ge=0.0, description="Weight multiplier on downstream churn risk penalty")
    frontier_steps: int = Field(15, ge=2, le=50, description="Granularity of efficient frontier points")


class SelectedFeatureResponse(BaseModel):
    feature_id: str
    name: str
    category: str
    expected_value: float
    defensible_floor_value: Optional[float] = None
    cost: float
    latency_ms: float
    effort_points: float
    downstream_churn_risk: float = 0.0
    is_mandatory: bool = False
    mutual_exclusive_group: Optional[str] = None


class EfficientFrontierPoint(BaseModel):
    budget: float
    value: float
    num_selected: int


class PortfolioOptimizeResponse(BaseModel):
    selected_features: List[SelectedFeatureResponse]
    rejected_features: List[SelectedFeatureResponse]
    total_value: float
    total_cost: float
    total_latency_ms: float
    total_effort_points: float
    budget_utilization_pct: float
    latency_utilization_pct: float
    effort_utilization_pct: float
    is_feasible: bool
    status_message: str
    efficient_frontier: List[EfficientFrontierPoint]
    is_robust: bool
    churn_penalty_deducted: float
