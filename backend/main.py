"""OptiSim Enterprise Causal Inference & Operations Research REST API."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import (
    bandit,
    experiment,
    guardrails,
    hte,
    memo,
    portfolio,
)

app = FastAPI(
    title="OptiSim Enterprise API",
    description="Algorithmic Causal Inference, Multi-Metric Guardrails, and Operations Research MILP Optimization API.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Next.js frontend and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular Routers
app.include_router(experiment.router)
app.include_router(hte.router)
app.include_router(guardrails.router)
app.include_router(portfolio.router)
app.include_router(bandit.router)
app.include_router(memo.router)


@app.get("/health", tags=["System"])
def health_check():
    """System liveness and readiness probe."""
    return {
        "status": "healthy",
        "service": "OptiSim Enterprise Engine",
        "version": "2.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
