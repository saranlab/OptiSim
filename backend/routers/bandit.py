"""Router for Multi-Armed Bandits (Thompson Sampling) and Contextual Bandits (LinUCB)."""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException

from ab_testing_platform.bandits import LinUCBBandit, ThompsonSamplingBandit
from backend.schemas.bandit import (
    BanditRoundRecord,
    LinUCBSimRequest,
    LinUCBSimResponse,
    ThompsonSimRequest,
    ThompsonSimResponse,
)

router = APIRouter(prefix="/api/v1/bandit", tags=["Multi-Armed Bandits & Personalization"])


@router.post("/thompson", response_model=ThompsonSimResponse)
def simulate_thompson_sampling(payload: ThompsonSimRequest) -> ThompsonSimResponse:
    """Run dynamic traffic allocation simulation with Thompson Sampling and delayed feedback."""
    try:
        sim = ThompsonSamplingBandit(
            true_conversion_rates=payload.true_conversion_rates,
            prior_alpha=payload.prior_alpha,
            prior_beta=payload.prior_beta,
            random_seed=payload.random_seed,
        )
        summary = sim.run(n_rounds=payload.n_rounds, delay_rounds=payload.delay_rounds)

        # Sample at most 100 history items to keep payload lean
        stride = max(1, len(summary.history) // 100)
        history_sample = [
            BanditRoundRecord(
                round_index=r.round_index,
                chosen_arm=r.chosen_arm,
                reward=r.reward,
                posterior_alpha=r.posterior_alpha,
                posterior_beta=r.posterior_beta,
            )
            for r in summary.history[::stride]
        ]

        return ThompsonSimResponse(
            pulls=summary.pulls,
            rewards=summary.rewards,
            conversion_rates=summary.conversion_rates,
            allocation_rates=summary.allocation_rates,
            cumulative_reward=summary.cumulative_reward,
            regret=summary.regret,
            history_sample=history_sample,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/linucb", response_model=LinUCBSimResponse)
def simulate_linucb(payload: LinUCBSimRequest) -> LinUCBSimResponse:
    """Simulate LinUCB contextual bandit with synthetic user feature vectors."""
    try:
        bandit = LinUCBBandit(
            arm_names=payload.arm_names,
            context_dim=payload.context_dim,
            alpha=payload.alpha,
            random_seed=payload.random_seed,
        )

        rng = np.random.default_rng(payload.random_seed)
        # Synthetic arm preference weights
        true_theta = {
            arm: rng.standard_normal(payload.context_dim)
            for arm in payload.arm_names
        }

        total_reward = 0
        arm_pulls = {arm: 0 for arm in payload.arm_names}
        arm_rewards = {arm: 0 for arm in payload.arm_names}

        for _ in range(payload.n_rounds):
            # Generate random synthetic user context vector
            context = rng.standard_normal(payload.context_dim)
            context = context / (np.linalg.norm(context) + 1e-9)

            chosen_arm = bandit.select_arm(context)
            arm_pulls[chosen_arm] += 1

            # Synthetic conversion probability via logistic link
            prob = 1.0 / (1.0 + np.exp(-np.dot(true_theta[chosen_arm], context)))
            reward = int(rng.binomial(1, np.clip(prob, 0.05, 0.95)))

            bandit.update(chosen_arm, context, reward)
            total_reward += reward
            arm_rewards[chosen_arm] += reward

        ctr = total_reward / payload.n_rounds if payload.n_rounds > 0 else 0.0

        return LinUCBSimResponse(
            arm_pulls=arm_pulls,
            arm_rewards=arm_rewards,
            total_reward=total_reward,
            ctr=ctr,
            message=f"LinUCB personalized routing converged over {payload.n_rounds} rounds.",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
