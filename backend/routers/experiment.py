"""Router for sequential testing, CUPED variance reduction, and Delta Method."""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException

from ab_testing_platform.cuped import CUPEDEngine
from ab_testing_platform.delta_method import DeltaMethodEngine
from ab_testing_platform.math_utils import safe_divide
from ab_testing_platform.sequential import SequentialTest
from backend.schemas.experiment import (
    CUPEDRequest,
    CUPEDResponse,
    DeltaMethodRequest,
    DeltaMethodResponse,
    SequentialAnalysisResponse,
    SequentialStreamRequest,
)

router = APIRouter(prefix="/api/v1/experiment", tags=["Experimentation"])


@router.post("/sequential", response_model=SequentialAnalysisResponse)
def analyze_sequential_stream(payload: SequentialStreamRequest) -> SequentialAnalysisResponse:
    """Evaluate continuous anytime-valid confidence sequences on an incoming conversion stream."""
    try:
        c_arr = np.array(payload.control_conversions, dtype=int)
        t_arr = np.array(payload.treatment_conversions, dtype=int)
        n = min(len(c_arr), len(t_arr))
        if n <= 0:
            raise ValueError("Stream cannot be empty.")

        cum_c = np.cumsum(c_arr[:n])
        cum_t = np.cumsum(t_arr[:n])

        sample_sizes = []
        tau_estimates = []
        ci_lowers = []
        ci_uppers = []
        stopped_early = False
        stopping_sample = None
        final_decision = "CONTINUE_SAMPLING"

        step = max(1, n // 50)
        eval_indices = list(range(step, n + 1, step))
        if eval_indices[-1] != n:
            eval_indices.append(n)

        for i in eval_indices:
            conv_a = int(cum_c[i - 1])
            conv_b = int(cum_t[i - 1])
            res = SequentialTest.confidence_sequence(
                conversions_a=conv_a,
                sample_size_a=i,
                conversions_b=conv_b,
                sample_size_b=i,
                alpha=payload.alpha,
                planned_sample_size=n,
            )
            sample_sizes.append(i)
            tau_estimates.append(float(res.absolute_lift))
            ci_lowers.append(float(res.ci_lower))
            ci_uppers.append(float(res.ci_upper))

            if res.is_conclusive and not stopped_early:
                stopped_early = True
                stopping_sample = i
                final_decision = "DECISION_REACHED"

        last_res = SequentialTest.confidence_sequence(
            conversions_a=int(cum_c[-1]),
            sample_size_a=n,
            conversions_b=int(cum_t[-1]),
            sample_size_b=n,
            alpha=payload.alpha,
            planned_sample_size=n,
        )

        ctrl_rate = safe_divide(int(cum_c[-1]), n)
        rel_lift = (last_res.absolute_lift / ctrl_rate * 100.0) if ctrl_rate > 0 else 0.0

        return SequentialAnalysisResponse(
            sample_sizes=sample_sizes,
            tau_estimates=tau_estimates,
            ci_lowers=ci_lowers,
            ci_uppers=ci_uppers,
            stopped_early=stopped_early,
            stopping_sample=stopping_sample,
            decision=final_decision,
            relative_lift_pct=float(rel_lift),
            p_value_anytime=float(last_res.always_valid_p_value),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/cuped", response_model=CUPEDResponse)
def apply_cuped(payload: CUPEDRequest) -> CUPEDResponse:
    """Apply Controlled-experiment using Pre-Experiment Data (CUPED) variance reduction."""
    try:
        y_ctrl = np.array(payload.y_control, dtype=float)
        y_treat = np.array(payload.y_treatment, dtype=float)
        x_ctrl = np.array(payload.x_control, dtype=float)
        x_treat = np.array(payload.x_treatment, dtype=float)

        res = CUPEDEngine.compute(
            y_control=y_ctrl,
            y_treatment=y_treat,
            x_control=x_ctrl,
            x_treatment=x_treat,
        )
        return CUPEDResponse(
            theta=res.theta,
            variance_reduction_pct=res.variance_reduction_pct,
            sample_size_savings_pct=res.sample_size_savings_pct,
            correlation=res.correlation,
            raw_mean_control=res.raw_mean_control,
            raw_mean_treatment=res.raw_mean_treatment,
            raw_lift=res.raw_lift,
            adjusted_mean_control=res.adjusted_mean_control,
            adjusted_mean_treatment=res.adjusted_mean_treatment,
            adjusted_lift=res.adjusted_lift,
            ci_lower=res.ci_lower,
            ci_upper=res.ci_upper,
            p_value=res.p_value,
            is_significant=res.is_significant,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/delta-method", response_model=DeltaMethodResponse)
def analyze_delta_method(payload: DeltaMethodRequest) -> DeltaMethodResponse:
    """Analyze ratio metrics with clustered sessions via asymptotic Taylor expansion (Delta Method)."""
    try:
        s_c = np.array(payload.sessions_control, dtype=int)
        c_c = np.array(payload.conversions_control, dtype=int)
        s_t = np.array(payload.sessions_treatment, dtype=int)
        c_t = np.array(payload.conversions_treatment, dtype=int)

        res = DeltaMethodEngine.compute(
            control_numerators=c_c,
            control_denominators=s_c,
            treatment_numerators=c_t,
            treatment_denominators=s_t,
            alpha=payload.alpha,
        )
        return DeltaMethodResponse(
            ratio_control=res.ratio_control,
            ratio_treatment=res.ratio_treatment,
            absolute_lift=res.absolute_lift,
            relative_lift=res.relative_lift,
            se_control=res.se_control,
            se_treatment=res.se_treatment,
            se_difference=res.se_difference,
            z_statistic=res.z_statistic,
            p_value=res.p_value,
            ci_lower=res.ci_lower,
            ci_upper=res.ci_upper,
            is_significant=res.is_significant,
            num_clusters_control=res.num_clusters_control,
            num_clusters_treatment=res.num_clusters_treatment,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
