"""Heterogeneous Treatment Effect (HTE) schemas."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SubgroupMetricInput(BaseModel):
    name: str = Field(..., description="Segment identifier (e.g. 'Mobile (iOS / Android)')")
    sample_size_a: int = Field(..., ge=1, description="Control sample size")
    conversions_a: int = Field(..., ge=0, description="Control conversions")
    sample_size_b: int = Field(..., ge=1, description="Treatment sample size")
    conversions_b: int = Field(..., ge=0, description="Treatment conversions")


class HTEAnalysisRequest(BaseModel):
    dimension: str = Field("Device", description="Segmentation dimension (e.g. Device, User Tier)")
    subgroups: List[SubgroupMetricInput] = Field(..., min_length=2, description="Subgroups data")
    alpha: float = Field(0.05, ge=0.001, le=0.5, description="Significance level")


class HTEResponseItem(BaseModel):
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


class HTEResponse(BaseModel):
    dimension: str
    overall_ate: float
    subgroups: List[HTEResponseItem]
    heterogeneity_p_value: float
    has_heterogeneity: bool
    top_performing_segment: str
    worst_performing_segment: str
