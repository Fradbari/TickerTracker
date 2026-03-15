import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import type { EstimateListParams, EstimateListResponse } from '@/shared/types'
import apiClient from '@/shared/api/client'
import { unwrapResponse, type ApiResponse } from '@/shared/types'

const BASE = '/api/estimates'

export async function listEstimates(
  params?: EstimateListParams,
): Promise<EstimateListResponse> {
  const { data } = await apiClient.get<ApiResponse<EstimateListResponse>>(
    BASE,
    { params },
  )
  return unwrapResponse(data)
}

export const estimateKeys = {
  all: ['estimates'] as const,
  list: (params?: EstimateListParams) =>
    [...estimateKeys.all, 'list', params ?? {}] as const,
  detail: (id: string) => [...estimateKeys.all, 'detail', id] as const,
  history: (id: string) => [...estimateKeys.all, 'history', id] as const,
} as const

export function useEstimates(
  filters?: EstimateListParams,
  options?: Omit<Parameters<typeof useQuery>[0], 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: estimateKeys.list(filters),
    queryFn: () => listEstimates(filters),
    ...options,
  })
}

export function useInfiniteEstimates(filters?: EstimateListParams, limit = 20) {
  return useInfiniteQuery({
    queryKey: [...estimateKeys.list(filters), 'infinite'],
    queryFn: ({ pageParam }) => listEstimates({ ...filters, limit, cursor: typeof pageParam === 'string' ? pageParam : undefined }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.page_info.next_cursor ?? undefined,
  })
}
