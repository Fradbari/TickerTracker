"""Create estimate_summary_view materialized view

Revision ID: e97b3b8578e1
Revises: f9f513c6220d
Create Date: 2026-02-07 19:34:32.314448

This migration creates a materialized view for optimized dashboard queries (CQRS pattern).
The view combines Estimate data with current market prices and computed metrics:
- current_price: Latest closing price from market_data
- current_pnl: Calculated unrealized P&L based on direction
- current_pnl_percent: P&L as percentage
- days_open: Days since estimate creation
- risk_level: Risk categorization (LOW/MEDIUM/HIGH)

The materialized view supports concurrent refresh via a unique index on (id).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e97b3b8578e1'
down_revision: Union[str, None] = 'f9f513c6220d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the materialized view
    op.execute("""
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
    """)
    
    # Create unique index on id (required for CONCURRENT refresh)
    op.execute("""
        CREATE UNIQUE INDEX ix_estimate_summary_view_id
        ON estimate_summary_view (id);
    """)
    
    # Create index on status for filtering open/closed estimates
    op.execute("""
        CREATE INDEX ix_estimate_summary_view_status
        ON estimate_summary_view (status);
    """)
    
    # Create index on ticker_id for filtering by ticker
    op.execute("""
        CREATE INDEX ix_estimate_summary_view_ticker_id
        ON estimate_summary_view (ticker_id);
    """)
    
    # Create composite index on status and created_at for sorting
    op.execute("""
        CREATE INDEX ix_estimate_summary_view_status_created_at
        ON estimate_summary_view (status, created_at DESC);
    """)


def downgrade() -> None:
    # Drop the materialized view (indexes are dropped automatically)
    op.execute("DROP MATERIALIZED VIEW IF EXISTS estimate_summary_view;")

