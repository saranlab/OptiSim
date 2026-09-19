"""Router for Multi-Metric Guardrails and Benjamini-Hochberg FDR Control."""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException

from ab_testing_platform.guardrails import GuardrailEngine
from backend.schemas.guardrails import (
    GuardrailAuditRecord,
    GuardrailAuditRequest,
    GuardrailAuditResponse,
    GuardrailMetricInput,
)

router = APIRouter(prefix="/api/v1/experiment", tags=["Guardrails & FDR Control"])


@router.post("/guardrails", response_model=GuardrailAuditResponse)
def audit_guardrails(payload: GuardrailAuditRequest) -> GuardrailAuditResponse:
    """Audit secondary operational guardrails with False Discovery Rate (FDR) adjustment."""
    try:
        metrics_data = [g.model_dump() for g in payload.guardrails]
        res = GuardrailEngine.audit(metrics_data, fdr_alpha=payload.fdr_alpha)

        records = [
            GuardrailAuditRecord(
                metric_name=m.metric_name,
                control_value=m.control_value,
                treatment_value=m.treatment_value,
                delta=m.delta,
                relative_change=m.relative_change,
                raw_p_value=m.raw_p_value,
                adjusted_p_value=m.adjusted_p_value,
                direction_favorable=m.direction_favorable,
                threshold_pct=m.threshold_pct,
                is_violated=m.is_violated,
                status=m.status,
            )
            for m in res.metrics
        ]

        return GuardrailAuditResponse(
            metrics=records,
            fdr_alpha=res.fdr_alpha,
            has_critical_violations=res.has_critical_violations,
            summary_verdict=res.summary_verdict,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/guardrails/defaults", response_model=List[GuardrailMetricInput])
def get_default_guardrails() -> List[GuardrailMetricInput]:
    """Retrieve preconfigured production guardrails (Latency, Errors, Abandonment, Churn)."""
    defaults = GuardrailEngine.get_default_guardrails()
    return [GuardrailMetricInput(**d) for d in defaults]
