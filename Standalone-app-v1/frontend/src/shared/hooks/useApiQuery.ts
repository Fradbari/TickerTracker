/**
 * useApiQuery — thin wrapper around TanStack Query v5 `useQuery`.
 *
 * Adds these defaults over raw `useQuery`:
 *   - Errors are always typed as `Error` (never `unknown`)
 *   - `throwOnError: false` is explicit (errors surface via `result.error`, not throws)
 *   - All other QueryOptions pass through unchanged
 *
 * Usage:
 * ```tsx
 * const { data, isLoading, error } = useApiQuery({
 *   queryKey: ESTIMATE_KEYS.detail(id),
 *   queryFn: () => getEstimate(id),
 *   enabled: Boolean(id),
 * })
 * if (error) return <ErrorBanner message={error.message} />
 * ```
 *
 * @see https://tanstack.com/query/v5/docs/framework/react/reference/useQuery
 */
import {
  useQuery,
  type UseQueryOptions,
  type UseQueryResult,
  type QueryKey,
} from '@tanstack/react-query'

export function useApiQuery<
  TData,
  TQueryKey extends QueryKey = QueryKey,
>(
  options: UseQueryOptions<TData, Error, TData, TQueryKey>,
): UseQueryResult<TData, Error> {
  return useQuery<TData, Error, TData, TQueryKey>({
    throwOnError: false,
    ...options,
  })
}
