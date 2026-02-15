"""manual create ix_estimate_events_unprocessed index (test)

Revision ID: manual_ix_estimate_events_unprocessed
Revises: 020ce6084655
Create Date: 2026-02-15 17:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'manual_ix_estimate_events_unprocessed'
down_revision: Union[str, None] = '020ce6084655'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add if_not_exists to prevent duplicate index error
    op.create_index('ix_estimate_events_unprocessed', 'estimate_events', ['processed_at'], unique=False, if_not_exists=True)

def downgrade() -> None:
    op.drop_index('ix_estimate_events_unprocessed', table_name='estimate_events', if_exists=True)
