/**
 * Estimates feature — TanStack Query hooks.
 *
 * All server state is managed here. Components should import these hooks, not
 * call the API layer directly.
 *
 * Cache invalidation strategy:
 *   - Mutations (create / close / delete) invalidate ESTIMATE_KEYS.all
 *   - This triggers a refetch of all active list/detail queries automatically
 */
import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import {
  listEstimates,
  getEstimate,
  createEstimate,
  closeEstimate,
  deleteEstimate,
} from '../api'
import type {
  EstimateListParams,
  CreateEstimatePayload,
  CloseEstimatePayload,
} from '../types'

// ---------------------------------------------------------------------------
// Query-key factory (stable references for cache invalidation)
// ---------------------------------------------------------------------------

export const ESTIMATE_KEYS = {
  /** Invalidate this to bust all estimate caches at once. */
  all: ['estimates'] as const,

  /** List queries (optionally scoped by params). */
  list: (params?: EstimateListParams) =>
    [...ESTIMATE_KEYS.all, 'list', params] as const,

  /** Single-estimate detail query. */
  detail: (id: string) => [...ESTIMATE_KEYS.all, 'detail', id] as const,

  /** Audit trail for an estimate. */
  history: (id: string) => [...ESTIMATE_KEYS.all, 'history', id] as const,
} as const

// ---------------------------------------------------------------------------
// Read hooks
// ---------------------------------------------------------------------------

/**
 * Fetch a paginated list of estimates.
 * Cursor-based pagination is handled by the backend; use `useInfiniteEstimates`
 * for infinite-scroll UI instead.
 */
export function useEstimateList(params?: EstimateListParams) {
  return useQuery({
    queryKey: ESTIMATE_KEYS.list(params),
    queryFn: () => listEstimates(params),
  })
}

/**
 * Infinite-scroll version of useEstimateList.
 * Each page is fetched by forwarding the next_cursor from the previous page.
 */
export function useInfiniteEstimates(
  params?: Omit<EstimateListParams, 'cursor'>,
) {
  return useInfiniteQuery({
    queryKey: ESTIMATE_KEYS.list(params),
    queryFn: ({ pageParam }) =>
      listEstimates({ ...params, cursor: pageParam as string | undefined }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) =>
      lastPage.page_info.has_next_page
        ? (lastPage.page_info.next_cursor ?? undefined)
        : undefined,
  })
}

/** Fetch a single estimate by id. Skips when id is empty. */
export function useEstimate(id: string) {
  return useQuery({
    queryKey: ESTIMATE_KEYS.detail(id),
    queryFn: () => getEstimate(id),
    enabled: Boolean(id),
  })
}

// ---------------------------------------------------------------------------
// Write hooks (mutations)
// ---------------------------------------------------------------------------

/** Create a new estimate. Invalidates the list cache on success. */
export function useCreateEstimate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CreateEstimatePayload) => createEstimate(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ESTIMATE_KEYS.all }),
  })
}

/** Close an estimate with an exit price. Invalidates list + detail caches. */
export function useCloseEstimate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string
      payload: CloseEstimatePayload
    }) => closeEstimate(id, payload),
    onSuccess: (_data, { id }) => {
      qc.invalidateQueries({ queryKey: ESTIMATE_KEYS.all })
      qc.invalidateQueries({ queryKey: ESTIMATE_KEYS.detail(id) })
    },
  })
}

/**
 * Soft-delete an estimate.
 * The backend marks is_deleted = true; include_deleted = true to see them again.
 */
export function useDeleteEstimate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteEstimate(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ESTIMATE_KEYS.all }),
  })
}
