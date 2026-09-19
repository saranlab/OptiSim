"""
Operations Research Portfolio Roll-Out Optimizer for A/B Testing.

Uses 0-1 Mixed-Integer Linear Programming (MILP) via scipy.optimize.milp
to select the globally optimal set of experiment variants under multi-dimensional
resource constraints (Budget, Latency Overhead, Engineering Effort, and Mutual Exclusion).
"""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from ab_testing_platform.models import CandidateFeature, OptimizationResult


class PortfolioOptimizer:
    """Solves the 0-1 Multi-Dimensional Knapsack Problem for Feature Roll-outs."""

    @staticmethod
    def solve(
        features: List[CandidateFeature],
        max_budget: float,
        max_latency_ms: float,
        max_effort_points: float,
        risk_aversion: float = 0.10,
        enforce_conflicts: bool = True,
        frontier_steps: int = 15,
    ) -> OptimizationResult:
        """
        Solve 0-1 Knapsack MILP to maximize risk-adjusted total incremental value.

        maximize   sum_i (v_i - risk_aversion * r_i * v_i) * x_i
        subject to sum_i c_i * x_i <= max_budget
                   sum_i l_i * x_i <= max_latency_ms
                   sum_i e_i * x_i <= max_effort_points
                   sum_{j in conflict_k} x_j <= 1
                   x_i in {0, 1}
        """
        if not features:
            return OptimizationResult(
                selected_features=[],
                rejected_features=[],
                total_value=0.0,
                total_cost=0.0,
                total_latency_ms=0.0,
                total_effort_points=0.0,
                budget_utilization_pct=0.0,
                latency_utilization_pct=0.0,
                effort_utilization_pct=0.0,
                is_feasible=True,
                status_message="No features provided for optimization.",
                efficient_frontier=[],
            )

        n = len(features)
        v = np.array([float(f.expected_value) for f in features], dtype=float)
        c = np.array([float(f.cost) for f in features], dtype=float)
        l = np.array([float(f.latency_ms) for f in features], dtype=float)
        e = np.array([float(f.effort_points) for f in features], dtype=float)
        r = np.array([float(np.clip(f.risk_score, 0.0, 1.0)) for f in features], dtype=float)

        # Objective: scipy.optimize.milp minimizes c^T x, so negate for maximization
        risk_adjusted_val = v - (float(risk_aversion) * r * v)
        c_obj = -risk_adjusted_val

        # 0-1 integrality and bounds
        integrality = np.ones(n, dtype=int)
        bounds = Bounds(lb=np.zeros(n), ub=np.ones(n))

        # Build Constraint Matrix
        constraint_rows = []
        ub_list = []

        # 1. Budget constraint
        constraint_rows.append(c)
        ub_list.append(max(0.0, float(max_budget)))

        # 2. Latency overhead constraint
        constraint_rows.append(l)
        ub_list.append(max(0.0, float(max_latency_ms)))

        # 3. Engineering effort constraint
        constraint_rows.append(e)
        ub_list.append(max(0.0, float(max_effort_points)))

        # 4. Mutually exclusive conflict groups
        if enforce_conflicts:
            groups: Dict[str, List[int]] = {}
            for idx, f in enumerate(features):
                if f.conflict_group:
                    groups.setdefault(f.conflict_group, []).append(idx)

            for g_name, indices in groups.items():
                if len(indices) > 1:
                    row = np.zeros(n, dtype=float)
                    for i_idx in indices:
                        row[i_idx] = 1.0
                    constraint_rows.append(row)
                    ub_list.append(1.0)

        A_mat = np.array(constraint_rows, dtype=float)
        b_u = np.array(ub_list, dtype=float)
        b_l = np.zeros(len(b_u), dtype=float)

        linear_constraints = LinearConstraint(A_mat, b_l, b_u)

        # Run MILP solver (HiGHS backend)
        res = milp(
            c=c_obj,
            integrality=integrality,
            constraints=linear_constraints,
            bounds=bounds,
        )

        if not res.success or res.x is None:
            return OptimizationResult(
                selected_features=[],
                rejected_features=features.copy(),
                total_value=0.0,
                total_cost=0.0,
                total_latency_ms=0.0,
                total_effort_points=0.0,
                budget_utilization_pct=0.0,
                latency_utilization_pct=0.0,
                effort_utilization_pct=0.0,
                is_feasible=False,
                status_message=f"Solver status: {res.status}. Infeasible under current resource constraints.",
                efficient_frontier=[],
            )

        x_sol = np.round(res.x).astype(int)
        selected = [features[i] for i in range(n) if x_sol[i] == 1]
        rejected = [features[i] for i in range(n) if x_sol[i] == 0]

        tot_val = float(sum(f.expected_value for f in selected))
        tot_cost = float(sum(f.cost for f in selected))
        tot_lat = float(sum(f.latency_ms for f in selected))
        tot_eff = float(sum(f.effort_points for f in selected))

        b_util = (tot_cost / max_budget * 100.0) if max_budget > 0 else 0.0
        l_util = (tot_lat / max_latency_ms * 100.0) if max_latency_ms > 0 else 0.0
        e_util = (tot_eff / max_effort_points * 100.0) if max_effort_points > 0 else 0.0

        # Calculate Efficient Frontier (Budget vs Unlocked Value)
        efficient_frontier: List[Dict[str, float]] = []
        if frontier_steps > 1 and max_budget > 0:
            b_steps = np.linspace(max_budget * 0.20, max_budget * 1.50, frontier_steps)
            for b_eval in b_steps:
                ub_eval = ub_list.copy()
                ub_eval[0] = float(b_eval)
                lin_eval = LinearConstraint(A_mat, b_l, np.array(ub_eval, dtype=float))
                res_eval = milp(c=c_obj, integrality=integrality, constraints=lin_eval, bounds=bounds)
                if res_eval.success and res_eval.x is not None:
                    x_eval = np.round(res_eval.x).astype(int)
                    val_eval = float(sum(features[i].expected_value for i in range(n) if x_eval[i] == 1))
                    cnt_eval = int(np.sum(x_eval))
                    efficient_frontier.append({
                        "budget": float(b_eval),
                        "value": val_eval,
                        "num_selected": cnt_eval,
                    })

        return OptimizationResult(
            selected_features=selected,
            rejected_features=rejected,
            total_value=tot_val,
            total_cost=tot_cost,
            total_latency_ms=tot_lat,
            total_effort_points=tot_eff,
            budget_utilization_pct=float(np.clip(b_util, 0.0, 100.0)),
            latency_utilization_pct=float(np.clip(l_util, 0.0, 100.0)),
            effort_utilization_pct=float(np.clip(e_util, 0.0, 100.0)),
            is_feasible=True,
            status_message="Global optimal portfolio identified.",
            efficient_frontier=efficient_frontier,
        )

    @staticmethod
    def get_default_candidate_pool(current_experiment_value: float = 45000.0, current_experiment_cost: float = 1200.0) -> List[CandidateFeature]:
        """Generate realistic production candidate experiments for portfolio evaluation."""
        return [
            CandidateFeature(
                feature_id="EXP_ACTIVE",
                name="Current Active Experiment (Variant B)",
                category="Primary Experiment",
                expected_value=max(1000.0, float(current_experiment_value)),
                cost=max(100.0, float(current_experiment_cost)),
                latency_ms=8.0,
                effort_points=5.0,
                risk_score=0.10,
                conflict_group=None,
            ),
            CandidateFeature(
                feature_id="EXP_01",
                name="1-Click Express Checkout Widget",
                category="Checkout",
                expected_value=85000.0,
                cost=7500.0,
                latency_ms=14.0,
                effort_points=13.0,
                risk_score=0.25,
                conflict_group="checkout_redesign",
            ),
            CandidateFeature(
                feature_id="EXP_02",
                name="Multi-Step Progressive Checkout Accordion",
                category="Checkout",
                expected_value=55000.0,
                cost=4000.0,
                latency_ms=6.0,
                effort_points=8.0,
                risk_score=0.15,
                conflict_group="checkout_redesign",
            ),
            CandidateFeature(
                feature_id="EXP_03",
                name="Deep Learning Real-Time Recommendation Bar",
                category="Search & Discovery",
                expected_value=120000.0,
                cost=12000.0,
                latency_ms=28.0,
                effort_points=21.0,
                risk_score=0.35,
                conflict_group=None,
            ),
            CandidateFeature(
                feature_id="EXP_04",
                name="Address Autocomplete & Instant Geocoding API",
                category="Checkout",
                expected_value=32000.0,
                cost=2500.0,
                latency_ms=4.0,
                effort_points=5.0,
                risk_score=0.08,
                conflict_group=None,
            ),
            CandidateFeature(
                feature_id="EXP_05",
                name="Dynamic Free Shipping Threshold Progress Meter",
                category="Marketing & Cart",
                expected_value=48000.0,
                cost=3000.0,
                latency_ms=3.0,
                effort_points=5.0,
                risk_score=0.12,
                conflict_group=None,
            ),
            CandidateFeature(
                feature_id="EXP_06",
                name="High-Contrast Dark Mode Color Scheme",
                category="UI / Accessibility",
                expected_value=15000.0,
                cost=1800.0,
                latency_ms=1.0,
                effort_points=3.0,
                risk_score=0.05,
                conflict_group=None,
            ),
            CandidateFeature(
                feature_id="EXP_07",
                name="Client-Side Image WebP Compression & Lazy Loading",
                category="Infrastructure",
                expected_value=28000.0,
                cost=2200.0,
                latency_ms=-18.0,  # Negative latency = improves speed!
                effort_points=5.0,
                risk_score=0.05,
                conflict_group=None,
            ),
        ]
