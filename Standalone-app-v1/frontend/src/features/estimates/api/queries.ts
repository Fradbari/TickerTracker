/**
 * Estimates feature — TanStack Query read-hooks.
 *
 * Exports:
 *   estimateKeys  — stable query-key factory for caching and invalidation
 *   useEstimates  — paginated list of estimates (with filters)
 *   useEstimate   — single estimate by id
 *   useEstimateHistory — audit trail for an estimate
 */

import { useQuery } from '@tanstack/react-query'
import { getEstimate, getEstimateHistory } from './index'

export { estimateKeys, useEstimates, useInfiniteEstimates } from '@/shared/api/queries/estimates'
import { estimateKeys } from '@/shared/api/queries/estimates'

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
// useEstimates moved to shared

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

// useInfiniteEstimates moved to shared

