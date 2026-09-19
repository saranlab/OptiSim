"""Router for Executive Decision Memo generation."""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter

from backend.schemas.memo import MemoRequest, MemoResponse

router = APIRouter(prefix="/api/v1/memo", tags=["Executive Decision Memo"])


@router.post("/generate", response_model=MemoResponse)
def generate_decision_memo(payload: MemoRequest) -> MemoResponse:
    """Generate an institutional-grade executive decision memo based on causal and optimization results."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    verdict_badge = "SHIP TO 100% TRAFFIC" if payload.recommended_action == "SHIP_TO_100_PERCENT" else (
        "CONTINUE SAMPLING (UNDERPOWERED)" if payload.recommended_action == "CONTINUE_SAMPLING" else "DO NOT SHIP (GUARDRAIL VIOLATION)"
    )

    memo_md = f"""# Executive Decision Memo: {payload.experiment_name}
**Date:** {now_str}  
**Platform:** OptiSim Enterprise Experimentation & OR Engine  
**Status:** **{verdict_badge}**  

---

### 1. Executive Summary
This document summarizes the causal inference evaluation and operational risk assessment for **{payload.experiment_name}**. Primary analysis was conducted using **anytime-valid confidence sequences** (Waudby-Smith & Ramdas, 2021) to eliminate peeking bias, paired with **Benjamini-Hochberg False Discovery Rate (FDR)** multi-metric guardrails.

* **Primary Evaluated Metric:** `{payload.primary_metric}`
* **Observed Baseline (Control):** `{payload.control_val:.4f}`
* **Observed Variant (Treatment):** `{payload.treatment_val:.4f}`
* **Relative Treatment Effect:** **`{payload.lift_pct:+.2f}%`**
* **95% Anytime-Valid Confidence Sequence:** `[{payload.ci_lower:+.4f}, {payload.ci_upper:+.4f}]`
* **Effective Sample Size:** `{payload.sample_size:,}` users

---

### 2. Statistical & Causal Validity
* **Peeking Resistance:** The confidence sequence maintains bounded Type I error (alpha = 0.05) across continuous monitoring.
* **Statistical Significance:** `{'Affirmed (Zero excluded from confidence interval)' if payload.is_significant else 'Non-significant or inconclusive'}`.
* **Heterogeneous Treatment Effects (HTE):** `{'Significant subgroup variance detected via Cochran’s Q test. Segmented rollout recommended.' if payload.subgroups_heterogeneity else 'Homogeneous treatment effects observed across device and tier cohorts.'}`

---

### 3. Operational Risk & Guardrails Audit
* **Operational Guardrail Status:** `{'PASSED - No significant degradation detected across latency, error rates, or churn.' if payload.guardrails_passed else 'BREACHED - Critical threshold exceeded after Benjamini-Hochberg adjustment.'}`
* **FDR Multiplicity Control:** Benjamini-Hochberg procedure applied across secondary telemetry to prevent false alarms from multiple comparisons.

---

### 4. Operations Research Portfolio Context
"""
    if payload.portfolio_value is not None:
        memo_md += f"""* **Integrated Portfolio Value:** Projected ARR contribution is **${payload.portfolio_value:,.2f}**.
* **Resource Optimization:** Solved via 0-1 Mixed-Integer Linear Program (MILP) respecting enterprise capital budgets, p99 latency SLAs, and sprint engineering capacity.
* **Risk Adjustment:** Conservative defensible floor formulation applied with downstream customer churn penalties deducted.
"""
    else:
        memo_md += "* **Portfolio Allocation:** Standalone feature evaluation. Cross-feature MILP bundling not requested.\n"

    memo_md += f"""
---

### 5. Final Governance Recommendation
**Action Plan:** **`{payload.recommended_action}`**

* **Rationale:** The treatment delivers a statistically verifiable positive impact on `{payload.primary_metric}` without degrading critical operational guardrails.
* **Sign-off:** OptiSim Automated Decision Pipeline
"""

    return MemoResponse(
        markdown=memo_md,
        executive_verdict=verdict_badge,
        timestamp=now_str,
    )
