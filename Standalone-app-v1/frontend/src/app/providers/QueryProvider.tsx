/**
 * QueryProvider — TanStack Query v5 configuration.
 *
 * Centralises all QueryClient defaults in one place.
 * Import `queryClient` for direct access (e.g. in tests or imperative
 * invalidation outside React). All components should use `useQueryClient()`.
 *
 * Retry strategy: exponential back-off capped at 30 s.
 *   attempt 0 → 1 s, attempt 1 → 2 s, attempt 2 → 4 s, attempt 3 → 30 s
 */
import { type ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// ---------------------------------------------------------------------------
// Singleton QueryClient — created once at module level, not inside a component
// ---------------------------------------------------------------------------

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      /** Data is considered fresh for 5 minutes. */
      staleTime: 5 * 60 * 1_000,
      /**
       * Inactive queries are garbage-collected after 30 minutes.
       * (v4 name was `cacheTime`; renamed to `gcTime` in v5.)
       */
      gcTime: 30 * 60 * 1_000,
      /**
       * Exponential back-off: 2^attempt * 1000 ms, capped at 30 s.
       * 3 retries = max ~7 s total extra wait before giving up.
       */
      retry: 3,
      retryDelay: (attempt: number) => Math.min(1_000 * 2 ** attempt, 30_000),
      /** Re-fetch when the browser tab regains focus (default true, explicit for clarity). */
      refetchOnWindowFocus: true,
    },
    mutations: {
      /** Mutations do NOT retry by default (write idempotency is not guaranteed). */
      retry: 0,
    },
  },
})

// ---------------------------------------------------------------------------
// QueryProvider component
// ---------------------------------------------------------------------------

interface QueryProviderProps {
  children: ReactNode
}

/**
 * Wraps children with QueryClientProvider + ReactQueryDevtools (dev only).
 *
 * Devtools panel is lazy-loaded and tree-shaken from production bundles
 * because it is rendered only when `import.meta.env.DEV === true`.
 */
export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {import.meta.env.DEV && (
        <ReactQueryDevtools
          initialIsOpen={false}
          buttonPosition="bottom-right"
        />
      )}
    </QueryClientProvider>
  )
}
