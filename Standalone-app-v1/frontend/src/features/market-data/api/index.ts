/**
 * Market-data feature — API layer.
 *
 * Calls the market-data router (TASK 2.17) to retrieve quotes and history.
 */
import apiClient from '@/shared/api/client'
import { unwrapResponse } from '@/shared/types'
import type { ApiResponse } from '@/shared/types'
import type { MarketQuote, OHLCVBar, HistoricalDataParams } from '../types'

const BASE = '/api/market-data'

/**
 * Get the latest quote for one or more tickers.
 * Backend fetches from Yahoo Finance (with caching + circuit-breaker).
 */
export async function getQuotes(tickers: string[]): Promise<MarketQuote[]> {
  const { data } = await apiClient.get<ApiResponse<MarketQuote[]>>(`${BASE}/quotes`, {
    params: { tickers: tickers.join(',') },
  })
  return unwrapResponse(data)
}

/** Get the latest quote for a single ticker. */
export async function getQuote(ticker: string): Promise<MarketQuote> {
  const { data } = await apiClient.get<ApiResponse<MarketQuote>>(
    `${BASE}/quotes/${ticker}`,
  )
  return unwrapResponse(data)
}

/**
 * Retrieve OHLCV history for a ticker.
 * Results are sorted ascending by date.
 */
export async function getHistoricalData(
  params: HistoricalDataParams,
): Promise<OHLCVBar[]> {
  const { ticker, ...rest } = params
  const { data } = await apiClient.get<ApiResponse<OHLCVBar[]>>(
    `${BASE}/history/${ticker}`,
    { params: rest },
  )
  return unwrapResponse(data)
}
