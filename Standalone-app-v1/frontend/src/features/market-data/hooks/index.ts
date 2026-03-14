/**
 * Market-data feature — TanStack Query hooks.
 *
 * Quotes are refreshed frequently (configurable staleTime).
 * Historical OHLCV data is considered stable and cached for longer.
 */
import { useQuery } from '@tanstack/react-query'
import { getQuotes, getQuote, getHistoricalData } from '../api'
import type { HistoricalDataParams } from '../types'

export const MARKET_DATA_KEYS = {
  all: ['market-data'] as const,
  quotes: (tickers: string[]) =>
    [...MARKET_DATA_KEYS.all, 'quotes', tickers.slice().sort()] as const,
  quote: (ticker: string) =>
    [...MARKET_DATA_KEYS.all, 'quote', ticker.toUpperCase()] as const,
  history: (params: HistoricalDataParams) =>
    [...MARKET_DATA_KEYS.all, 'history', params] as const,
} as const

/**
 * Fetch live quotes for multiple tickers.
 * Refreshes every 60 seconds by default (Yahoo Finance rate-limited).
 */
export function useMarketQuotes(tickers: string[]) {
  return useQuery({
    queryKey: MARKET_DATA_KEYS.quotes(tickers),
    queryFn: () => getQuotes(tickers),
    enabled: tickers.length > 0,
    staleTime: 60 * 1_000,
    refetchInterval: 60 * 1_000,
  })
}

/** Fetch the latest quote for a single ticker. */
export function useMarketQuote(ticker: string) {
  return useQuery({
    queryKey: MARKET_DATA_KEYS.quote(ticker),
    queryFn: () => getQuote(ticker),
    enabled: Boolean(ticker),
    staleTime: 60 * 1_000,
    refetchInterval: 60 * 1_000,
  })
}

/**
 * Fetch OHLCV history for a ticker.
 * Historical data is stable — cached for 30 minutes.
 */
export function useHistoricalData(params: HistoricalDataParams) {
  return useQuery({
    queryKey: MARKET_DATA_KEYS.history(params),
    queryFn: () => getHistoricalData(params),
    enabled: Boolean(params.ticker),
    staleTime: 30 * 60 * 1_000,
  })
}
export * from './usePriceHistory'
