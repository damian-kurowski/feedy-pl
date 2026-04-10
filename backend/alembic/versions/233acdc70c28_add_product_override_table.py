"""add product_override table

Revision ID: 233acdc70c28
Revises: 6304485bd4dd
Create Date: 2026-04-10 13:28:28.587026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '233acdc70c28'
down_revision: Union[str, None] = '6304485bd4dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'product_override',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('feed_out_id', sa.Integer(), sa.ForeignKey('config.feed_out.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_in_id', sa.BigInteger(), sa.ForeignKey('data.product_in.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_overrides', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('excluded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('feed_out_id', 'product_in_id'),
        schema='data',
    )


def downgrade() -> None:
    op.drop_table('product_override', schema='data')
