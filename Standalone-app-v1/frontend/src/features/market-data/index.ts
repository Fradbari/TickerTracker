/**
 * Market-data feature — public API.
 *
 * @example
 *   import { useMarketQuote, type MarketQuote } from '@/features/market-data'
 */

export type {
  MarketQuote,
  OHLCVBar,
  MarketQuoteParams,
  HistoricalDataParams,
} from './types'

export {
  getQuotes,
  getQuote,
  getHistoricalData,
} from './api'

export {
  MARKET_DATA_KEYS,
  useMarketQuotes,
  useMarketQuote,
  useHistoricalData,
} from './hooks'

// export * from './components'  // TASK 4.9, 4.13, 4.14
