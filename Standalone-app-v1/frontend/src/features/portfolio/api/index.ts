/**
 * Portfolio feature — API layer.
 *
 * Portfolio data is derived from estimates + market data on the backend.
 * Endpoints will be added to the analytics router (TASK 2.27).
 */
import apiClient from '@/shared/api/client'
import { unwrapResponse } from '@/shared/types'
import type { ApiResponse } from '@/shared/types'
import type { PortfolioSummary, PortfolioPosition, PerformanceByPeriod } from '../types'

const BASE = '/api/portfolio'

/** Aggregate portfolio summary (totals, win-rate, open/closed counts). */
export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const { data } = await apiClient.get<ApiResponse<PortfolioSummary>>(`${BASE}/summary`)
  return unwrapResponse(data)
}

/** All open positions with current prices and unrealised PnL. */
export async function getOpenPositions(): Promise<PortfolioPosition[]> {
  const { data } = await apiClient.get<ApiResponse<PortfolioPosition[]>>(`${BASE}/positions`)
  return unwrapResponse(data)
}

/** Performance breakdown by calendar period (week / month / year). */
export async function getPerformanceByPeriod(
  granularity: 'week' | 'month' | 'year' = 'month',
): Promise<PerformanceByPeriod[]> {
  const { data } = await apiClient.get<ApiResponse<PerformanceByPeriod[]>>(
    `${BASE}/performance`,
    { params: { granularity } },
  )
  return unwrapResponse(data)
}
