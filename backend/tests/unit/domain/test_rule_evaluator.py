"""Unit tests for RuleEvaluatorService — no I/O, pure domain logic."""
from __future__ import annotations

import pytest

from src.campaign.domain.services.rule_evaluator import RuleEvaluatorService
from src.campaign.domain.value_objects.metric_type import MetricType, RuleAction, RuleOperator
from src.campaign.domain.value_objects.performance_rule import PerformanceRule


def _rule(metric: MetricType, operator: RuleOperator, threshold: float) -> PerformanceRule:
    return PerformanceRule(metric=metric, operator=operator, threshold=threshold, action=RuleAction.PAUSE_CAMPAIGN)


class TestRuleEvaluator:
    def test_roas_lt_triggers_when_below_threshold(self) -> None:
        rule = _rule(MetricType.ROAS, RuleOperator.LT, 3.0)
        metrics = {MetricType.ROAS: 2.5}
        assert RuleEvaluatorService.evaluate(rule, metrics) is True

    def test_roas_lt_does_not_trigger_when_above_threshold(self) -> None:
        rule = _rule(MetricType.ROAS, RuleOperator.LT, 3.0)
        metrics = {MetricType.ROAS: 3.5}
        assert RuleEvaluatorService.evaluate(rule, metrics) is False

    def test_roas_lt_boundary_not_triggered(self) -> None:
        """LT is strict: value == threshold should NOT trigger."""
        rule = _rule(MetricType.ROAS, RuleOperator.LT, 3.0)
        metrics = {MetricType.ROAS: 3.0}
        assert RuleEvaluatorService.evaluate(rule, metrics) is False

    def test_roas_lte_boundary_triggers(self) -> None:
        rule = _rule(MetricType.ROAS, RuleOperator.LTE, 3.0)
        metrics = {MetricType.ROAS: 3.0}
        assert RuleEvaluatorService.evaluate(rule, metrics) is True

    def test_ctr_gt_triggers(self) -> None:
        rule = _rule(MetricType.CTR, RuleOperator.GT, 0.05)
        metrics = {MetricType.CTR: 0.07}
        assert RuleEvaluatorService.evaluate(rule, metrics) is True

    def test_ctr_gt_does_not_trigger(self) -> None:
        rule = _rule(MetricType.CTR, RuleOperator.GT, 0.05)
        metrics = {MetricType.CTR: 0.03}
        assert RuleEvaluatorService.evaluate(rule, metrics) is False

    def test_eq_operator(self) -> None:
        rule = _rule(MetricType.CPC, RuleOperator.EQ, 1.0)
        assert RuleEvaluatorService.evaluate(rule, {MetricType.CPC: 1.0}) is True
        assert RuleEvaluatorService.evaluate(rule, {MetricType.CPC: 1.1}) is False

    def test_missing_metric_returns_false(self) -> None:
        """If the metric is not present in the snapshot, do not trigger."""
        rule = _rule(MetricType.ROAS, RuleOperator.LT, 3.0)
        assert RuleEvaluatorService.evaluate(rule, {}) is False

    def test_multiple_metrics_evaluates_correct_one(self) -> None:
        rule = _rule(MetricType.ROAS, RuleOperator.LT, 3.0)
        metrics = {
            MetricType.ROAS: 2.0,
            MetricType.CTR: 0.01,
            MetricType.CPC: 5.0,
        }
        assert RuleEvaluatorService.evaluate(rule, metrics) is True
