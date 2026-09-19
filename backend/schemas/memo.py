"""Executive Decision Memo schemas."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class MemoRequest(BaseModel):
    experiment_name: str = Field("Checkout Flow Modernization", description="Experiment Title")
    primary_metric: str = Field("Checkout Conversion Rate (CVR)", description="Primary business metric")
    control_val: float = Field(0.1240, description="Control baseline rate / value")
    treatment_val: float = Field(0.1410, description="Treatment observed rate / value")
    lift_pct: float = Field(13.71, description="Relative lift in percent")
    ci_lower: float = Field(0.0062, description="Anytime-valid 95% CI lower bound")
    ci_upper: float = Field(0.0278, description="Anytime-valid 95% CI upper bound")
    sample_size: int = Field(24000, ge=1)
    is_significant: bool = Field(True)
    guardrails_passed: bool = Field(True)
    recommended_action: str = Field("SHIP_TO_100_PERCENT", description="E.g. SHIP_TO_100_PERCENT, CONTINUE_SAMPLING, ABORT")
    portfolio_value: Optional[float] = Field(None, description="Unlocked portfolio value from OR knapsack ($)")
    subgroups_heterogeneity: Optional[bool] = Field(None, description="Whether Cochran's Q detected heterogeneity")


class MemoResponse(BaseModel):
    markdown: str
    executive_verdict: str
    timestamp: str
