"""add value_map table

Revision ID: ee1be193c82d
Revises: 95443a188e6d
Create Date: 2026-04-11 16:02:10.553120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'ee1be193c82d'
down_revision: Union[str, None] = '95443a188e6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'value_map',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('mappings', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='config',
    )
    # Add field_maps column to feed_out for linking maps to fields
    op.add_column('feed_out', sa.Column('field_maps', postgresql.JSONB()), schema='config')


def downgrade() -> None:
    op.drop_column('feed_out', 'field_maps', schema='config')
    op.drop_table('value_map', schema='config')
