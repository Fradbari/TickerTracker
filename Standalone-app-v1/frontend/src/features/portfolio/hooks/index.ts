export * from './usePortfolioMetrics'

import { useQuery } from '@tanstack/react-query'
import { getPortfolioSummary, getOpenPositions, getPerformanceByPeriod } from '../api'

export const PORTFOLIO_KEYS = {
  all: ['portfolio'] as const,
  summary: () => [...PORTFOLIO_KEYS.all, 'summary'] as const,
  positions: () => [...PORTFOLIO_KEYS.all, 'positions'] as const,
  performance: (granularity: string) =>
    [...PORTFOLIO_KEYS.all, 'performance', granularity] as const,
} as const

/** Aggregate portfolio summary */
export function usePortfolioSummary() {
  return useQuery({
    queryKey: PORTFOLIO_KEYS.summary(),
    queryFn: getPortfolioSummary,
    staleTime: 5 * 60 * 1_000,
  })
}

export function useOpenPositions() {
  return useQuery({
    queryKey: PORTFOLIO_KEYS.positions(),
    queryFn: getOpenPositions,
    staleTime: 60 * 1_000,
  })
}

export function usePerformanceByPeriod(
  granularity: 'week' | 'month' | 'year' = 'month',
) {
  return useQuery({
    queryKey: PORTFOLIO_KEYS.performance(granularity),
    queryFn: () => getPerformanceByPeriod(granularity),
    staleTime: 10 * 60 * 1_000,
  })
}
