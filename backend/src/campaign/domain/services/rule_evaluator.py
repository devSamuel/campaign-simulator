from __future__ import annotations

from src.campaign.domain.value_objects.metric_type import MetricType, RuleOperator
from src.campaign.domain.value_objects.performance_rule import PerformanceRule


class RuleEvaluatorService:
    """Pure, stateless domain service that evaluates a PerformanceRule against a metrics snapshot."""

    _OPERATORS = {
        RuleOperator.LT: float.__lt__,
        RuleOperator.GT: float.__gt__,
        RuleOperator.LTE: float.__le__,
        RuleOperator.GTE: float.__ge__,
        RuleOperator.EQ: float.__eq__,
    }

    @classmethod
    def evaluate(
        cls,
        rule: PerformanceRule,
        metrics: dict[MetricType, float],
    ) -> bool:
        """Return True if the rule condition is satisfied by the provided metrics.

        Args:
            rule: The performance rule to evaluate.
            metrics: A mapping of metric type → computed value.

        Returns:
            True if the rule fires (condition met), False otherwise.
        """
        metric_value = metrics.get(rule.metric)
        if metric_value is None:
            return False
        op_fn = cls._OPERATORS[rule.operator]
        return op_fn(metric_value, rule.threshold)
