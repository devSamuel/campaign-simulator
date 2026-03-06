from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetDTO(BaseModel):
    amount: Decimal
    currency: str


class CreativityDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str
    asset_url: str


class AudienceSegmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    age_min: int
    age_max: int
    locations: list[str]
    interests: list[str]
    device_types: list[str]


class PerformanceRuleDTO(BaseModel):
    metric: str
    operator: str
    threshold: float
    action: str
    description: str | None = None


class CampaignDTO(BaseModel):
    """Full campaign detail response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    status: str
    budget: BudgetDTO
    creativities: list[CreativityDTO] = Field(default_factory=list)
    audience_segment: AudienceSegmentDTO | None = None
    rule: PerformanceRuleDTO | None = None
    created_at: datetime
    updated_at: datetime


class CampaignSummaryDTO(BaseModel):
    """Lightweight campaign list item."""

    id: uuid.UUID
    name: str
    status: str
    budget: BudgetDTO
    created_at: datetime


# ── Request bodies ──────────────────────────────────────────────────────────

class CreateCampaignCreativityRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., description="BANNER | VIDEO | COPY")
    asset_url: str = Field(..., min_length=1)


class CreateCampaignAudienceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    age_min: int = Field(default=18, ge=0, le=120)
    age_max: int = Field(default=65, ge=0, le=120)
    locations: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    device_types: list[str] = Field(default_factory=list)


class CreateCampaignRuleRequest(BaseModel):
    metric: str = Field(..., description="ROAS | CTR | CPC | CPM | CPA")
    operator: str = Field(..., description="LT | GT | LTE | GTE | EQ")
    threshold: float
    action: str = Field(..., description="PAUSE_CAMPAIGN | REDUCE_BUDGET | SEND_ALERT")


class CreateCampaignRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    budget_amount: Decimal = Field(..., gt=0)
    budget_currency: str = Field(..., min_length=3, max_length=3)
    creativities: list[CreateCampaignCreativityRequest] = Field(..., min_length=1)
    audience: CreateCampaignAudienceRequest
    rule: CreateCampaignRuleRequest
