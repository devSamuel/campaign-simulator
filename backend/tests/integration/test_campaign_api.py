"""Integration tests for the full campaign API flow.

Requires a running PostgreSQL + Redis + RabbitMQ (use docker compose).
Set DATABASE_URL, REDIS_URL, CELERY_BROKER_URL env vars before running.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from src.api.main import app
from src.shared.infrastructure.database import engine

CAMPAIGN_PAYLOAD = {
    "name": "Summer Sale",
    "budget_amount": "10000.00",
    "budget_currency": "USD",
    "creativities": [
        {"name": "Banner Ad", "type": "BANNER", "asset_url": "https://cdn.example.com/banner.jpg"}
    ],
    "audience": {
        "name": "Young Adults",
        "age_min": 18,
        "age_max": 35,
        "locations": ["US", "UK"],
        "interests": ["sports", "tech"],
        "device_types": ["mobile"],
    },
    "rule": {"metric": "ROAS", "operator": "LT", "threshold": 3.0, "action": "PAUSE_CAMPAIGN"},
}


@pytest.fixture(autouse=True)
async def reset_engine() -> None:
    yield
    await engine.dispose()


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_full_campaign_creator_flow(client: AsyncClient) -> None:
    # 1. Create campaign with creativities, audience, and rule in one request
    resp = await client.post("/api/v1/campaigns", json=CAMPAIGN_PAYLOAD)
    assert resp.status_code == 201
    campaign = resp.json()
    campaign_id = campaign["id"]
    assert campaign["status"] == "DRAFT"
    assert campaign["rule"]["metric"] == "ROAS"
    assert campaign["rule"]["description"] == "if ROAS < 3.0 → PAUSE_CAMPAIGN"
    assert len(campaign["creativities"]) == 1
    assert campaign["audience_segment"]["name"] == "Young Adults"

    # 2. Start simulation
    resp = await client.post(f"/api/v1/campaigns/{campaign_id}/simulate")
    assert resp.status_code == 202
    sim_data = resp.json()
    assert "job_id" in sim_data
    assert "stream_url" in sim_data
    assert "poll_url" in sim_data

    # 3. Retrieve the campaign — status should be SIMULATING
    resp = await client.get(f"/api/v1/campaigns/{campaign_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "SIMULATING"


@pytest.mark.asyncio
async def test_list_campaigns(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/campaigns", json=CAMPAIGN_PAYLOAD)
    assert resp.status_code == 201

    resp = await client.get("/api/v1/campaigns")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_get_nonexistent_campaign(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/campaigns/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
