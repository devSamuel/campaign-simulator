from __future__ import annotations

import uuid

from pydantic import BaseModel


class SimulationStepDTO(BaseModel):
    step: int
    hour: int
    metrics: dict[str, float]
    rule_triggered: bool
    rule_description: str | None = None


class SimulationResultDTO(BaseModel):
    job_id: uuid.UUID
    campaign_id: uuid.UUID
    triggered: bool
    triggered_at_step: int | None
    final_status: str
    steps: list[SimulationStepDTO]


class RunSimulationResponse(BaseModel):
    job_id: uuid.UUID
    stream_url: str
    poll_url: str
