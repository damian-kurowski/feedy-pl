"""add branding fields to organizations

Revision ID: b7c8d9e0f1a2
Revises: 3ae88ff407a5
Create Date: 2026-04-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = '3ae88ff407a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('organizations', sa.Column('brand_name', sa.String(255), nullable=True), schema='auth')
    op.add_column('organizations', sa.Column('brand_color', sa.String(7), nullable=True), schema='auth')
    op.add_column('organizations', sa.Column('brand_logo_url', sa.String(2048), nullable=True), schema='auth')
    op.add_column('organizations', sa.Column('custom_domain', sa.String(255), nullable=True), schema='auth')


def downgrade() -> None:
    op.drop_column('organizations', 'custom_domain', schema='auth')
    op.drop_column('organizations', 'brand_logo_url', schema='auth')
    op.drop_column('organizations', 'brand_color', schema='auth')
    op.drop_column('organizations', 'brand_name', schema='auth')
