from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from src.shared.domain.entity import Entity


@dataclass(eq=False)
class AudienceSegment(Entity):
    name: str
    campaign_id: uuid.UUID
    age_min: int = 18
    age_max: int = 65
    locations: list[str] = field(default_factory=list)    # e.g. ["US", "UK", "FR"]
    interests: list[str] = field(default_factory=list)    # e.g. ["sports", "tech"]
    device_types: list[str] = field(default_factory=list) # e.g. ["mobile", "desktop"]
