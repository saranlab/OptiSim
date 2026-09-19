"""
Multi-Metric Guardrails & False Discovery Rate (FDR) Engine.

Evaluates secondary business and operational guardrails (latency, errors, churn)
using the Benjamini-Hochberg (BH) step-up procedure to strictly control the
False Discovery Rate across simultaneous hypothesis tests.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np

from ab_testing_platform.models import GuardrailAuditResult, GuardrailMetric


class GuardrailEngine:
    """Enterprise guardrail auditing with Benjamini-Hochberg FDR correction."""

    @staticmethod
    def audit(
        metrics_data: List[Dict[str, any]],
        fdr_alpha: float = 0.05,
    ) -> GuardrailAuditResult:
        """
        Audit a collection of guardrail metrics using the Benjamini-Hochberg procedure.

        Parameters
        ----------
        metrics_data: List[Dict]
            List of dicts, each with keys:
            - 'metric_name': str
            - 'control_value': float
            - 'treatment_value': float
            - 'raw_p_value': float
            - 'direction_favorable': str ('lower' or 'higher')
            - 'threshold_pct': float (e.g. 5.0 for 5% max allowable degradation)
        fdr_alpha: float
            Target False Discovery Rate (default 0.05).
        """
        if not metrics_data:
            raise ValueError("metrics_data cannot be empty")

        m = len(metrics_data)

        # 1. Sort metrics by raw p-value ascending for Benjamini-Hochberg
        indexed_metrics = list(enumerate(metrics_data))
        indexed_metrics.sort(key=lambda x: float(x[1]["raw_p_value"]))

        # 2. Compute Benjamini-Hochberg adjusted p-values (step-up)
        # P_adj(i) = min_{j >= i} ( (m / j) * P(j) )
        raw_p_values = [float(item[1]["raw_p_value"]) for item in indexed_metrics]
        adjusted_p_values = [0.0] * m

        running_min = 1.0
        for i in reversed(range(m)):
            rank = i + 1
            adj = (m / rank) * raw_p_values[i]
            running_min = min(running_min, adj)
            adjusted_p_values[i] = min(1.0, float(running_min))

        # 3. Classify each metric
        audited_metrics: List[GuardrailMetric] = [None] * m
        has_critical = False

        for original_idx, (orig_pos, item) in enumerate(indexed_metrics):
            name = str(item["metric_name"])
            ctrl = float(item["control_value"])
            treat = float(item["treatment_value"])
            raw_p = float(item["raw_p_value"])
            adj_p = float(adjusted_p_values[original_idx])
            direction = str(item.get("direction_favorable", "lower")).lower()
            threshold_pct = float(item.get("threshold_pct", 5.0))

            delta = treat - ctrl
            rel_change = (delta / ctrl * 100.0) if ctrl != 0 else 0.0

            # Determine adverse degradation
            if direction == "lower":
                # Increase is bad (e.g. latency, errors, churn)
                adverse_degradation_pct = rel_change
            else:
                # Decrease is bad (e.g. RPM, satisfaction)
                adverse_degradation_pct = -rel_change

            # Critical violation: statistically significant under FDR AND exceeds threshold
            is_significant_under_fdr = adj_p < fdr_alpha
            exceeds_threshold = adverse_degradation_pct > threshold_pct

            if exceeds_threshold and is_significant_under_fdr:
                status = "FAIL"
                is_violated = True
                has_critical = True
            elif exceeds_threshold and not is_significant_under_fdr:
                status = "WARN"  # trending bad, but not statistically significant under FDR
                is_violated = False
            else:
                status = "PASS"
                is_violated = False

            metric_obj = GuardrailMetric(
                metric_name=name,
                control_value=ctrl,
                treatment_value=treat,
                delta=delta,
                relative_change=rel_change,
                raw_p_value=raw_p,
                adjusted_p_value=adj_p,
                direction_favorable=direction,
                threshold_pct=threshold_pct,
                is_violated=is_violated,
                status=status,
            )
            audited_metrics[orig_pos] = metric_obj

        verdict = (
            "CRITICAL VIOLATION: Secondary guardrails severely degraded"
            if has_critical
            else "ALL GUARDRAILS PASSED: No statistically significant degradation detected"
        )

        return GuardrailAuditResult(
            metrics=audited_metrics,
            fdr_alpha=fdr_alpha,
            has_critical_violations=has_critical,
            summary_verdict=verdict,
        )

    @staticmethod
    def get_default_guardrails(active_lift: float = 0.12) -> List[Dict[str, any]]:
        """Default enterprise guardrails with realistic p-values and thresholds."""
        return [
            {
                "metric_name": "API p95 Latency (ms)",
                "control_value": 42.0,
                "treatment_value": 44.5,
                "raw_p_value": 0.082,
                "direction_favorable": "lower",
                "threshold_pct": 10.0,
            },
            {
                "metric_name": "Checkout Error Rate (%)",
                "control_value": 0.45,
                "treatment_value": 0.46,
                "raw_p_value": 0.450,
                "direction_favorable": "lower",
                "threshold_pct": 15.0,
            },
            {
                "metric_name": "Cart Abandonment Rate (%)",
                "control_value": 68.2,
                "treatment_value": 66.8,
                "raw_p_value": 0.034,
                "direction_favorable": "lower",
                "threshold_pct": 5.0,
            },
            {
                "metric_name": "30-Day Customer Churn (%)",
                "control_value": 4.10,
                "treatment_value": 4.15,
                "raw_p_value": 0.620,
                "direction_favorable": "lower",
                "threshold_pct": 8.0,
            },
        ]
