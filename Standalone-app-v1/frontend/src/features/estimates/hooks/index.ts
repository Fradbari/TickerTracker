/**
 * Estimates feature — TanStack Query hooks (public re-export barrel).
 *
 * The canonical hook implementations live in the API layer for discoverability:
 *   features/estimates/api/queries.ts   ← read hooks + estimateKeys
 *   features/estimates/api/mutations.ts ← write hooks
 *
 * This file re-exports everything under a stable import path:
 *   import { useEstimates, useCloseEstimate } from '@/features/estimates/hooks'
 *
 * ESTIMATE_KEYS is aliased from estimateKeys for backward compatibility with
 * any early code that references the uppercase name.
 */

import { useInfiniteQuery } from '@tanstack/react-query'
import { listEstimates } from '../api'
import { estimateKeys } from '../api/queries'
import type { EstimateListParams } from '../types'

// ---------------------------------------------------------------------------
// Re-export read hooks + key factory
// ---------------------------------------------------------------------------

export {
  estimateKeys,
  /** @deprecated Use estimateKeys (camelCase) — kept for backward compat. */
  estimateKeys as ESTIMATE_KEYS,
  useEstimates,
  /** @deprecated Use useEstimates — renamed for consistency. */
  useEstimates as useEstimateList,
  useEstimate,
  useEstimateHistory,
} from '../api/queries'

// ---------------------------------------------------------------------------
// Re-export write hooks
// ---------------------------------------------------------------------------

export {
  useCreateEstimate,
  useCloseEstimate,
  useDeleteEstimate,
  useUpdateEstimate,
} from '../api/mutations'

// ---------------------------------------------------------------------------
// Infinite-scroll variant (extends the list hook with cursor pagination)
// ---------------------------------------------------------------------------

/**
 * Infinite-scroll list of estimates using TanStack Query's `useInfiniteQuery`.
 *
 * Each page is fetched by forwarding the `next_cursor` token returned by the
 * previous page. Use this hook in components that render a virtualised list
 * or a "Load more" button.
 *
 * @param params - Optional filters (same as `useEstimates`), excluding `cursor`
 *                 which is managed internally by the hook.
 *
 * @example
 * const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
 *   useInfiniteEstimates({ status: 'OPEN' })
 *
 * // Flatten pages for rendering:
 * const estimates = data?.pages.flatMap(p => p.items) ?? []
 */
export function useInfiniteEstimates(
  params?: Omit<EstimateListParams, 'cursor'>,
) {
  return useInfiniteQuery({
    queryKey: estimateKeys.list(params as EstimateListParams | undefined),
    queryFn: ({ pageParam }) =>
      listEstimates({ ...params, cursor: pageParam as string | undefined }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) =>
      lastPage.page_info.has_next_page
        ? (lastPage.page_info.next_cursor ?? undefined)
        : undefined,
  })
}
