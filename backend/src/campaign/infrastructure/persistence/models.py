from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DECIMAL,
    JSON,
    UUID,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CampaignModel(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    budget_amount: Mapped[float] = mapped_column(DECIMAL(18, 4), nullable=False)
    budget_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    creativities: Mapped[list[CreativityModel]] = relationship(
        "CreativityModel", back_populates="campaign", cascade="all, delete-orphan"
    )
    audience_segment: Mapped[AudienceSegmentModel | None] = relationship(
        "AudienceSegmentModel", back_populates="campaign", uselist=False, cascade="all, delete-orphan"
    )
    performance_rule: Mapped[PerformanceRuleModel | None] = relationship(
        "PerformanceRuleModel", back_populates="campaign", uselist=False, cascade="all, delete-orphan"
    )
    simulation_jobs: Mapped[list[SimulationJobModel]] = relationship(
        "SimulationJobModel", back_populates="campaign", cascade="all, delete-orphan"
    )


class CreativityModel(Base):
    __tablename__ = "creativities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    asset_url: Mapped[str] = mapped_column(Text, nullable=False)

    campaign: Mapped[CampaignModel] = relationship("CampaignModel", back_populates="creativities")


class AudienceSegmentModel(Base):
    __tablename__ = "audience_segments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    age_min: Mapped[int] = mapped_column(Integer, default=18)
    age_max: Mapped[int] = mapped_column(Integer, default=65)
    locations: Mapped[list] = mapped_column(JSON, default=list)
    interests: Mapped[list] = mapped_column(JSON, default=list)
    device_types: Mapped[list] = mapped_column(JSON, default=list)

    campaign: Mapped[CampaignModel] = relationship("CampaignModel", back_populates="audience_segment")


class PerformanceRuleModel(Base):
    __tablename__ = "performance_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), unique=True, nullable=False
    )
    metric: Mapped[str] = mapped_column(String(20), nullable=False)
    operator: Mapped[str] = mapped_column(String(5), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)

    campaign: Mapped[CampaignModel] = relationship("CampaignModel", back_populates="performance_rule")


class SimulationJobModel(Base):
    __tablename__ = "simulation_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped[CampaignModel] = relationship("CampaignModel", back_populates="simulation_jobs")
