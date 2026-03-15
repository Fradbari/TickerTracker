export type EstimateDirection = 'LONG' | 'SHORT'

export type EstimateStatus =
  | 'OPEN'
  | 'CLOSED_WIN'
  | 'CLOSED_LOSS'
  | 'CLOSED_NEUTRAL'

export interface Estimate {
  id: string
  ticker_id: string
  user_id: string | null
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
  created_at: string
  updated_at: string
  closed_at: string | null
  is_deleted: boolean
}

export interface PageInfo {
  has_next_page: boolean
  has_previous_page: boolean
  next_cursor: string | null
  previous_cursor: string | null
}

export interface EstimateListResponse {
  items: Estimate[]
  total: number
  page_info: PageInfo
}

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
