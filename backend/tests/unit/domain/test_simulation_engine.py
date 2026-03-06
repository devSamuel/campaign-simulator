"""Unit tests for SimulationEngine — pure domain logic, no I/O."""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from src.campaign.domain.entities.campaign import Campaign
from src.campaign.domain.services.simulation_engine import SimulationEngine
from src.campaign.domain.value_objects.budget import Budget
from src.campaign.domain.value_objects.campaign_status import CampaignStatus
from src.campaign.domain.value_objects.metric_type import MetricType, RuleAction, RuleOperator
from src.campaign.domain.value_objects.performance_rule import PerformanceRule


def _make_campaign(metric: MetricType = MetricType.ROAS, threshold: float = 3.0) -> Campaign:
    budget = Budget(amount=Decimal("10000.00"), currency="USD")
    campaign = Campaign.create(name="Test Campaign", budget=budget)
    campaign.define_rule(
        PerformanceRule(
            metric=metric,
            operator=RuleOperator.LT,
            threshold=threshold,
            action=RuleAction.PAUSE_CAMPAIGN,
        )
    )
    return campaign


class TestSimulationEngine:
    def test_produces_24_steps(self) -> None:
        campaign = _make_campaign()
        engine = SimulationEngine()
        result = engine.run(campaign)
        assert len(result.steps) == 24

    def test_step_hours_are_sequential(self) -> None:
        campaign = _make_campaign()
        result = SimulationEngine().run(campaign)
        hours = [s.hour for s in result.steps]
        assert hours == list(range(24))

    def test_all_metrics_present_each_step(self) -> None:
        campaign = _make_campaign()
        result = SimulationEngine().run(campaign)
        expected_metrics = {MetricType.ROAS, MetricType.CTR, MetricType.CPC, MetricType.CPM, MetricType.CPA}
        for step in result.steps:
            assert set(step.metrics.keys()) == expected_metrics

    def test_roas_metrics_are_positive(self) -> None:
        campaign = _make_campaign()
        result = SimulationEngine().run(campaign)
        for step in result.steps:
            assert step.metrics[MetricType.ROAS] > 0

    def test_rule_triggered_flag_matches_evaluator(self) -> None:
        """Each step's rule_triggered must be consistent with the metric value."""
        campaign = _make_campaign(metric=MetricType.ROAS, threshold=3.0)
        result = SimulationEngine().run(campaign)
        for step in result.steps:
            roas = step.metrics[MetricType.ROAS]
            expected = roas < 3.0
            assert step.rule_triggered == expected, (
                f"Step {step.step}: ROAS={roas}, expected triggered={expected}, got {step.rule_triggered}"
            )

    def test_simulation_result_triggered_set_correctly(self) -> None:
        """triggered is True iff at least one step had rule_triggered=True."""
        campaign = _make_campaign()
        result = SimulationEngine().run(campaign)
        any_triggered = any(s.rule_triggered for s in result.steps)
        assert result.triggered == any_triggered

    def test_triggered_at_step_is_first_trigger(self) -> None:
        campaign = _make_campaign()
        result = SimulationEngine().run(campaign)
        if result.triggered:
            first_trigger = next(s.step for s in result.steps if s.rule_triggered)
            assert result.triggered_at_step == first_trigger

    def test_never_triggers_with_impossibly_high_threshold(self) -> None:
        """With threshold 0 and GT operator (metric > 0 always true), every step triggers."""
        budget = Budget(amount=Decimal("1000.00"), currency="USD")
        campaign = Campaign.create(name="Always Trigger", budget=budget)
        campaign.define_rule(
            PerformanceRule(
                metric=MetricType.ROAS,
                operator=RuleOperator.GT,
                threshold=0.0,
                action=RuleAction.SEND_ALERT,
            )
        )
        result = SimulationEngine().run(campaign)
        assert result.triggered is True
        assert all(s.rule_triggered for s in result.steps)

    def test_reproducible_with_same_campaign_id(self) -> None:
        """Two runs with the same campaign produce identical results."""
        campaign = _make_campaign()
        r1 = SimulationEngine().run(campaign)
        r2 = SimulationEngine().run(campaign)
        assert [s.metrics for s in r1.steps] == [s.metrics for s in r2.steps]

    def test_raises_without_rule(self) -> None:
        budget = Budget(amount=Decimal("1000.00"), currency="USD")
        campaign = Campaign.create(name="No Rule", budget=budget)
        with pytest.raises(ValueError, match="no performance rule"):
            SimulationEngine().run(campaign)
