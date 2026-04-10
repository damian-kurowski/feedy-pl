"""add organizations and org_members

Revision ID: a1b2c3d4e5f6
Revises: 5dc62ef81feb
Create Date: 2026-04-09 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5dc62ef81feb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('auth.plans.id'), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema='auth',
    )

    op.create_table(
        'org_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('auth.organizations.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth.users.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='member'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema='auth',
    )


def downgrade() -> None:
    op.drop_table('org_members', schema='auth')
    op.drop_table('organizations', schema='auth')
