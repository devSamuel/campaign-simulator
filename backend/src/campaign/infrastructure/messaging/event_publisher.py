from __future__ import annotations

import json
import uuid
from datetime import datetime


class SimulationEventPublisher:
    """Publishes simulation step events to a Redis pub/sub channel.

    Channel name: sim:{job_id}
    """

    CHANNEL_PREFIX = "sim"

    def __init__(self, redis_client: object) -> None:  # aioredis.Redis
        self._redis = redis_client

    def channel(self, job_id: uuid.UUID) -> str:
        return f"{self.CHANNEL_PREFIX}:{job_id}"

    async def publish_step(
        self,
        job_id: uuid.UUID,
        step: int,
        hour: int,
        metrics: dict,
        rule_triggered: bool,
        rule_description: str | None = None,
    ) -> None:
        payload = json.dumps(
            {
                "type": "step",
                "job_id": str(job_id),
                "step": step,
                "hour": hour,
                "metrics": metrics,
                "rule_triggered": rule_triggered,
                "rule_description": rule_description,
            }
        )
        await self._redis.publish(self.channel(job_id), payload)

    async def publish_completed(
        self,
        job_id: uuid.UUID,
        triggered: bool,
        triggered_at_step: int | None,
        final_status: str,
    ) -> None:
        payload = json.dumps(
            {
                "type": "completed",
                "job_id": str(job_id),
                "triggered": triggered,
                "triggered_at_step": triggered_at_step,
                "final_status": final_status,
                "completed_at": datetime.utcnow().isoformat(),
            }
        )
        await self._redis.publish(self.channel(job_id), payload)

    async def publish_error(self, job_id: uuid.UUID, message: str) -> None:
        payload = json.dumps({"type": "error", "job_id": str(job_id), "message": message})
        await self._redis.publish(self.channel(job_id), payload)
