"""merge_heads

Revision ID: 6304485bd4dd
Revises: b2c3d4e5f6g7, b7c8d9e0f1a2
Create Date: 2026-04-10 11:18:04.000457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6304485bd4dd'
down_revision: Union[str, None] = ('b2c3d4e5f6g7', 'b7c8d9e0f1a2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
