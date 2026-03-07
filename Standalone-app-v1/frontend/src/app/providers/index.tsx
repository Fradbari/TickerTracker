/**
 * Application providers — wraps the entire React tree with all global context.
 *
 * Provider stack (outermost → innermost):
 *   1. React.StrictMode  — double-render in dev to detect side effects
 *   2. QueryProvider     — TanStack Query v5 client + ReactQueryDevtools (dev only)
 *   3. BrowserRouter     — React Router v7 client-side routing
 *
 * Usage in main.tsx:
 *   ReactDOM.createRoot(document.getElementById('root')!).render(
 *     <AppProviders><App /></AppProviders>
 *   )
 */
import React, { type ReactNode } from 'react'
import { BrowserRouter } from 'react-router-dom'
import { QueryProvider, queryClient } from './QueryProvider'

// Re-export queryClient so callers can do:
//   import { queryClient } from '@/app/providers'
// (prefer useQueryClient() inside components)
export { queryClient }

// ---------------------------------------------------------------------------
// AppProviders
// ---------------------------------------------------------------------------

interface AppProvidersProps {
  children: ReactNode
}

/**
 * Root provider wrapper.
 * Import from '@/app' or '@/app/providers'.
 * Never import QueryClient directly in feature code — use useQueryClient() instead.
 */
export function AppProviders({ children }: AppProvidersProps) {
  return (
    <React.StrictMode>
      <QueryProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryProvider>
    </React.StrictMode>
  )
}
