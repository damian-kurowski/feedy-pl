"""add category_mapping to feed_out

Revision ID: b2c3d4e5f6g7
Revises: 3ae88ff407a5
Create Date: 2026-04-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6g7"
down_revision = "3ae88ff407a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "feed_out",
        sa.Column("category_mapping", JSONB, nullable=True),
        schema="config",
    )


def downgrade() -> None:
    op.drop_column("feed_out", "category_mapping", schema="config")
