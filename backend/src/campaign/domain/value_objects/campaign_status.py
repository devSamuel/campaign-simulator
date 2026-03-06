from __future__ import annotations

from enum import StrEnum


class CampaignStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SIMULATING = "SIMULATING"
