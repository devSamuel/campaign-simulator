from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum

from src.shared.domain.entity import Entity


class CreativityType(StrEnum):
    BANNER = "BANNER"
    VIDEO = "VIDEO"
    COPY = "COPY"


@dataclass(eq=False)
class Creativity(Entity):
    name: str
    type: CreativityType
    asset_url: str
    campaign_id: uuid.UUID
