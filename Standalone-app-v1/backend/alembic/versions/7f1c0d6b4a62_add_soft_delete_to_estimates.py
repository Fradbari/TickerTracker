"""Add soft delete fields to estimates

Revision ID: 7f1c0d6b4a62
Revises: e97b3b8578e1
Create Date: 2026-02-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f1c0d6b4a62"
down_revision: Union[str, None] = "e97b3b8578e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "estimates",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "estimates",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_estimate_is_deleted", "estimates", ["is_deleted"], unique=False)

    op.execute("DROP MATERIALIZED VIEW IF EXISTS estimate_summary_view;")
    op.execute(
        """
        CREATE MATERIALIZED VIEW estimate_summary_view AS
        SELECT
            -- All fields from estimates table
            e.id,
            e.ticker_id,
            e.user_id,
            e.start_price,
            e.target_price,
            e.stop_loss_price,
            e.target_profit_percent,
            e.stop_loss_percent,
            e.status,
            e.direction,
            e.ai_model,
            e.ai_confidence,
            e.ai_reasoning,
            e.created_at,
            e.updated_at,
            e.closed_at,
            e.exit_price,
            e.realized_pnl,

            -- Current price from latest market_data
            COALESCE(md.close, e.start_price) AS current_price,

            -- Current unrealized PnL (only for open estimates)
            CASE
                WHEN e.status = 'OPEN' THEN
                    CASE
                        WHEN e.direction = 'LONG' THEN
                            (COALESCE(md.close, e.start_price) - e.start_price) * 100
                        WHEN e.direction = 'SHORT' THEN
                            (e.start_price - COALESCE(md.close, e.start_price)) * 100
                        ELSE 0
                    END
                ELSE e.realized_pnl
            END AS current_pnl,

            -- Current PnL percentage
            CASE
                WHEN e.status = 'OPEN' THEN
                    CASE
                        WHEN e.direction = 'LONG' THEN
                            ((COALESCE(md.close, e.start_price) - e.start_price) / e.start_price) * 100
                        WHEN e.direction = 'SHORT' THEN
                            ((e.start_price - COALESCE(md.close, e.start_price)) / e.start_price) * 100
                        ELSE 0
                    END
                ELSE
                    CASE
                        WHEN e.realized_pnl IS NOT NULL AND e.start_price > 0 THEN
                            (e.realized_pnl / (e.start_price * 100)) * 100
                        ELSE 0
                    END
            END AS current_pnl_percent,

            -- Days since estimate was opened
            CASE
                WHEN e.status = 'OPEN' THEN
                    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - e.created_at))::INTEGER
                ELSE
                    EXTRACT(DAY FROM (COALESCE(e.closed_at, e.updated_at) - e.created_at))::INTEGER
            END AS days_open,

            -- Risk level based on stop_loss_percent
            CASE
                WHEN e.stop_loss_percent <= 2.0 THEN 'LOW'
                WHEN e.stop_loss_percent <= 5.0 THEN 'MEDIUM'
                ELSE 'HIGH'
            END AS risk_level

        FROM estimates e
        LEFT JOIN LATERAL (
            SELECT close
            FROM market_data md_inner
            WHERE md_inner.ticker_id = e.ticker_id
            ORDER BY md_inner.date DESC
            LIMIT 1
        ) md ON true
        WHERE e.is_deleted = false;
        """
    )

    op.execute(
        """
        CREATE UNIQUE INDEX ix_estimate_summary_view_id
        ON estimate_summary_view (id);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_estimate_summary_view_status
        ON estimate_summary_view (status);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_estimate_summary_view_ticker_id
        ON estimate_summary_view (ticker_id);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_estimate_summary_view_status_created_at
        ON estimate_summary_view (status, created_at DESC);
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS estimate_summary_view;")

    op.drop_index("ix_estimate_is_deleted", table_name="estimates")
    op.drop_column("estimates", "deleted_at")
    op.drop_column("estimates", "is_deleted")

    op.execute(
        """
        CREATE MATERIALIZED VIEW estimate_summary_view AS
        SELECT
            -- All fields from estimates table
            e.id,
            e.ticker_id,
            e.user_id,
            e.start_price,
            e.target_price,
            e.stop_loss_price,
            e.target_profit_percent,
            e.stop_loss_percent,
            e.status,
            e.direction,
            e.ai_model,
            e.ai_confidence,
            e.ai_reasoning,
            e.created_at,
            e.updated_at,
            e.closed_at,
            e.exit_price,
            e.realized_pnl,

            -- Current price from latest market_data
            COALESCE(md.close, e.start_price) AS current_price,

            -- Current unrealized PnL (only for open estimates)
            CASE
                WHEN e.status = 'OPEN' THEN
                    CASE
                        WHEN e.direction = 'LONG' THEN
                            (COALESCE(md.close, e.start_price) - e.start_price) * 100
                        WHEN e.direction = 'SHORT' THEN
                            (e.start_price - COALESCE(md.close, e.start_price)) * 100
                        ELSE 0
                    END
                ELSE e.realized_pnl
            END AS current_pnl,

            -- Current PnL percentage
            CASE
                WHEN e.status = 'OPEN' THEN
                    CASE
                        WHEN e.direction = 'LONG' THEN
                            ((COALESCE(md.close, e.start_price) - e.start_price) / e.start_price) * 100
                        WHEN e.direction = 'SHORT' THEN
                            ((e.start_price - COALESCE(md.close, e.start_price)) / e.start_price) * 100
                        ELSE 0
                    END
                ELSE
                    CASE
                        WHEN e.realized_pnl IS NOT NULL AND e.start_price > 0 THEN
                            (e.realized_pnl / (e.start_price * 100)) * 100
                        ELSE 0
                    END
            END AS current_pnl_percent,

            -- Days since estimate was opened
            CASE
                WHEN e.status = 'OPEN' THEN
                    EXTRACT(DAY FROM (CURRENT_TIMESTAMP - e.created_at))::INTEGER
                ELSE
                    EXTRACT(DAY FROM (COALESCE(e.closed_at, e.updated_at) - e.created_at))::INTEGER
            END AS days_open,

            -- Risk level based on stop_loss_percent
            CASE
                WHEN e.stop_loss_percent <= 2.0 THEN 'LOW'
                WHEN e.stop_loss_percent <= 5.0 THEN 'MEDIUM'
                ELSE 'HIGH'
            END AS risk_level

        FROM estimates e
        LEFT JOIN LATERAL (
            SELECT close
            FROM market_data md_inner
            WHERE md_inner.ticker_id = e.ticker_id
            ORDER BY md_inner.date DESC
            LIMIT 1
        ) md ON true;
        """
    )

    op.execute(
        """
        CREATE UNIQUE INDEX ix_estimate_summary_view_id
        ON estimate_summary_view (id);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_estimate_summary_view_status
        ON estimate_summary_view (status);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_estimate_summary_view_ticker_id
        ON estimate_summary_view (ticker_id);
        """
    )
    op.execute(
        """
        CREATE INDEX ix_estimate_summary_view_status_created_at
        ON estimate_summary_view (status, created_at DESC);
        """
    )
