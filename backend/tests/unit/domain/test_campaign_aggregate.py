"""Unit tests for the Campaign aggregate root."""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from src.campaign.domain.entities.audience_segment import AudienceSegment
from src.campaign.domain.entities.campaign import Campaign
from src.campaign.domain.entities.creativity import Creativity, CreativityType
from src.campaign.domain.events.campaign_events import CampaignCreated, RuleDefined, SimulationStarted
from src.campaign.domain.value_objects.budget import Budget
from src.campaign.domain.value_objects.campaign_status import CampaignStatus
from src.campaign.domain.value_objects.metric_type import MetricType, RuleAction, RuleOperator
from src.campaign.domain.value_objects.performance_rule import PerformanceRule


def _budget() -> Budget:
    return Budget(amount=Decimal("5000.00"), currency="USD")


class TestCampaignCreation:
    def test_create_sets_draft_status(self) -> None:
        c = Campaign.create(name="Summer Sale", budget=_budget())
        assert c.status == CampaignStatus.DRAFT

    def test_create_emits_campaign_created_event(self) -> None:
        c = Campaign.create(name="Summer Sale", budget=_budget())
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], CampaignCreated)
        assert events[0].name == "Summer Sale"

    def test_pull_events_clears_queue(self) -> None:
        c = Campaign.create(name="X", budget=_budget())
        c.pull_events()
        assert c.pull_events() == []


class TestBudgetValueObject:
    def test_rejects_zero_amount(self) -> None:
        with pytest.raises(ValueError):
            Budget(amount=Decimal("0"), currency="USD")

    def test_rejects_negative_amount(self) -> None:
        with pytest.raises(ValueError):
            Budget(amount=Decimal("-100"), currency="USD")

    def test_rejects_invalid_currency_code(self) -> None:
        with pytest.raises(ValueError):
            Budget(amount=Decimal("100"), currency="USDD")


class TestCreativities:
    def test_add_creativity_to_campaign(self) -> None:
        c = Campaign.create(name="Test", budget=_budget())
        creativity = Creativity(
            name="Banner 1", type=CreativityType.BANNER, asset_url="https://cdn.example.com/b1.jpg", campaign_id=c.id
        )
        c.add_creativity(creativity)
        assert len(c.creativities) == 1

    def test_rejects_creativity_from_different_campaign(self) -> None:
        c = Campaign.create(name="Test", budget=_budget())
        creativity = Creativity(
            name="Banner 1", type=CreativityType.BANNER, asset_url="https://cdn.example.com/b1.jpg",
            campaign_id=uuid.uuid4()  # wrong campaign
        )
        with pytest.raises(ValueError):
            c.add_creativity(creativity)


class TestPerformanceRule:
    def test_define_rule_emits_event(self) -> None:
        c = Campaign.create(name="Test", budget=_budget())
        c.pull_events()  # clear create event
        rule = PerformanceRule(
            metric=MetricType.ROAS, operator=RuleOperator.LT, threshold=3.0, action=RuleAction.PAUSE_CAMPAIGN
        )
        c.define_rule(rule)
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], RuleDefined)

    def test_rule_describe_format(self) -> None:
        rule = PerformanceRule(
            metric=MetricType.ROAS, operator=RuleOperator.LT, threshold=3.0, action=RuleAction.PAUSE_CAMPAIGN
        )
        assert rule.describe() == "if ROAS < 3.0 → PAUSE_CAMPAIGN"


class TestSimulation:
    def test_start_simulation_emits_event(self) -> None:
        c = Campaign.create(name="Test", budget=_budget())
        rule = PerformanceRule(
            metric=MetricType.ROAS, operator=RuleOperator.LT, threshold=3.0, action=RuleAction.PAUSE_CAMPAIGN
        )
        c.define_rule(rule)
        c.pull_events()

        job_id = uuid.uuid4()
        c.start_simulation(job_id)
        events = c.pull_events()
        assert any(isinstance(e, SimulationStarted) for e in events)
        assert c.status == CampaignStatus.SIMULATING

    def test_cannot_simulate_without_rule(self) -> None:
        c = Campaign.create(name="Test", budget=_budget())
        with pytest.raises(ValueError, match="performance rule"):
            c.start_simulation(uuid.uuid4())

    def test_complete_simulation_pauses_on_trigger(self) -> None:
        c = Campaign.create(name="Test", budget=_budget())
        rule = PerformanceRule(
            metric=MetricType.ROAS, operator=RuleOperator.LT, threshold=3.0, action=RuleAction.PAUSE_CAMPAIGN
        )
        c.define_rule(rule)
        c.start_simulation(uuid.uuid4())
        c.complete_simulation(rule_triggered=True)
        assert c.status == CampaignStatus.PAUSED

    def test_complete_simulation_activates_on_no_trigger(self) -> None:
        c = Campaign.create(name="Test", budget=_budget())
        rule = PerformanceRule(
            metric=MetricType.ROAS, operator=RuleOperator.LT, threshold=3.0, action=RuleAction.PAUSE_CAMPAIGN
        )
        c.define_rule(rule)
        c.start_simulation(uuid.uuid4())
        c.complete_simulation(rule_triggered=False)
        assert c.status == CampaignStatus.ACTIVE
