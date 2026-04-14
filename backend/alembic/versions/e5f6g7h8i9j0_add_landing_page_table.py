"""add landing_page table

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-04-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "e5f6g7h8i9j0"
down_revision = "d4e5f6g7h8i9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "landing_page",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("auth.users.id"), nullable=False, index=True),
        sa.Column("slug", sa.String(512), unique=True, nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("short_description", sa.String(500), nullable=True),
        sa.Column("full_description", sa.Text, nullable=True),
        sa.Column("hero_image", sa.String(512), nullable=True),
        sa.Column("gallery", JSONB, nullable=True),
        sa.Column("price", sa.String(100), nullable=True),
        sa.Column("price_negotiable", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("cta_text", sa.String(100), nullable=True),
        sa.Column("cta_url", sa.String(1024), nullable=True),
        sa.Column("meta_title", sa.String(255), nullable=True),
        sa.Column("meta_description", sa.String(320), nullable=True),
        sa.Column("is_indexable", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("is_followable", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("is_published", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        schema="config",
    )


def downgrade() -> None:
    op.drop_table("landing_page", schema="config")
