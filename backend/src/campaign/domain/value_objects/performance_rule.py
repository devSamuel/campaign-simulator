from __future__ import annotations

from dataclasses import dataclass

from src.campaign.domain.value_objects.metric_type import MetricType, RuleAction, RuleOperator
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class PerformanceRule(ValueObject):
    """Defines a threshold-based rule: if <metric> <operator> <threshold> → <action>."""

    metric: MetricType
    operator: RuleOperator
    threshold: float
    action: RuleAction

    def describe(self) -> str:
        op_symbol = {
            RuleOperator.LT: "<",
            RuleOperator.GT: ">",
            RuleOperator.LTE: "<=",
            RuleOperator.GTE: ">=",
            RuleOperator.EQ: "==",
        }[self.operator]
        return f"if {self.metric} {op_symbol} {self.threshold} → {self.action}"
