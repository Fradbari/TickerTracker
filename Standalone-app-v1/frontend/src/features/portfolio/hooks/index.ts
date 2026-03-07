/**
 * Portfolio feature — TanStack Query hooks.
 */
import { useQuery } from '@tanstack/react-query'
import { getPortfolioSummary, getOpenPositions, getPerformanceByPeriod } from '../api'

export const PORTFOLIO_KEYS = {
  all: ['portfolio'] as const,
  summary: () => [...PORTFOLIO_KEYS.all, 'summary'] as const,
  positions: () => [...PORTFOLIO_KEYS.all, 'positions'] as const,
  performance: (granularity: string) =>
    [...PORTFOLIO_KEYS.all, 'performance', granularity] as const,
} as const

/** Aggregate portfolio summary — total invested, win rate, open/closed counts. */
export function usePortfolioSummary() {
  return useQuery({
    queryKey: PORTFOLIO_KEYS.summary(),
    queryFn: getPortfolioSummary,
    // Refresh every 5 minutes (prices change slowly for position-level summary)
    staleTime: 5 * 60 * 1_000,
  })
}

/** All open positions enriched with current prices and unrealised PnL. */
export function useOpenPositions() {
  return useQuery({
    queryKey: PORTFOLIO_KEYS.positions(),
    queryFn: getOpenPositions,
    staleTime: 60 * 1_000, // 1-minute freshness for price-sensitive data
  })
}

/**
 * Historical performance broken down by period.
 * @param granularity 'week' | 'month' | 'year' (default 'month')
 */
export function usePerformanceByPeriod(
  granularity: 'week' | 'month' | 'year' = 'month',
) {
  return useQuery({
    queryKey: PORTFOLIO_KEYS.performance(granularity),
    queryFn: () => getPerformanceByPeriod(granularity),
    staleTime: 10 * 60 * 1_000,
  })
}
