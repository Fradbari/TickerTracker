/**
 * Estimates feature — TanStack Query read-hooks.
 *
 * Exports:
 *   estimateKeys  — stable query-key factory for caching and invalidation
 *   useEstimates  — paginated list of estimates (with filters)
 *   useEstimate   — single estimate by id
 *   useEstimateHistory — audit trail for an estimate
 *
 * Components should import these hooks (or via @/features/estimates),
 * never calling the HTTP functions from api/index.ts directly.
 *
 * Cache strategy:
 *   estimateKeys.all is used as the root key; invalidating it busts every
 *   list, detail, and history query at once after a mutation.
 */

import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { listEstimates, getEstimate, getEstimateHistory } from './index'
import type { EstimateListParams } from '../types'

// ---------------------------------------------------------------------------
// Query-key factory
// ---------------------------------------------------------------------------

/**
 * Stable query-key factory for all estimate-related queries.
 *
 * Hierarchy:
 *   estimateKeys.all                → root — invalidates everything
 *   estimateKeys.list(params)      → paginated list, scoped by filter params
 *   estimateKeys.detail(id)        → single estimate
 *   estimateKeys.history(id)       → audit trail
 *
 * @example
 * // Invalidate all estimate caches after a mutation:
 * queryClient.invalidateQueries({ queryKey: estimateKeys.all })
 *
 * // Scope invalidation to a specific estimate:
 * queryClient.invalidateQueries({ queryKey: estimateKeys.detail(id) })
 */
export const estimateKeys = {
  all: ['estimates'] as const,
  list: (params?: EstimateListParams) =>
    [...estimateKeys.all, 'list', params ?? {}] as const,
  detail: (id: string) => [...estimateKeys.all, 'detail', id] as const,
  history: (id: string) => [...estimateKeys.all, 'history', id] as const,
} as const

// ---------------------------------------------------------------------------
// Read hooks
// ---------------------------------------------------------------------------

/**
 * Fetch a paginated / filtered list of estimates.
 *
 * The full filter object is encoded into the query key so React Query caches
 * each distinct filter combination independently.
 *
 * @param filters - Optional {@link EstimateListParams}. Pass `undefined` to
 *                  fetch all estimates with default server-side pagination.
 *
 * @example
 * const { data, isLoading, isError } = useEstimates({ status: 'OPEN' })
 * data?.items.forEach(e => console.log(e.ticker_id, e.direction))
 */
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

/**
 * Fetch a single estimate by UUID.
 *
 * The query is disabled automatically when `id` is an empty string so
 * components can call the hook unconditionally before the id is known.
 *
 * @param id - UUID of the estimate to fetch.
 *
 * @example
 * const { data: estimate, isLoading } = useEstimate(estimateId)
 */
export function useEstimate(id: string) {
  return useQuery({
    queryKey: estimateKeys.detail(id),
    queryFn: () => getEstimate(id),
    enabled: Boolean(id),
  })
}

/**
 * Fetch the audit trail (history) for an estimate.
 *
 * The backend endpoint is `GET /api/estimates/:id/history`.
 * Return type is `unknown` because the response schema is not yet formalised
 * in the frontend types — use with caution and add a type guard when consumed.
 *
 * TODO (TASK 4.7+): Narrow the `unknown` type once HistoryEntry schema is
 *   added to `features/estimates/types/index.ts`.
 *
 * @param id - UUID of the estimate.
 *
 * @example
 * const { data: history, isLoading } = useEstimateHistory(estimateId)
 */
export function useEstimateHistory(id: string) {
  return useQuery<unknown>({
    queryKey: estimateKeys.history(id),
    queryFn: () => getEstimateHistory(id),
    enabled: Boolean(id),
  })
}

export function useInfiniteEstimates(filters?: EstimateListParams, limit = 20) {
  return useInfiniteQuery({
    queryKey: [...estimateKeys.list(filters), 'infinite'],
    queryFn: ({ pageParam }) => listEstimates({ ...filters, limit, cursor: pageParam }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.page_info.next_cursor ?? undefined,
  })
}

