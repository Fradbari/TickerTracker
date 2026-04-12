/**
 * Estimate feature — TypeScript types.
 *
 * Mirrors the backend Pydantic schemas:
 *   backend/src/estimates/schemas/responses.py  → EstimateResponse, EstimateListResponse
 *   backend/src/estimates/schemas/commands.py   → CreateEstimateCommand, CloseEstimateCommand
 *   backend/src/estimates/schemas/filters.py    → EstimateFilters
 */

import type {
  EstimateDirection,
  EstimateStatus,
  Estimate,
  PageInfo,
  EstimateListResponse,
  EstimateListParams
} from '@/shared/types'

export type {
  EstimateDirection,
  EstimateStatus,
  Estimate,
  PageInfo,
  EstimateListResponse,
  EstimateListParams
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

/** Matches backend TaskStatusResponse. */
export interface TaskStatusResponse {
  task_id: string
  status: 'Pending' | 'Processing' | 'Completed' | 'Failed'
  created_at: string
  updated_at: string
  error?: string | null
  estimate?: Estimate | null
}

/** Matches backend EstimateCreatedResponse but adapted for async 202 */
export interface AsyncCreateEstimateResponse {
  message: string
  task_id: string
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

 
