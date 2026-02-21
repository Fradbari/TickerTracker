"""Add lineage source_timestamp; rename ingested_at to ingestion_timestamp

Revision ID: a3b5c7d9e1f0
Revises: 1ff98aa47c0c
Create Date: 2026-02-21 12:00:00.000000

Offline-only migration: run with 'alembic upgrade head'

This migration implements TASK 3.9 — Data Lineage Tracking schema changes
on the ``market_data`` table:

1. Renames column ``ingested_at`` → ``ingestion_timestamp`` to align with
   the ``LineageTracked`` SQLAlchemy mixin.
2. Adds column ``source_timestamp`` (TIMESTAMPTZ, nullable) to record when
   data was generated at the external source.

Note
----
- ``data_source`` and ``quality_score`` already exist — no DDL change needed.
- No data UPDATE statements are included.  Existing rows keep their current
  values for ``data_source`` and ``quality_score``; ``ingestion_timestamp``
  retains the values previously stored in ``ingested_at``.
- To apply: ``alembic upgrade head``
- To rollback: ``alembic downgrade -1``
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3b5c7d9e1f0"
down_revision: Union[str, None] = "1ff98aa47c0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename ingested_at → ingestion_timestamp
    op.alter_column(
        "market_data",
        "ingested_at",
        new_column_name="ingestion_timestamp",
    )

    # 2. Add source_timestamp (nullable — historical rows have no source ts)
    op.add_column(
        "market_data",
        sa.Column(
            "source_timestamp",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    # Remove source_timestamp
    op.drop_column("market_data", "source_timestamp")

    # Rename ingestion_timestamp back to ingested_at
    op.alter_column(
        "market_data",
        "ingestion_timestamp",
        new_column_name="ingested_at",
    )
