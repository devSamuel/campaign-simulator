from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.campaign.application.commands.create_campaign import CreateCampaignHandler
from src.campaign.application.commands.run_simulation import RunSimulationHandler
from src.campaign.application.queries.get_campaign import GetCampaignHandler
from src.campaign.application.queries.list_campaigns import ListCampaignsHandler
from src.campaign.infrastructure.persistence.campaign_repo_impl import PostgresCampaignRepository
from src.shared.infrastructure.database import get_db


# ── Session ──────────────────────────────────────────────────────────────────

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


# ── Repository ───────────────────────────────────────────────────────────────

def get_campaign_repo(session: AsyncSession = Depends(get_session)) -> PostgresCampaignRepository:
    return PostgresCampaignRepository(session)


# ── Command handlers ─────────────────────────────────────────────────────────

def get_create_campaign_handler(
    repo: PostgresCampaignRepository = Depends(get_campaign_repo),
) -> CreateCampaignHandler:
    return CreateCampaignHandler(repo)


def get_run_simulation_handler(
    repo: PostgresCampaignRepository = Depends(get_campaign_repo),
) -> RunSimulationHandler:
    return RunSimulationHandler(repo)


# ── Query handlers ───────────────────────────────────────────────────────────

def get_campaign_handler(
    repo: PostgresCampaignRepository = Depends(get_campaign_repo),
) -> GetCampaignHandler:
    return GetCampaignHandler(repo)


def get_list_campaigns_handler(
    repo: PostgresCampaignRepository = Depends(get_campaign_repo),
) -> ListCampaignsHandler:
    return ListCampaignsHandler(repo)
