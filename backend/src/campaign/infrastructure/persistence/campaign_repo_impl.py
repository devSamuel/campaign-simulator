from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.campaign.domain.entities.audience_segment import AudienceSegment
from src.campaign.domain.entities.campaign import Campaign
from src.campaign.domain.entities.creativity import Creativity, CreativityType
from src.campaign.domain.repositories.campaign_repository import ICampaignRepository
from src.campaign.domain.value_objects.budget import Budget
from src.campaign.domain.value_objects.campaign_status import CampaignStatus
from src.campaign.domain.value_objects.metric_type import MetricType, RuleAction, RuleOperator
from src.campaign.domain.value_objects.performance_rule import PerformanceRule
from src.campaign.infrastructure.persistence.models import (
    AudienceSegmentModel,
    CampaignModel,
    CreativityModel,
    PerformanceRuleModel,
)


class PostgresCampaignRepository(ICampaignRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, campaign: Campaign) -> None:
        stmt = (
            select(CampaignModel)
            .where(CampaignModel.id == campaign.id)
            .options(
                selectinload(CampaignModel.creativities),
                selectinload(CampaignModel.audience_segment),
                selectinload(CampaignModel.performance_rule),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            model = CampaignModel(id=campaign.id)
            self._session.add(model)

        model.name = campaign.name
        model.status = str(campaign.status)
        model.budget_amount = float(campaign.budget.amount)
        model.budget_currency = campaign.budget.currency
        model.created_at = campaign.created_at
        model.updated_at = campaign.updated_at

        # Sync creativities: delete removed ones, upsert existing
        existing_ids = {c.id for c in (model.creativities or [])}
        domain_ids = {c.id for c in campaign.creativities}

        # Remove creativities no longer in the aggregate
        model.creativities = [c for c in (model.creativities or []) if c.id in domain_ids]

        for creativity in campaign.creativities:
            if creativity.id not in existing_ids:
                model.creativities.append(
                    CreativityModel(
                        id=creativity.id,
                        campaign_id=campaign.id,
                        name=creativity.name,
                        type=str(creativity.type),
                        asset_url=creativity.asset_url,
                    )
                )

        # Sync audience segment
        if campaign.audience_segment is not None:
            seg = campaign.audience_segment
            if model.audience_segment is None:
                model.audience_segment = AudienceSegmentModel(
                    id=seg.id,
                    campaign_id=campaign.id,
                )
            as_model = model.audience_segment
            as_model.name = seg.name
            as_model.age_min = seg.age_min
            as_model.age_max = seg.age_max
            as_model.locations = seg.locations
            as_model.interests = seg.interests
            as_model.device_types = seg.device_types
        else:
            model.audience_segment = None

        # Sync performance rule
        if campaign.rule is not None:
            rule = campaign.rule
            if model.performance_rule is None:
                model.performance_rule = PerformanceRuleModel(
                    id=uuid.uuid4(),
                    campaign_id=campaign.id,
                )
            pr_model = model.performance_rule
            pr_model.metric = str(rule.metric)
            pr_model.operator = str(rule.operator)
            pr_model.threshold = rule.threshold
            pr_model.action = str(rule.action)
        else:
            model.performance_rule = None

        await self._session.flush()

    async def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        stmt = (
            select(CampaignModel)
            .where(CampaignModel.id == campaign_id)
            .options(
                selectinload(CampaignModel.creativities),
                selectinload(CampaignModel.audience_segment),
                selectinload(CampaignModel.performance_rule),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_all(self, limit: int = 20, offset: int = 0) -> list[Campaign]:
        stmt = (
            select(CampaignModel)
            .options(
                selectinload(CampaignModel.creativities),
                selectinload(CampaignModel.audience_segment),
                selectinload(CampaignModel.performance_rule),
            )
            .order_by(CampaignModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    def _to_domain(self, model: CampaignModel) -> Campaign:
        budget = Budget(amount=Decimal(str(model.budget_amount)), currency=model.budget_currency)

        creativities = [
            Creativity(
                id=c.id,
                name=c.name,
                type=CreativityType(c.type),
                asset_url=c.asset_url,
                campaign_id=model.id,
            )
            for c in (model.creativities or [])
        ]

        audience_segment: AudienceSegment | None = None
        if model.audience_segment:
            seg = model.audience_segment
            audience_segment = AudienceSegment(
                id=seg.id,
                name=seg.name,
                campaign_id=model.id,
                age_min=seg.age_min,
                age_max=seg.age_max,
                locations=list(seg.locations or []),
                interests=list(seg.interests or []),
                device_types=list(seg.device_types or []),
            )

        rule: PerformanceRule | None = None
        if model.performance_rule:
            pr = model.performance_rule
            rule = PerformanceRule(
                metric=MetricType(pr.metric),
                operator=RuleOperator(pr.operator),
                threshold=pr.threshold,
                action=RuleAction(pr.action),
            )

        campaign = Campaign(
            id=model.id,
            name=model.name,
            budget=budget,
            status=CampaignStatus(model.status),
            creativities=creativities,
            audience_segment=audience_segment,
            rule=rule,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        return campaign
