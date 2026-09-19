"""Router for Operations Research: Multi-Constraint Knapsack & Robust Optimization."""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException

from ab_testing_platform.models import CandidateFeature
from ab_testing_platform.optimizer import PortfolioOptimizer
from backend.schemas.portfolio import (
    CandidateFeatureInput,
    EfficientFrontierPoint,
    PortfolioOptimizeRequest,
    PortfolioOptimizeResponse,
    SelectedFeatureResponse,
)

router = APIRouter(prefix="/api/v1/portfolio", tags=["Operations Research & Knapsack Optimization"])


@router.post("/optimize", response_model=PortfolioOptimizeResponse)
def optimize_portfolio(payload: PortfolioOptimizeRequest) -> PortfolioOptimizeResponse:
    """Solve multi-constraint 0-1 Knapsack with robust defensible floor and churn penalties."""
    try:
        features = [
            CandidateFeature(
                feature_id=f.feature_id,
                name=f.name,
                category=f.category,
                expected_value=f.expected_value,
                cost=f.cost,
                latency_ms=f.latency_ms,
                effort_points=f.effort_points,
                defensible_floor_value=f.defensible_floor_value,
                downstream_churn_risk=f.downstream_churn_risk,
                conflict_group=f.mutual_exclusive_group,
                is_mandatory=f.is_mandatory,
            )
            for f in payload.features
        ]

        res = PortfolioOptimizer.solve(
            features=features,
            max_budget=payload.max_budget,
            max_latency_ms=payload.max_latency_ms,
            max_effort_points=payload.max_effort_points,
            robust_mode=payload.robust_mode,
            churn_penalty_weight=payload.churn_penalty_weight,
            frontier_steps=payload.frontier_steps,
        )

        selected = [
            SelectedFeatureResponse(
                feature_id=f.feature_id,
                name=f.name,
                category=f.category,
                expected_value=f.expected_value,
                defensible_floor_value=f.defensible_floor_value,
                cost=f.cost,
                latency_ms=f.latency_ms,
                effort_points=f.effort_points,
                downstream_churn_risk=f.downstream_churn_risk,
                is_mandatory=getattr(f, "is_mandatory", False),
                mutual_exclusive_group=getattr(f, "conflict_group", None),
            )
            for f in res.selected_features
        ]

        rejected = [
            SelectedFeatureResponse(
                feature_id=f.feature_id,
                name=f.name,
                category=f.category,
                expected_value=f.expected_value,
                defensible_floor_value=f.defensible_floor_value,
                cost=f.cost,
                latency_ms=f.latency_ms,
                effort_points=f.effort_points,
                downstream_churn_risk=f.downstream_churn_risk,
                is_mandatory=getattr(f, "is_mandatory", False),
                mutual_exclusive_group=getattr(f, "conflict_group", None),
            )
            for f in res.rejected_features
        ]

        frontier = [
            EfficientFrontierPoint(
                budget=float(pt["budget"]),
                value=float(pt["value"]),
                num_selected=int(pt["num_selected"]),
            )
            for pt in res.efficient_frontier
        ]

        return PortfolioOptimizeResponse(
            selected_features=selected,
            rejected_features=rejected,
            total_value=res.total_value,
            total_cost=res.total_cost,
            total_latency_ms=res.total_latency_ms,
            total_effort_points=res.total_effort_points,
            budget_utilization_pct=res.budget_utilization_pct,
            latency_utilization_pct=res.latency_utilization_pct,
            effort_utilization_pct=res.effort_utilization_pct,
            is_feasible=res.is_feasible,
            status_message=res.status_message,
            efficient_frontier=frontier,
            is_robust=res.is_robust,
            churn_penalty_deducted=res.churn_penalty_deducted,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/candidates/default", response_model=List[CandidateFeatureInput])
def get_default_candidates(
    active_val: float = 45000.0,
    active_cost: float = 1200.0,
) -> List[CandidateFeatureInput]:
    """Retrieve preconfigured enterprise candidate feature pool."""
    pool = PortfolioOptimizer.get_default_candidate_pool(
        current_experiment_value=active_val,
        current_experiment_cost=active_cost,
    )
    return [
        CandidateFeatureInput(
            feature_id=f.feature_id,
            name=f.name,
            category=f.category,
            expected_value=f.expected_value,
            cost=f.cost,
            latency_ms=f.latency_ms,
            effort_points=f.effort_points,
            defensible_floor_value=f.defensible_floor_value,
            downstream_churn_risk=f.downstream_churn_risk,
            is_mandatory=getattr(f, "is_mandatory", False),
            mutual_exclusive_group=getattr(f, "conflict_group", None),
        )
        for f in pool
    ]
