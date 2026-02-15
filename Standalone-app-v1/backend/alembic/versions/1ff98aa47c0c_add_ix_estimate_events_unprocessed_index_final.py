"""add ix_estimate_events_unprocessed index (final)

Revision ID: 1ff98aa47c0c
Revises: 794dbcf91a85
Create Date: 2026-02-15 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ff98aa47c0c'
down_revision: Union[str, None] = '794dbcf91a85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    This migration marks the stable state after all manual index fixes.
    
    All required database changes have been applied in previous migrations:
    - outbox_pattern_001: Added processed_at, retry_count, error columns
    - 7f1c0d6b4a62: Added soft delete to estimates
    - e2ae7d63d61b: Merged parallel branches
    - 020ce6084655, manual_ix, 5f1db463f8c6, 794dbcf91a85: Fixed indexes
    
    This migration serves as a checkpoint for verification scripts.
    No additional changes needed.
    """
    pass


def downgrade() -> None:
    """
    No-op downgrade since this migration doesn't change anything.
    """
    pass
