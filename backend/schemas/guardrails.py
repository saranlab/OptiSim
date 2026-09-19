"""Guardrails and False Discovery Rate (FDR) schemas."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


class GuardrailMetricInput(BaseModel):
    metric_name: str = Field(..., description="Guardrail metric name (e.g. 'API p95 Latency (ms)')")
    control_value: float = Field(..., description="Baseline control mean/rate")
    treatment_value: float = Field(..., description="Treatment mean/rate")
    raw_p_value: float = Field(..., ge=0.0, le=1.0, description="Unadjusted p-value for the metric test")
    direction_favorable: str = Field("lower", description="'lower' if lower is better, 'higher' if higher is better")
    threshold_pct: float = Field(5.0, gt=0.0, description="Maximum tolerable adverse deviation (%)")


class GuardrailAuditRequest(BaseModel):
    guardrails: List[GuardrailMetricInput] = Field(..., min_length=1, description="List of guardrail specifications")
    fdr_alpha: float = Field(0.05, ge=0.001, le=0.5, description="Target FDR threshold for Benjamini-Hochberg")


class GuardrailAuditRecord(BaseModel):
    metric_name: str
    control_value: float
    treatment_value: float
    delta: float
    relative_change: float
    raw_p_value: float
    adjusted_p_value: float
    direction_favorable: str
    threshold_pct: float
    is_violated: bool
    status: str


class GuardrailAuditResponse(BaseModel):
    metrics: List[GuardrailAuditRecord]
    fdr_alpha: float
    has_critical_violations: bool
    summary_verdict: str
