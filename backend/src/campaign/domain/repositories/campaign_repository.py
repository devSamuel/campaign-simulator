from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.campaign.domain.entities.campaign import Campaign


class ICampaignRepository(ABC):
    """Abstract repository interface — part of the domain layer.

    Infrastructure implementations must not leak into the domain.
    """

    @abstractmethod
    async def save(self, campaign: Campaign) -> None:
        """Persist a new or updated campaign aggregate."""

    @abstractmethod
    async def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        """Return the campaign aggregate or None if not found."""

    @abstractmethod
    async def list_all(self, limit: int = 20, offset: int = 0) -> list[Campaign]:
        """Return a paginated list of campaigns."""
