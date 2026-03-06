from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.campaign.domain.entities.campaign import Campaign
from src.campaign.domain.services.rule_evaluator import RuleEvaluatorService
from src.campaign.domain.value_objects.metric_type import MetricType


@dataclass
class SimulationStep:
    """Result of one simulation time step."""

    step: int                                # 0-based step index
    hour: int                                # simulated hour of day (0–23)
    metrics: dict[MetricType, float]
    rule_triggered: bool
    rule_description: str | None = None


@dataclass
class SimulationResult:
    steps: list[SimulationStep] = field(default_factory=list)
    triggered: bool = False
    triggered_at_step: int | None = None
    final_status: str = "ACTIVE"


class SimulationEngine:
    """Domain service that generates synthetic campaign performance data over 24 hourly steps.

    Metric generation follows a simple random-walk model seeded from the campaign id
    so results are reproducible for the same campaign.
    """

    STEPS = 24  # one per hour

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def run(self, campaign: Campaign) -> SimulationResult:
        if campaign.rule is None:
            raise ValueError("Campaign has no performance rule to simulate against")

        result = SimulationResult()
        # Use campaign id as seed for reproducibility
        rng = random.Random(int(campaign.id) % (2**32))

        # Base ROAS drifts downward over time to make rule triggering visible
        base_roas = rng.uniform(3.5, 5.5)
        roas_drift = rng.uniform(-0.15, -0.05)  # ROAS degrades each hour

        for step in range(self.STEPS):
            hour = step
            impressions = rng.randint(1_000, 50_000)
            ctr = rng.uniform(0.01, 0.05)
            clicks = max(1, int(impressions * ctr))
            cpc = rng.uniform(0.10, 2.00)
            spend = clicks * cpc

            # ROAS drifts downward over time
            current_roas = max(0.5, base_roas + step * roas_drift + rng.uniform(-0.3, 0.3))
            revenue = spend * current_roas

            conversions = max(0, int(clicks * rng.uniform(0.01, 0.05)))
            cpa = spend / conversions if conversions > 0 else 0.0
            cpm = (spend / impressions) * 1_000

            metrics: dict[MetricType, float] = {
                MetricType.ROAS: round(current_roas, 4),
                MetricType.CTR: round(ctr, 4),
                MetricType.CPC: round(cpc, 4),
                MetricType.CPM: round(cpm, 4),
                MetricType.CPA: round(cpa, 4),
            }

            rule_triggered = RuleEvaluatorService.evaluate(campaign.rule, metrics)

            sim_step = SimulationStep(
                step=step,
                hour=hour,
                metrics=metrics,
                rule_triggered=rule_triggered,
                rule_description=campaign.rule.describe() if rule_triggered else None,
            )
            result.steps.append(sim_step)

            if rule_triggered and not result.triggered:
                result.triggered = True
                result.triggered_at_step = step

        result.final_status = "PAUSED" if result.triggered else "ACTIVE"
        return result
