"""add envelope to feed_out

Revision ID: c3d4e5f6g7h8
Revises: ee1be193c82d
Create Date: 2026-04-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "c3d4e5f6g7h8"
down_revision = "ee1be193c82d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "feed_out",
        sa.Column("envelope", JSONB, nullable=True),
        schema="config",
    )


def downgrade() -> None:
    op.drop_column("feed_out", "envelope", schema="config")
