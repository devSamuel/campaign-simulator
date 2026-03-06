"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-05
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("budget_amount", sa.DECIMAL(18, 4), nullable=False),
        sa.Column("budget_currency", sa.String(3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "creativities",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("campaign_id", sa.UUID(as_uuid=True), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("asset_url", sa.Text, nullable=False),
    )
    op.create_index("ix_creativities_campaign_id", "creativities", ["campaign_id"])

    op.create_table(
        "audience_segments",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("campaign_id", sa.UUID(as_uuid=True), sa.ForeignKey("campaigns.id"), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("age_min", sa.Integer, server_default="18"),
        sa.Column("age_max", sa.Integer, server_default="65"),
        sa.Column("locations", sa.JSON, server_default="[]"),
        sa.Column("interests", sa.JSON, server_default="[]"),
        sa.Column("device_types", sa.JSON, server_default="[]"),
    )

    op.create_table(
        "performance_rules",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("campaign_id", sa.UUID(as_uuid=True), sa.ForeignKey("campaigns.id"), unique=True, nullable=False),
        sa.Column("metric", sa.String(20), nullable=False),
        sa.Column("operator", sa.String(5), nullable=False),
        sa.Column("threshold", sa.Float, nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
    )

    op.create_table(
        "simulation_jobs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("campaign_id", sa.UUID(as_uuid=True), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("result", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_simulation_jobs_campaign_id", "simulation_jobs", ["campaign_id"])


def downgrade() -> None:
    op.drop_table("simulation_jobs")
    op.drop_table("performance_rules")
    op.drop_table("audience_segments")
    op.drop_table("creativities")
    op.drop_table("campaigns")
