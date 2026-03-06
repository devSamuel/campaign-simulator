from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.campaign.application.commands.create_campaign import (
    CreateCampaignAudienceInput,
    CreateCampaignCommand,
    CreateCampaignCreativityInput,
    CreateCampaignHandler,
    CreateCampaignRuleInput,
)
from src.campaign.application.dtos.campaign_dto import (
    CampaignDTO,
    CampaignSummaryDTO,
    CreateCampaignRequest,
    CreativityDTO,
)
from src.campaign.application.queries.get_campaign import GetCampaignHandler, GetCampaignQuery
from src.campaign.application.queries.list_campaigns import ListCampaignsHandler, ListCampaignsQuery
from src.campaign.domain.entities.campaign import Campaign
from src.api.dependencies import (
    get_campaign_handler,
    get_create_campaign_handler,
    get_list_campaigns_handler,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def _campaign_to_dto(campaign: Campaign) -> CampaignDTO:
    from src.campaign.application.dtos.campaign_dto import (
        AudienceSegmentDTO,
        BudgetDTO,
        PerformanceRuleDTO,
    )

    return CampaignDTO(
        id=campaign.id,
        name=campaign.name,
        status=str(campaign.status),
        budget=BudgetDTO(amount=campaign.budget.amount, currency=campaign.budget.currency),
        creativities=[
            CreativityDTO(id=c.id, name=c.name, type=str(c.type), asset_url=c.asset_url)
            for c in campaign.creativities
        ],
        audience_segment=(
            AudienceSegmentDTO(
                id=campaign.audience_segment.id,
                name=campaign.audience_segment.name,
                age_min=campaign.audience_segment.age_min,
                age_max=campaign.audience_segment.age_max,
                locations=campaign.audience_segment.locations,
                interests=campaign.audience_segment.interests,
                device_types=campaign.audience_segment.device_types,
            )
            if campaign.audience_segment
            else None
        ),
        rule=(
            PerformanceRuleDTO(
                metric=str(campaign.rule.metric),
                operator=str(campaign.rule.operator),
                threshold=campaign.rule.threshold,
                action=str(campaign.rule.action),
                description=campaign.rule.describe(),
            )
            if campaign.rule
            else None
        ),
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


@router.post("", response_model=CampaignDTO, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    body: CreateCampaignRequest,
    handler: CreateCampaignHandler = Depends(get_create_campaign_handler),
) -> CampaignDTO:
    cmd = CreateCampaignCommand(
        name=body.name,
        budget_amount=body.budget_amount,
        budget_currency=body.budget_currency,
        creativities=[
            CreateCampaignCreativityInput(name=c.name, type=c.type, asset_url=c.asset_url)
            for c in body.creativities
        ],
        audience=CreateCampaignAudienceInput(
            name=body.audience.name,
            age_min=body.audience.age_min,
            age_max=body.audience.age_max,
            locations=body.audience.locations,
            interests=body.audience.interests,
            device_types=body.audience.device_types,
        ),
        rule=CreateCampaignRuleInput(
            metric=body.rule.metric,
            operator=body.rule.operator,
            threshold=body.rule.threshold,
            action=body.rule.action,
        ),
    )
    campaign = await handler.handle(cmd)
    return _campaign_to_dto(campaign)


@router.get("", response_model=list[CampaignSummaryDTO])
async def list_campaigns(
    limit: int = 20,
    offset: int = 0,
    handler: ListCampaignsHandler = Depends(get_list_campaigns_handler),
) -> list[CampaignSummaryDTO]:
    from src.campaign.application.dtos.campaign_dto import BudgetDTO

    campaigns = await handler.handle(ListCampaignsQuery(limit=limit, offset=offset))
    return [
        CampaignSummaryDTO(
            id=c.id,
            name=c.name,
            status=str(c.status),
            budget=BudgetDTO(amount=c.budget.amount, currency=c.budget.currency),
            created_at=c.created_at,
        )
        for c in campaigns
    ]


@router.get("/{campaign_id}", response_model=CampaignDTO)
async def get_campaign(
    campaign_id: uuid.UUID,
    handler: GetCampaignHandler = Depends(get_campaign_handler),
) -> CampaignDTO:
    campaign = await handler.handle(GetCampaignQuery(campaign_id=campaign_id))
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return _campaign_to_dto(campaign)
