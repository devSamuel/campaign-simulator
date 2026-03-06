from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.campaign.domain.entities.campaign import Campaign
from src.campaign.domain.repositories.campaign_repository import ICampaignRepository


@dataclass
class GetCampaignQuery:
    campaign_id: uuid.UUID


class GetCampaignHandler:
    def __init__(self, repo: ICampaignRepository) -> None:
        self._repo = repo

    async def handle(self, query: GetCampaignQuery) -> Campaign | None:
        return await self._repo.get_by_id(query.campaign_id)
