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
import { QueryClient, QueryClientProvider, QueryCache } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { toast } from 'react-hot-toast'
import type { EstimateListResponse, Estimate } from '@/shared/types'

// ---------------------------------------------------------------------------
// Singleton QueryClient â€” created once at module level, not inside a component
// ---------------------------------------------------------------------------

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onSuccess: (data, query) => {
      // Stub function: Simulazione di eventi SSE (estimate_update) o polling diff.
      // I toast vengono triggerati qui per assicurare che siano emessi NELLO STESSO PUNTO 
      // in cui lo stato (la cache React Query) viene aggiornato per evitare race conditions.
      const queryKey = query.queryKey as string[];
      if (queryKey[0] === 'estimates' && queryKey[1] === 'list') {
        const newData = data as EstimateListResponse;
        const oldData = query.state.data as EstimateListResponse | undefined;

        if (oldData && newData.items) {
          newData.items.forEach((newEst: Estimate) => {
            const oldEst = oldData.items.find((e: Estimate) => e.id === newEst.id);
            // Verifica se lo stato è cambiato rispetto al precedente (simulando un evento SSE "estimate_update")
            if (oldEst && oldEst.status !== newEst.status && newEst.status === 'CLOSED') {
              const targetOrStop = newEst.realized_pnl && Number(newEst.realized_pnl) > 0 ? 'Target' : 'Stop Loss';
              const price = newEst.close_price ? newEst.close_price : newEst.target_price; // Mocking close price presence
              if (targetOrStop === 'Target') {
                toast.success(
                  `🎯 ${newEst.ticker} — Target raggiunto a ${price}€ / ${price}$`,
                  { duration: 4000 }
                );
              } else {
                toast.error(
                  `⚠️ ${newEst.ticker} — Stop Loss colpito a ${price}€ / ${price}$`,
                  { duration: 4000 }
                );
              }
            }
          });
        }
      }
    }
  }),
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
