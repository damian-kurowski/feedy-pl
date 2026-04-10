"""add uploaded_image feed_change_log and plan columns

Revision ID: 95443a188e6d
Revises: 233acdc70c28
Create Date: 2026-04-10 14:20:18.753575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '95443a188e6d'
down_revision: Union[str, None] = '233acdc70c28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # uploaded_image table
    op.create_table(
        'uploaded_image',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_filename', sa.String(512), nullable=False),
        sa.Column('stored_path', sa.String(1024), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='data',
    )

    # feed_change_log table
    op.create_table(
        'feed_change_log',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('feed_in_id', sa.Integer(), sa.ForeignKey('config.feed_in.id', ondelete='CASCADE'), nullable=False),
        sa.Column('change_type', sa.String(20), nullable=False),
        sa.Column('product_name', sa.String(512)),
        sa.Column('details', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='data',
    )

    # New columns on plans
    op.add_column('plans', sa.Column('ai_rewrites_monthly', sa.Integer()), schema='auth')
    op.add_column('plans', sa.Column('upload_storage_mb', sa.Integer()), schema='auth')
    op.add_column('plans', sa.Column('changelog_days', sa.Integer()), schema='auth')

    # Usage tracking table
    op.create_table(
        'usage',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('month', sa.String(7), nullable=False),
        sa.Column('ai_rewrites_used', sa.Integer(), nullable=False, server_default='0'),
        sa.UniqueConstraint('user_id', 'month'),
        schema='auth',
    )


def downgrade() -> None:
    op.drop_table('usage', schema='auth')
    op.drop_column('plans', 'changelog_days', schema='auth')
    op.drop_column('plans', 'upload_storage_mb', schema='auth')
    op.drop_column('plans', 'ai_rewrites_monthly', schema='auth')
    op.drop_table('feed_change_log', schema='data')
    op.drop_table('uploaded_image', schema='data')
