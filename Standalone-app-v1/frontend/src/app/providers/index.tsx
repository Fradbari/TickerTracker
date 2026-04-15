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
import { Toaster } from 'react-hot-toast'
import { I18nextProvider } from 'react-i18next'
import { QueryProvider, queryClient } from './QueryProvider'
import { AppErrorBoundary } from '../components/AppErrorBoundary'
import { AsyncQueueProvider } from './AsyncQueueProvider'
import i18n from '@/shared/i18n/config'

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
      <I18nextProvider i18n={i18n}>
        <QueryProvider>
          <AsyncQueueProvider>
            <BrowserRouter>
              <AppErrorBoundary>
                {children}
              </AppErrorBoundary>
              {/* Toaster lives outside AppErrorBoundary so toasts work even during crashes */}
              <Toaster
                position="top-right"
                toastOptions={{
                  // Global style overrides
                  style: {
                    background: '#1e293b',   // slate-800
                    color: '#f1f5f9',        // slate-100
                    border: '1px solid #334155', // slate-700
                    fontSize: '0.875rem',
                  },
                  success: { duration: 3000 },
                  error: { duration: 5000 },
                }}
              />
            </BrowserRouter>
          </AsyncQueueProvider>
        </QueryProvider>
      </I18nextProvider>
    </React.StrictMode>
  )
}
