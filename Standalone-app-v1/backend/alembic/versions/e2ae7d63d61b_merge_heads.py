"""Merge heads

Revision ID: e2ae7d63d61b
Revises: 7f1c0d6b4a62, outbox_pattern_001
Create Date: 2026-02-15 15:02:13.180947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2ae7d63d61b'
down_revision: Union[str, None] = ('7f1c0d6b4a62', 'outbox_pattern_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
