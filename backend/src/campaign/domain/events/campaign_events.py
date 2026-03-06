from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.campaign.domain.value_objects.performance_rule import PerformanceRule
from src.shared.domain.domain_event import DomainEvent


@dataclass(frozen=True)
class CampaignCreated(DomainEvent):
    campaign_id: uuid.UUID
    name: str


@dataclass(frozen=True)
class RuleDefined(DomainEvent):
    campaign_id: uuid.UUID
    rule: PerformanceRule


@dataclass(frozen=True)
class SimulationStarted(DomainEvent):
    campaign_id: uuid.UUID
    job_id: uuid.UUID


@dataclass(frozen=True)
class RuleTriggered(DomainEvent):
    campaign_id: uuid.UUID
    job_id: uuid.UUID
    step: int
    metric_value: float
    rule: PerformanceRule


@dataclass(frozen=True)
class SimulationCompleted(DomainEvent):
    campaign_id: uuid.UUID
    job_id: uuid.UUID
    triggered: bool
    triggered_at_step: int | None = None
