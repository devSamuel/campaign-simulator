from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.campaign.application.commands.run_simulation import RunSimulationCommand, RunSimulationHandler
from src.campaign.application.dtos.simulation_dto import RunSimulationResponse, SimulationResultDTO, SimulationStepDTO
from src.api.dependencies import get_run_simulation_handler
from src.shared.infrastructure.redis_client import get_redis_client

router = APIRouter(prefix="/campaigns", tags=["simulations"])


@router.post("/{campaign_id}/simulate", response_model=RunSimulationResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_simulation(
    campaign_id: uuid.UUID,
    request: Request,
    handler: RunSimulationHandler = Depends(get_run_simulation_handler),
) -> RunSimulationResponse:
    cmd = RunSimulationCommand(campaign_id=campaign_id)
    result = await handler.handle(cmd)

    base_url = str(request.base_url).rstrip("/")
    return RunSimulationResponse(
        job_id=result.job_id,
        stream_url=f"{base_url}/api/v1/campaigns/{campaign_id}/simulate/{result.job_id}/stream",
        poll_url=f"{base_url}/api/v1/campaigns/{campaign_id}/simulate/{result.job_id}",
    )


@router.get("/{campaign_id}/simulate/{job_id}", response_model=SimulationResultDTO)
async def get_simulation_result(
    campaign_id: uuid.UUID,
    job_id: uuid.UUID,
) -> SimulationResultDTO:
    redis = get_redis_client()
    raw = await redis.get(f"sim_result:{job_id}")
    if raw is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation result not found or still running",
        )
    data = json.loads(raw)
    return SimulationResultDTO(
        job_id=job_id,
        campaign_id=campaign_id,
        triggered=data["triggered"],
        triggered_at_step=data.get("triggered_at_step"),
        final_status=data["final_status"],
        steps=[
            SimulationStepDTO(
                step=s["step"],
                hour=s["hour"],
                metrics=s["metrics"],
                rule_triggered=s["rule_triggered"],
                rule_description=s.get("rule_description"),
            )
            for s in data.get("steps", [])
        ],
    )
