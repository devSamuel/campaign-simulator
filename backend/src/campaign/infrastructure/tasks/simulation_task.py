from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.campaign.domain.services.simulation_engine import SimulationEngine
from src.campaign.infrastructure.messaging.event_publisher import SimulationEventPublisher
from src.campaign.infrastructure.persistence.campaign_repo_impl import PostgresCampaignRepository
from src.campaign.infrastructure.persistence.models import SimulationJobModel
from src.shared.infrastructure.celery_app import celery_app
from src.shared.infrastructure.settings import settings


@celery_app.task(name="simulate_campaign", bind=True, max_retries=3)
def simulate_campaign_task(self, campaign_id: str, job_id: str) -> dict:  # type: ignore[no-untyped-def]
    """Celery task that runs the simulation and streams results via Redis pub/sub."""
    return asyncio.run(_run_simulation(campaign_id, job_id))


async def _run_simulation(campaign_id_str: str, job_id_str: str) -> dict:
    campaign_id = uuid.UUID(campaign_id_str)
    job_id = uuid.UUID(job_id_str)

    # Create fresh engine + Redis client per asyncio.run() call to avoid
    # "Future attached to a different loop" from global connection pools.
    local_engine = create_async_engine(settings.database_url, poolclass=NullPool)
    LocalSession: async_sessionmaker[AsyncSession] = async_sessionmaker(
        local_engine, expire_on_commit=False, class_=AsyncSession
    )
    redis_client: aioredis.Redis = aioredis.Redis.from_url(
        settings.redis_url, decode_responses=True
    )
    publisher = SimulationEventPublisher(redis_client)

    try:
        async with LocalSession() as session:
            repo = PostgresCampaignRepository(session)
            campaign = await repo.get_by_id(campaign_id)

            if campaign is None:
                await publisher.publish_error(job_id, f"Campaign {campaign_id} not found")
                return {"error": "campaign_not_found"}

            # Mark job as RUNNING
            job_model = await session.get(SimulationJobModel, job_id)
            if job_model:
                job_model.status = "RUNNING"
                await session.flush()

            try:
                engine = SimulationEngine()
                result = engine.run(campaign)

                # Stream each step via pub/sub
                for step in result.steps:
                    await publisher.publish_step(
                        job_id=job_id,
                        step=step.step,
                        hour=step.hour,
                        metrics={k.value: v for k, v in step.metrics.items()},
                        rule_triggered=step.rule_triggered,
                        rule_description=step.rule_description,
                    )
                    await asyncio.sleep(0.1)

                # Apply domain action and persist campaign state
                campaign.complete_simulation(result.triggered)
                await repo.save(campaign)

                # Persist simulation result
                result_payload = {
                    "triggered": result.triggered,
                    "triggered_at_step": result.triggered_at_step,
                    "final_status": result.final_status,
                    "steps": [
                        {
                            "step": s.step,
                            "hour": s.hour,
                            "metrics": {k.value: v for k, v in s.metrics.items()},
                            "rule_triggered": s.rule_triggered,
                            "rule_description": s.rule_description,
                        }
                        for s in result.steps
                    ],
                }

                if job_model:
                    job_model.status = "COMPLETED"
                    job_model.result = result_payload
                    job_model.completed_at = datetime.now(timezone.utc)

                await session.commit()

                # Cache result in Redis for polling endpoint
                await redis_client.setex(
                    f"sim_result:{job_id}",
                    settings.simulation_result_ttl,
                    json.dumps(result_payload),
                )

                # Publish completion event
                await publisher.publish_completed(
                    job_id=job_id,
                    triggered=result.triggered,
                    triggered_at_step=result.triggered_at_step,
                    final_status=result.final_status,
                )

                return result_payload

            except Exception as exc:
                if job_model:
                    job_model.status = "FAILED"
                    await session.commit()
                await publisher.publish_error(job_id, str(exc))
                raise

    finally:
        await local_engine.dispose()
        await redis_client.aclose()
