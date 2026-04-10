"""add rules to feed_out

Revision ID: 3ae88ff407a5
Revises: a1b2c3d4e5f6
Create Date: 2026-04-09 20:11:04.123957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '3ae88ff407a5'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('feed_out', sa.Column('rules', JSONB, nullable=True), schema='config')


def downgrade() -> None:
    op.drop_column('feed_out', 'rules', schema='config')
