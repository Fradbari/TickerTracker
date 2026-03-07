/**
 * useApiMutation — wrapper around TanStack Query v5 `useMutation`.
 *
 * Adds uniform error handling and optional success/error messaging.
 * Error and success messages are surfaced via `react-hot-toast` through
 * the `useNotify` hook. Pass `errorMessage` / `successMessage` for
 * human-readable overrides; falls back to `error.message` from the API.
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
import { isApiError } from '../api'
import { useNotify } from '../ui'

// ---------------------------------------------------------------------------
// Extra options (not part of the base UseMutationOptions)
// ---------------------------------------------------------------------------

interface ApiMutationExtras {
  /**
   * Human-readable success message surfaced as a green toast on mutation success.
   */
  successMessage?: string
  /**
   * Override the default error message shown on failure as a red toast.
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
  const notify = useNotify()

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
      const err = args[0]
      // Use error.code as toast id to deduplicate identical API errors
      const toastId = isApiError(err) ? err.code : undefined
      notify.error(errorMessage ?? err.message, { id: toastId })
      // Forward to caller-provided handler (if any) — spread preserves all v5 args
      return (userOnError as ((...a: typeof args) => unknown) | undefined)?.(...args)
    },

    onSuccess: (...args) => {
      if (successMessage) {
        notify.success(successMessage)
      }
      return (userOnSuccess as ((...a: typeof args) => unknown) | undefined)?.(...args)
    },

    ...rest,
  })
}
