from __future__ import annotations

from fastapi import APIRouter

from src.api.v1.campaigns import router as campaigns_router
from src.api.v1.simulations import router as simulations_router
from src.api.v1.sse import router as sse_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(campaigns_router)
api_router.include_router(simulations_router)
api_router.include_router(sse_router)
