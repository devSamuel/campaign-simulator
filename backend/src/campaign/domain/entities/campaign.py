from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.campaign.domain.entities.audience_segment import AudienceSegment
from src.campaign.domain.entities.creativity import Creativity
from src.campaign.domain.events.campaign_events import (
    CampaignCreated,
    RuleDefined,
    SimulationStarted,
)
from src.campaign.domain.value_objects.budget import Budget
from src.campaign.domain.value_objects.campaign_status import CampaignStatus
from src.campaign.domain.value_objects.performance_rule import PerformanceRule
from src.shared.domain.aggregate_root import AggregateRoot


@dataclass(eq=False)
class Campaign(AggregateRoot):
    """Campaign aggregate root.

    Owns creativities and the audience segment. Holds a single performance rule.
    Status transitions are enforced here, keeping invariants inside the domain.
    """

    name: str
    budget: Budget
    status: CampaignStatus = field(default=CampaignStatus.DRAFT)
    creativities: list[Creativity] = field(default_factory=list)
    audience_segment: AudienceSegment | None = field(default=None)
    rule: PerformanceRule | None = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, name: str, budget: Budget) -> "Campaign":
        campaign = cls(name=name, budget=budget)
        campaign.record_event(CampaignCreated(campaign_id=campaign.id, name=campaign.name))
        return campaign

    def add_creativity(self, creativity: Creativity) -> None:
        if creativity.campaign_id != self.id:
            raise ValueError("Creativity does not belong to this campaign")
        self.creativities.append(creativity)
        self._touch()

    def set_audience_segment(self, segment: AudienceSegment) -> None:
        if segment.campaign_id != self.id:
            raise ValueError("Audience segment does not belong to this campaign")
        self.audience_segment = segment
        self._touch()

    def define_rule(self, rule: PerformanceRule) -> None:
        self.rule = rule
        self._touch()
        self.record_event(RuleDefined(campaign_id=self.id, rule=rule))

    def start_simulation(self, job_id: uuid.UUID) -> None:
        if self.rule is None:
            raise ValueError("Cannot simulate a campaign without a performance rule")
        self.status = CampaignStatus.SIMULATING
        self._touch()
        self.record_event(SimulationStarted(campaign_id=self.id, job_id=job_id))

    def apply_rule_action(self) -> None:
        """Apply the action defined in the rule (called after simulation triggers)."""
        from src.campaign.domain.value_objects.metric_type import RuleAction

        if self.rule is None:
            return
        if self.rule.action == RuleAction.PAUSE_CAMPAIGN:
            self.status = CampaignStatus.PAUSED
        elif self.rule.action == RuleAction.REDUCE_BUDGET:
            # Reduce budget by 20% as a sensible default
            from decimal import Decimal

            new_amount = self.budget.amount * Decimal("0.80")
            self.budget = Budget(amount=new_amount, currency=self.budget.currency)
        # SEND_ALERT does not change status
        self._touch()

    def complete_simulation(self, rule_triggered: bool) -> None:
        if rule_triggered:
            self.apply_rule_action()
        elif self.status == CampaignStatus.SIMULATING:
            self.status = CampaignStatus.ACTIVE
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
