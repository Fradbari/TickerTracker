/**
 * Market-data feature — TypeScript types.
 *
 * Aligned with backend MarketDataRow schema
 * (backend/src/market_data/schemas/market_data_schemas.py).
 */

// ---------------------------------------------------------------------------
// Quote (real-time / delayed snapshot)
// ---------------------------------------------------------------------------

export interface MarketQuote {
  ticker: string
  price: string          // current (close) price — Decimal-safe string
  change: string         // absolute change from previous close
  change_percent: string // e.g. "1.32" = +1.32 %
  volume: number | null
  high: string | null    // day high
  low: string | null     // day low
  open: string | null    // day open
  timestamp: string      // ISO 8601
  source: string         // "yahoo" | "manual" | …
  quality_score: string  // 0.00–1.00
}

// ---------------------------------------------------------------------------
// Historical OHLCV bar (matches MarketDataRow)
// ---------------------------------------------------------------------------

export interface OHLCVBar {
  date: string          // "YYYY-MM-DD"
  open: string
  high: string
  low: string
  close: string
  volume: number
  data_source: string
  quality_score: string
}

// ---------------------------------------------------------------------------
// Query params
// ---------------------------------------------------------------------------

export interface MarketQuoteParams {
  /** One or more ticker symbols, e.g. ["AAPL", "MSFT"]. */
  tickers: string[]
}

export interface HistoricalDataParams {
  ticker: string
  start_date?: string   // "YYYY-MM-DD"
  end_date?: string
  limit?: number
}
