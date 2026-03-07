/**
 * useApiQuery — thin wrapper around TanStack Query v5 `useQuery`.
 *
 * Adds these defaults over raw `useQuery`:
 *   - Errors are always typed as `Error` (never `unknown`)
 *   - `throwOnError: false` is explicit (errors surface via `result.error`, not throws)
 *   - Optional `showErrorToast: true` auto-displays a red toast whenever the
 *     query enters an error state (uses `useNotify` + `error.code` for deduplication)
 *   - All other QueryOptions pass through unchanged
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, error } = useApiQuery({
 *   queryKey: ESTIMATE_KEYS.detail(id),
 *   queryFn: () => getEstimate(id),
 *   enabled: Boolean(id),
 *   showErrorToast: true, // optional — shows a toast on query failure
 * })
 * if (error) return <ErrorBanner message={error.message} />
 * ```
 *
 * @see https://tanstack.com/query/v5/docs/framework/react/reference/useQuery
 */
import { useEffect } from 'react'
import {
  useQuery,
  type UseQueryOptions,
  type UseQueryResult,
  type QueryKey,
} from '@tanstack/react-query'
import { isApiError } from '../api'
import { useNotify } from '../ui'

// ---------------------------------------------------------------------------
// Extended options type
// ---------------------------------------------------------------------------

type ApiQueryOptions<TData, TQueryKey extends QueryKey> = UseQueryOptions<
  TData,
  Error,
  TData,
  TQueryKey
> & {
  /**
   * When `true`, automatically shows a red toast whenever the query enters an
   * error state. The toast id is set to `ApiError.code` for deduplication so
   * repeated retries for the same network error don't stack multiple toasts.
   * @default false
   */
  showErrorToast?: boolean
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useApiQuery<
  TData,
  TQueryKey extends QueryKey = QueryKey,
>(
  options: ApiQueryOptions<TData, TQueryKey>,
): UseQueryResult<TData, Error> {
  const { showErrorToast, ...queryOptions } = options

  const notify = useNotify()

  const result = useQuery<TData, Error, TData, TQueryKey>({
    throwOnError: false,
    ...queryOptions,
  })

  // TanStack Query v5 removed `onError` from `useQuery` — use `useEffect` instead.
  useEffect(() => {
    if (!showErrorToast || !result.error) return
    const err = result.error
    const toastId = isApiError(err) ? err.code : undefined
    notify.error(err.message, { id: toastId })
  // Only fire when the error reference changes — suppress notify in deps
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result.error, showErrorToast])

  return result
}
