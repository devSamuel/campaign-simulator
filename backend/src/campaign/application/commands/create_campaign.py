from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from src.campaign.domain.entities.audience_segment import AudienceSegment
from src.campaign.domain.entities.campaign import Campaign
from src.campaign.domain.entities.creativity import Creativity, CreativityType
from src.campaign.domain.repositories.campaign_repository import ICampaignRepository
from src.campaign.domain.value_objects.budget import Budget
from src.campaign.domain.value_objects.metric_type import MetricType, RuleAction, RuleOperator
from src.campaign.domain.value_objects.performance_rule import PerformanceRule


@dataclass
class CreateCampaignCreativityInput:
    name: str
    type: str
    asset_url: str


@dataclass
class CreateCampaignAudienceInput:
    name: str
    age_min: int = 18
    age_max: int = 65
    locations: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)
    device_types: list[str] = field(default_factory=list)


@dataclass
class CreateCampaignRuleInput:
    metric: str
    operator: str
    threshold: float
    action: str


@dataclass
class CreateCampaignCommand:
    name: str
    budget_amount: Decimal
    budget_currency: str
    creativities: list[CreateCampaignCreativityInput]
    audience: CreateCampaignAudienceInput
    rule: CreateCampaignRuleInput


class CreateCampaignHandler:
    def __init__(self, repo: ICampaignRepository) -> None:
        self._repo = repo

    async def handle(self, cmd: CreateCampaignCommand) -> Campaign:
        budget = Budget(amount=cmd.budget_amount, currency=cmd.budget_currency.upper())
        campaign = Campaign.create(name=cmd.name, budget=budget)

        for c in cmd.creativities:
            creativity = Creativity(
                name=c.name,
                type=CreativityType(c.type.upper()),
                asset_url=c.asset_url,
                campaign_id=campaign.id,
            )
            campaign.add_creativity(creativity)

        segment = AudienceSegment(
            name=cmd.audience.name,
            campaign_id=campaign.id,
            age_min=cmd.audience.age_min,
            age_max=cmd.audience.age_max,
            locations=cmd.audience.locations,
            interests=cmd.audience.interests,
            device_types=cmd.audience.device_types,
        )
        campaign.set_audience_segment(segment)

        rule = PerformanceRule(
            metric=MetricType(cmd.rule.metric.upper()),
            operator=RuleOperator(cmd.rule.operator.upper()),
            threshold=cmd.rule.threshold,
            action=RuleAction(cmd.rule.action.upper()),
        )
        campaign.define_rule(rule)

        await self._repo.save(campaign)
        return campaign
