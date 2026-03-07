/**
 * Application providers — wraps the entire React tree with all global context.
 *
 * Providers:
 *   1. React.StrictMode  — double-render in dev to detect side effects
 *   2. QueryClientProvider — TanStack Query server-state cache
 *   3. BrowserRouter       — React Router v7 client-side routing
 *
 * Usage in main.tsx:
 *   ReactDOM.createRoot(document.getElementById('root')!).render(
 *     <AppProviders><App /></AppProviders>
 *   )
 */
import React, { type ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'

// ---------------------------------------------------------------------------
// Shared QueryClient instance (singleton — do NOT create inside a component)
// ---------------------------------------------------------------------------

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1_000 * 60 * 5,  // 5 minutes default freshness
      retry: 1,                    // 1 automatic retry on error
    },
  },
})

// ---------------------------------------------------------------------------
// AppProviders component
// ---------------------------------------------------------------------------

interface AppProvidersProps {
  children: ReactNode
}

/**
 * Root provider wrapper.
 * Import from '@/app' or '@/app/providers' — never import the QueryClient
 * instance directly from here in feature code (use useQueryClient() instead).
 */
export function AppProviders({ children }: AppProvidersProps) {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    </React.StrictMode>
  )
}
