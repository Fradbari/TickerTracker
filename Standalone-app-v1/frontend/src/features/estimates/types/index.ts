/**
 * Estimate feature — TypeScript types.
 *
 * Mirrors the backend Pydantic schemas:
 *   backend/src/estimates/schemas/responses.py  → EstimateResponse, EstimateListResponse
 *   backend/src/estimates/schemas/commands.py   → CreateEstimateCommand, CloseEstimateCommand
 *   backend/src/estimates/schemas/filters.py    → EstimateFilters
 */

// ---------------------------------------------------------------------------
// Domain enums
// ---------------------------------------------------------------------------

export type EstimateDirection = 'LONG' | 'SHORT'

/**
 * OPEN          — Active, not yet closed
 * CLOSED_WIN    — Closed at profit (exit_price >= target_price)
 * CLOSED_LOSS   — Closed at loss (exit_price <= stop_loss_price)
 * CLOSED_NEUTRAL — Closed manually without clear win/loss
 */
export type EstimateStatus =
  | 'OPEN'
  | 'CLOSED_WIN'
  | 'CLOSED_LOSS'
  | 'CLOSED_NEUTRAL'

// ---------------------------------------------------------------------------
// Response types (read models)
// ---------------------------------------------------------------------------

/**
 * Single estimate — matches backend EstimateResponse.
 * All price/percent fields are serialised as strings to preserve Decimal precision.
 */
export interface Estimate {
  id: string               // UUID
  ticker_id: string        // UUID
  user_id: string | null   // UUID or null
  direction: EstimateDirection
  status: EstimateStatus
  start_price: string
  target_price: string
  stop_loss_price: string
  target_profit_percent: string
  stop_loss_percent: string
  exit_price: string | null
  realized_pnl: string | null
  ai_model: string | null
  ai_confidence: string | null
  ai_reasoning: string | null
  created_at: string       // ISO 8601
  updated_at: string
  closed_at: string | null
  is_deleted: boolean
}

/** Cursor-based pagination info — matches backend page_info dict. */
export interface PageInfo {
  has_next_page: boolean
  has_previous_page: boolean
  next_cursor: string | null
  previous_cursor: string | null
}

/** Matches backend EstimateListResponse. */
export interface EstimateListResponse {
  items: Estimate[]
  total: number
  page_info: PageInfo
}

/** Matches backend EstimateCreatedResponse. */
export interface EstimateCreatedResponse {
  estimate: Estimate
  message: string
}

/** Matches backend EstimateUpdatedResponse. */
export interface EstimateUpdatedResponse {
  estimate: Estimate
  message: string
}

/** Matches backend EstimateDeletedResponse. */
export interface EstimateDeletedResponse {
  id: string
  status: string
  message: string
}

// ---------------------------------------------------------------------------
// Command types (write models)
// ---------------------------------------------------------------------------

/**
 * Matches backend CreateEstimateCommand.
 * start_price / target_price / stop_loss_price are derived server-side from
 * current market price + percentage inputs.
 */
export interface CreateEstimatePayload {
  ticker_id: string
  direction: EstimateDirection
  target_profit_percent: string  // e.g. "15.0" for 15 %
  stop_loss_percent: string      // e.g. "5.0"  for 5 %
  user_id?: string
  ai_model?: string
  ai_confidence?: string
  ai_reasoning?: string
}

/** Matches backend CloseEstimateCommand. */
export interface CloseEstimatePayload {
  exit_price: string
  notes?: string
}

// ---------------------------------------------------------------------------
// Query / filter types
// ---------------------------------------------------------------------------

/** Mirrors backend EstimateFilters + cursor pagination params. */
export interface EstimateListParams {
  ticker_id?: string
  user_id?: string
  status?: EstimateStatus
  direction?: EstimateDirection
  created_after?: string
  created_before?: string
  closed_after?: string
  closed_before?: string
  min_confidence?: number
  max_confidence?: number
  include_deleted?: boolean
  cursor?: string
  limit?: number
}
