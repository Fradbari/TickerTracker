/**
 * Estimates feature — TanStack Query mutation hooks.
 *
 * Exports:
 *   useCreateEstimate   — POST a new estimate
 *   useCloseEstimate    — PATCH /close an estimate with an exit price
 *   useDeleteEstimate   — DELETE (soft-delete) an estimate
 *   useUpdateEstimate   — placeholder; no generic PATCH endpoint exists yet
 *
 * Cache invalidation:
 *   Every successful mutation calls:
 *     queryClient.invalidateQueries({ queryKey: estimateKeys.all })
 *   which triggers a background refetch of all active estimate queries.
 *   useCloseEstimate additionally invalidates the specific detail cache so
 *   an open EstimateDetail page refreshes immediately.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createEstimate, closeEstimate, deleteEstimate } from './index'
import { estimateKeys } from './queries'
import type { CreateEstimatePayload, CloseEstimatePayload } from '../types'

// ---------------------------------------------------------------------------
// Write hooks
// ---------------------------------------------------------------------------

/**
 * Create a new estimate.
 *
 * Invalidates all estimate caches on success so the caller's list view
 * refreshes automatically.
 *
 * @example
 * const { mutate, isPending, isError } = useCreateEstimate()
 * mutate({ ticker_id, direction, target_profit_percent, stop_loss_percent })
 */
export function useCreateEstimate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CreateEstimatePayload) => createEstimate(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: estimateKeys.all }),
  })
}

/**
 * Close an open estimate by providing an exit price.
 *
 * The backend evaluates the exit price against target / stop-loss and sets
 * the status to CLOSED_WIN, CLOSED_LOSS, or CLOSED_NEUTRAL automatically.
 *
 * Invalidates both the global list cache and the specific detail cache.
 *
 * @example
 * const { mutate } = useCloseEstimate()
 * mutate({ id: estimateId, payload: { exit_price: '42.50' } })
 */
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
      qc.invalidateQueries({ queryKey: estimateKeys.all })
      qc.invalidateQueries({ queryKey: estimateKeys.detail(id) })
    },
  })
}

/**
 * Soft-delete an estimate (backend sets is_deleted = true).
 *
 * Deleted estimates are hidden by default; pass `include_deleted: true` in
 * `useEstimates` filters to retrieve them.
 *
 * @example
 * const { mutate } = useDeleteEstimate()
 * mutate(estimateId)
 */
export function useDeleteEstimate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteEstimate(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: estimateKeys.all }),
  })
}

/**
 * Placeholder — generic estimate update hook.
 *
 * NOTE: The backend does NOT expose a generic PATCH /api/estimates/:id endpoint
 * in the current MVP plan (Piano-Operativo-v1.7.md). Only closing via
 * PATCH /api/estimates/:id/close is supported.
 *
 * This hook is reserved for a future task when partial updates (e.g. editing
 * target_price or stop_loss_price before close) are added to the backend.
 *
 * TODO (future task): Replace the `never` mutationFn once the backend endpoint
 *   PATCH /api/estimates/:id is implemented.
 *
 * @throws Always rejects — do not call until the backend endpoint exists.
 */
export function useUpdateEstimate() {
  return useMutation({
    mutationFn: (_payload: never) =>
      Promise.reject(
        new Error(
          'useUpdateEstimate: PATCH /api/estimates/:id is not yet implemented in the backend. Use useCloseEstimate() to close an open estimate.',
        ),
      ),
  })
}
