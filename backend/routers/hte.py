"""Router for Heterogeneous Treatment Effects (HTE) & Subgroup Slicing."""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException

from ab_testing_platform.hte import HTEEngine
from backend.schemas.hte import (
    HTEAnalysisRequest,
    HTEResponse,
    HTEResponseItem,
    SubgroupMetricInput,
)

router = APIRouter(prefix="/api/v1/experiment", tags=["Heterogeneous Treatment Effects"])


@router.post("/hte", response_model=HTEResponse)
def analyze_hte(payload: HTEAnalysisRequest) -> HTEResponse:
    """Analyze Conditional Average Treatment Effects (CATE) across customer subgroups."""
    try:
        subgroup_dicts = [s.model_dump() for s in payload.subgroups]
        res = HTEEngine.analyze_subgroups(
            dimension=payload.dimension,
            subgroup_data=subgroup_dicts,
            alpha=payload.alpha,
        )

        subgroup_items = [
            HTEResponseItem(
                segment_name=item.segment_name,
                sample_size_a=item.sample_size_a,
                conversions_a=item.conversions_a,
                cvr_a=item.cvr_a,
                sample_size_b=item.sample_size_b,
                conversions_b=item.conversions_b,
                cvr_b=item.cvr_b,
                absolute_lift=item.absolute_lift,
                relative_lift=item.relative_lift,
                se_difference=item.se_difference,
                z_score=item.z_score,
                p_value=item.p_value,
                ci_lower=item.ci_lower,
                ci_upper=item.ci_upper,
                is_significant=item.is_significant,
                interaction_p_value=item.interaction_p_value,
                interaction_significant=item.interaction_significant,
            )
            for item in res.subgroups
        ]

        return HTEResponse(
            dimension=res.dimension,
            overall_ate=res.overall_ate,
            subgroups=subgroup_items,
            heterogeneity_p_value=res.heterogeneity_p_value,
            has_heterogeneity=res.has_heterogeneity,
            top_performing_segment=res.top_performing_segment,
            worst_performing_segment=res.worst_performing_segment,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/hte/defaults", response_model=List[SubgroupMetricInput])
def get_default_subgroups() -> List[SubgroupMetricInput]:
    """Retrieve preconfigured production device and user tier subgroup metrics."""
    defaults = HTEEngine.get_default_device_subgroups()
    return [SubgroupMetricInput(**d) for d in defaults]
