"""Experimentation schemas: Sequential testing, CUPED variance reduction, and Delta Method."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SequentialStreamRequest(BaseModel):
    control_conversions: List[int] = Field(..., description="Binary stream of control conversions")
    treatment_conversions: List[int] = Field(..., description="Binary stream of treatment conversions")
    alpha: float = Field(0.05, ge=0.001, le=0.5, description="Significance level (Type I error rate)")
    v_opt: float = Field(0.05, gt=0.0, description="Variance tuning parameter for empirical betting")


class SequentialAnalysisResponse(BaseModel):
    sample_sizes: List[int]
    tau_estimates: List[float]
    ci_lowers: List[float]
    ci_uppers: List[float]
    stopped_early: bool
    stopping_sample: Optional[int] = None
    decision: str
    relative_lift_pct: float
    p_value_anytime: float


class CUPEDRequest(BaseModel):
    y_control: List[float] = Field(..., description="Post-experiment metric (Control)")
    y_treatment: List[float] = Field(..., description="Post-experiment metric (Treatment)")
    x_control: List[float] = Field(..., description="Pre-experiment covariate metric (Control)")
    x_treatment: List[float] = Field(..., description="Pre-experiment covariate metric (Treatment)")


class CUPEDResponse(BaseModel):
    theta: float
    variance_reduction_pct: float
    sample_size_savings_pct: float
    correlation: float
    raw_mean_control: float
    raw_mean_treatment: float
    raw_lift: float
    adjusted_mean_control: float
    adjusted_mean_treatment: float
    adjusted_lift: float
    ci_lower: float
    ci_upper: float
    p_value: float
    is_significant: bool


class DeltaMethodRequest(BaseModel):
    sessions_control: List[int] = Field(..., description="User session counts for control")
    conversions_control: List[int] = Field(..., description="User conversion counts for control")
    sessions_treatment: List[int] = Field(..., description="User session counts for treatment")
    conversions_treatment: List[int] = Field(..., description="User conversion counts for treatment")
    alpha: float = Field(0.05, ge=0.001, le=0.5)


class DeltaMethodResponse(BaseModel):
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
