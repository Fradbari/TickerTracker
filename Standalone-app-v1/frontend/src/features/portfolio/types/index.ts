/**
 * Portfolio feature — TypeScript types.
 *
 * Portfolio views are aggregations derived from the estimates domain.
 * Backend routes will be defined in a future task (analytics module).
 */

// ---------------------------------------------------------------------------
// Portfolio summary (overall view)
// ---------------------------------------------------------------------------

export interface PortfolioSummary {
  /** Total capital invested across all OPEN estimates (string = Decimal precision). */
  total_invested: string
  /** Current market value of open positions. */
  current_value: string
  /** Total realised PnL from CLOSED estimates. */
  total_realized_pnl: string
  /** Total unrealised PnL from OPEN estimates. */
  total_unrealized_pnl: string
  /** Win rate as a decimal string, e.g. "0.65" = 65 %. Null if no closed trades. */
  win_rate: string | null
  /** Number of currently OPEN estimates. */
  open_count: number
  /** Total number of CLOSED estimates (win + loss + neutral). */
  closed_count: number
  /** Currency of the portfolio (default "USD"). */
  currency: string
}

// ---------------------------------------------------------------------------
// Individual position (one row in the portfolio table)
// ---------------------------------------------------------------------------

export interface PortfolioPosition {
  estimate_id: string   // UUID
  ticker_id: string     // UUID
  ticker_symbol: string
  direction: 'LONG' | 'SHORT'
  start_price: string
  target_price: string
  stop_loss_price: string
  current_price: string | null
  unrealized_pnl: string | null
  unrealized_pnl_percent: string | null
  target_profit_percent: string
  stop_loss_percent: string
  created_at: string
}

// ---------------------------------------------------------------------------
// Performance breakdown
// ---------------------------------------------------------------------------

export interface PerformanceByPeriod {
  period: string   // "2026-W09" | "2026-03" | "2026"
  realized_pnl: string
  closed_count: number
  win_count: number
  loss_count: number
}
