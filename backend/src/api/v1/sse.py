from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.shared.infrastructure.redis_client import get_redis_client

router = APIRouter(prefix="/campaigns", tags=["sse"])

_HEARTBEAT_INTERVAL = 15  # seconds


async def _sse_event(event_type: str, data: str) -> str:
    return f"event: {event_type}\ndata: {data}\n\n"


async def _simulation_stream(job_id: uuid.UUID) -> AsyncGenerator[str, None]:
    """Subscribe to Redis pub/sub and forward messages as SSE."""
    redis = get_redis_client()
    channel = f"sim:{job_id}"

    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    # Send an initial connection confirmation
    yield await _sse_event("connected", json.dumps({"job_id": str(job_id)}))

    try:
        while True:
            # Non-blocking get with a short timeout so we can send heartbeats
            message = await asyncio.wait_for(
                pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0),
                timeout=2.0,
            )

            if message is not None:
                raw = message.get("data", "")
                if isinstance(raw, bytes):
                    raw = raw.decode()

                try:
                    payload = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue

                event_type = payload.get("type", "step")
                yield await _sse_event(event_type, json.dumps(payload))

                if event_type in ("completed", "error"):
                    break
            else:
                # Heartbeat to keep connection alive
                yield ": heartbeat\n\n"

    except asyncio.TimeoutError:
        yield await _sse_event("error", json.dumps({"message": "stream timeout"}))
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()


@router.get(
    "/{campaign_id}/simulate/{job_id}/stream",
    summary="Stream simulation progress via Server-Sent Events",
    response_description="text/event-stream of simulation steps",
)
async def stream_simulation(campaign_id: uuid.UUID, job_id: uuid.UUID) -> StreamingResponse:
    return StreamingResponse(
        _simulation_stream(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
