"""seed plans

Revision ID: 4eb11564563e
Revises: 127bd2bf0b5d
Create Date: 2026-04-09 18:48:43.205421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4eb11564563e'
down_revision: Union[str, None] = '127bd2bf0b5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO auth.plans (id, name, max_products, max_feeds_out, price_pln) VALUES
        (1, 'Free', 200, 1, 0),
        (2, 'Starter', 1000, 3, 29),
        (3, 'Pro', 5000, 10, 59),
        (4, 'Business', 20000, NULL, 99)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM auth.plans WHERE id IN (1, 2, 3, 4)")
