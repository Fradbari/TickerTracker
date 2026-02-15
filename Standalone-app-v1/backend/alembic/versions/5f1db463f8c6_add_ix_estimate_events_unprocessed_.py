"""add ix_estimate_events_unprocessed index (clean)

Revision ID: 5f1db463f8c6
Revises: manual_ix_estimate_events_unprocessed
Create Date: 2026-02-15 16:55:45.536662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f1db463f8c6'
down_revision: Union[str, None] = 'manual_ix_estimate_events_unprocessed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add if_not_exists to prevent duplicate index error
    op.create_index('ix_estimate_events_unprocessed', 'estimate_events', ['processed_at'], unique=False, if_not_exists=True)


def downgrade() -> None:
    op.drop_index('ix_estimate_events_unprocessed', table_name='estimate_events', if_exists=True)
