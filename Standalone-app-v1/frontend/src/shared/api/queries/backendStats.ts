import { useQuery } from '@tanstack/react-query'
import apiClient from '@/shared/api/client'
import { unwrapResponse, type ApiResponse } from '@/shared/types'

export interface BackendStats {
  open_estimates: number
  auto_closed_estimates: number
  synced_market_rows: number
  backend_jobs_active: boolean
}

export async function fetchBackendStats(): Promise<BackendStats> {
  const { data } = await apiClient.get<ApiResponse<BackendStats>>('/api/estimates/statistics/backend-check')
  return unwrapResponse(data)
}

export function useBackendStats() {
  return useQuery({
    queryKey: ['backend-stats'],
    queryFn: fetchBackendStats,
    refetchInterval: 60000, // Refetch every 1 minute to stay up to date
  })
}
