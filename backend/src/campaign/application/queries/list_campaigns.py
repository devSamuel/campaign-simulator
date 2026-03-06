from __future__ import annotations

from dataclasses import dataclass

from src.campaign.domain.entities.campaign import Campaign
from src.campaign.domain.repositories.campaign_repository import ICampaignRepository


@dataclass
class ListCampaignsQuery:
    limit: int = 20
    offset: int = 0


class ListCampaignsHandler:
    def __init__(self, repo: ICampaignRepository) -> None:
        self._repo = repo

    async def handle(self, query: ListCampaignsQuery) -> list[Campaign]:
        return await self._repo.list_all(limit=query.limit, offset=query.offset)
