/**
 * useApiMutation — wrapper around TanStack Query v5 `useMutation`.
 *
 * Adds uniform error handling and optional success/error messaging.
 * Toast notifications are intentionally NOT implemented yet (TASK 4.5 will
 * introduce the shared UI component library). A console.warn / console.info
 * is used as a placeholder so the interface is stable.
 *
 * Usage:
 * ```tsx
 * const { mutate, isPending } = useApiMutation(
 *   (payload: CreateEstimatePayload) => createEstimate(payload),
 *   {
 *     successMessage: 'Stima creata con successo',
 *     onSuccess: (data) => navigate(`/estimates/${data.estimate.id}`),
 *   }
 * )
 * ```
 *
 * @see https://tanstack.com/query/v5/docs/framework/react/reference/useMutation
 */
import {
  useMutation,
  type UseMutationOptions,
  type UseMutationResult,
} from '@tanstack/react-query'

// ---------------------------------------------------------------------------
// Extra options (not part of the base UseMutationOptions)
// ---------------------------------------------------------------------------

interface ApiMutationExtras {
  /**
   * Human-readable success message.
   * Currently logged to console; will trigger a toast notification once the
   * shared toast component is available (TASK 4.5).
   */
  successMessage?: string
  /**
   * Override the default error message shown on failure.
   * Falls back to `error.message` from the API response.
   */
  errorMessage?: string
}

type ApiMutationOptions<TData, TVariables, TContext = unknown> = Omit<
  UseMutationOptions<TData, Error, TVariables, TContext>,
  'mutationFn'
> &
  ApiMutationExtras

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

/**
 * @param mutationFn - Async function that performs the mutation.
 * @param options    - Optional UseMutation config + successMessage / errorMessage.
 */
export function useApiMutation<TData, TVariables, TContext = unknown>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: ApiMutationOptions<TData, TVariables, TContext>,
): UseMutationResult<TData, Error, TVariables, TContext> {
  const {
    successMessage,
    errorMessage,
    onError: userOnError,
    onSuccess: userOnSuccess,
    ...rest
  } = options ?? {}

  return useMutation<TData, Error, TVariables, TContext>({
    mutationFn,

    onError: (...args) => {
      // ── Placeholder: replace with toast once TASK 4.5 ships ──────────────
      console.warn(
        '[useApiMutation] Errore:',
        errorMessage ?? args[0].message,
      )
      // Forward to caller-provided handler (if any) — spread preserves all v5 args
      return (userOnError as ((...a: typeof args) => unknown) | undefined)?.(...args)
    },

    onSuccess: (...args) => {
      if (successMessage) {
        // ── Placeholder: replace with toast once TASK 4.5 ships ──────────
        console.info('[useApiMutation] Successo:', successMessage)
      }
      return (userOnSuccess as ((...a: typeof args) => unknown) | undefined)?.(...args)
    },

    ...rest,
  })
}
