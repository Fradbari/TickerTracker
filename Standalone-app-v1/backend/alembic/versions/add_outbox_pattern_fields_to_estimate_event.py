"""Add Outbox pattern fields to EstimateEvent

Revision ID: outbox_pattern_001
Revises: e97b3b8578e1
Create Date: 2026-02-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'outbox_pattern_001'
down_revision = 'e97b3b8578e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add processed_at column
    op.add_column(
        'estimate_events',
        sa.Column(
            'processed_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When event was successfully processed to Drive"
        )
    )
    
    # Add retry_count column with default value 0
    op.add_column(
        'estimate_events',
        sa.Column(
            'retry_count',
            sa.Integer(),
            nullable=False,
            server_default='0',
            comment="Number of processing retry attempts"
        )
    )
    
    # Add error column for error messages
    op.add_column(
        'estimate_events',
        sa.Column(
            'error',
            sa.String(500),
            nullable=True,
            comment="Last error message if processing failed"
        )
    )
    
    # Create index on processed_at for efficient querying of unprocessed events
    op.create_index(
        'ix_estimate_event_processed_at',
        'estimate_events',
        ['processed_at'],
        postgresql_ops={'processed_at': 'DESC'}
    )
    
    # Create index on (processed_at, retry_count) for identifying failed events to retry
    op.create_index(
        'ix_estimate_event_unprocessed',
        'estimate_events',
        ['processed_at', 'retry_count'],
        postgresql_where=sa.text("processed_at IS NULL")
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_estimate_event_unprocessed', table_name='estimate_events')
    op.drop_index('ix_estimate_event_processed_at', table_name='estimate_events')
    
    # Drop columns
    op.drop_column('estimate_events', 'error')
    op.drop_column('estimate_events', 'retry_count')
    op.drop_column('estimate_events', 'processed_at')
