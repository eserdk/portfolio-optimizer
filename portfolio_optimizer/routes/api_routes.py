from typing import List

import fastapi.exceptions
from fastapi import APIRouter, Body, Query

from portfolio_optimizer import controller
from portfolio_optimizer.models import (
    OptimizationResults,
    Optimizer,
    ReturnModel,
    RiskModel,
    Target,
)

api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.post(
    "/v1/optimize",
    response_model=OptimizationResults,
    status_code=200,
    description="Calculate optimal weights for the given tickers (in request body), optimizer, risk model and target.",
    responses={
        200: {"description": "Portfolio allocation and corresponding performance."},
        404: {"description": "No data available for one or more symbols."},
    },
)
def optimize(
    tickers: List[str] = Body(
        ...,
        description="List of tickers from Yahoo Finance",
        min_length=2,
        max_length=20,
        example=["BTC-USD", "ETH-USD", "ADA-USD", "EIMI.L", "SUSW.L", "WSML.L"],
    ),
    optimizer: Optimizer = Query(Optimizer.ef, description="Optimizer to use."),
    risk_model: RiskModel = Query(
        RiskModel.oracle_approximating,
        description="Risk model to use. Doesn't matter if `hrp` is chosen as an optimizer.",
    ),
    return_model: ReturnModel = Query(
        ReturnModel.capm_return,
        description="Return model used to calculate an estimate of future returns. Doesn't matter if `hrp` is chosen as an optimizer.",
    ),
    target: Target = Query(
        Target.max_sharpe,
        description="Optimization problem to solve. Doesn't matter if `hrp` is chosen as an optimizer.",
    ),
) -> OptimizationResults:
    try:
        return controller.optimize(
            tickers=tickers,
            optimizer=optimizer,
            risk_model=risk_model,
            return_model=return_model,
            target=target,
        )
    except ValueError as e:
        raise fastapi.exceptions.HTTPException(404, str(e))
