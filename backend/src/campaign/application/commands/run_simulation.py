from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from src.campaign.infrastructure.persistence.models import SimulationJobModel
from src.campaign.domain.repositories.campaign_repository import ICampaignRepository
from src.shared.infrastructure.database import AsyncSessionFactory


@dataclass
class RunSimulationCommand:
    campaign_id: uuid.UUID


@dataclass
class RunSimulationResult:
    job_id: uuid.UUID
    campaign_id: uuid.UUID


class RunSimulationHandler:
    def __init__(self, repo: ICampaignRepository) -> None:
        self._repo = repo

    async def handle(self, cmd: RunSimulationCommand) -> RunSimulationResult:
        campaign = await self._repo.get_by_id(cmd.campaign_id)
        if campaign is None:
            raise ValueError(f"Campaign {cmd.campaign_id} not found")
        if campaign.rule is None:
            raise ValueError("Campaign has no performance rule defined")

        job_id = uuid.uuid4()

        # Persist the job record first (so SSE endpoint can find it)
        async with AsyncSessionFactory() as session:
            job = SimulationJobModel(
                id=job_id,
                campaign_id=campaign.id,
                status="PENDING",
                created_at=datetime.now(timezone.utc),
            )
            session.add(job)

            # Mark campaign as SIMULATING
            campaign.start_simulation(job_id)
            repo_in_session = type(self._repo)(session)  # same impl, new session
            await repo_in_session.save(campaign)
            await session.commit()

        # Dispatch Celery task (import here to avoid circular at module load)
        from src.campaign.infrastructure.tasks.simulation_task import simulate_campaign_task

        simulate_campaign_task.delay(str(campaign.id), str(job_id))

        return RunSimulationResult(job_id=job_id, campaign_id=campaign.id)
