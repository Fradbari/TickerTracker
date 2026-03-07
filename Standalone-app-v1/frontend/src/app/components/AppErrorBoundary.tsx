/**
 * AppErrorBoundary — global React Error Boundary.
 *
 * Catches any unhandled JavaScript error thrown inside the React component
 * tree and renders a user-friendly fallback screen instead of a blank page.
 *
 * IMPORTANT: Error Boundaries MUST be class components. React does not support
 * function-component error boundaries (getDerivedStateFromError / componentDidCatch
 * are class-only lifecycle methods).
 *
 * Placement:
 *   Wrap the root <App /> inside AppProviders so the entire component tree is
 *   protected. The ErrorBoundary intentionally sits outside individual feature
 *   routes so navigation itself still works even if a child crashes.
 *
 * Recovery:
 *   - "Riprova" button resets the boundary state (works for transient errors).
 *   - "Ricarica pagina" performs a full `window.location.reload()` (last resort).
 *
 * @example
 * // In AppProviders or main.tsx:
 * <AppErrorBoundary>
 *   <App />
 * </AppErrorBoundary>
 */
import React, { Component, type ErrorInfo } from 'react'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Props {
  children: React.ReactNode
  /** Optional custom fallback. Defaults to the built-in error screen. */
  fallback?: React.ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export class AppErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
    this.handleReset = this.handleReset.bind(this)
  }

  // -------------------------------------------------------------------------
  // React Error Boundary lifecycle
  // -------------------------------------------------------------------------

  /**
   * Derived from React error — called synchronously during render when a
   * descendant throws. Sets the `hasError` flag before the next paint so the
   * fallback is shown without a flash of the broken UI.
   */
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  /**
   * Called after the fallback render. Use for logging / monitoring.
   * Never perform UI mutations here — the component tree is already committed.
   */
  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Use `console.error` so error monitoring tools (Sentry, Datadog, etc.)
    // can pick it up via their `console` integration.
    console.error('[AppErrorBoundary] Uncaught error:', error)
    console.error('[AppErrorBoundary] Component stack:', info.componentStack)
  }

  // -------------------------------------------------------------------------
  // Recovery handler
  // -------------------------------------------------------------------------

  /** Resets the boundary — try to re-render the original subtree. */
  handleReset(): void {
    this.setState({ hasError: false, error: null })
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  render() {
    if (!this.state.hasError) {
      return this.props.children
    }

    if (this.props.fallback) {
      return this.props.fallback
    }

    return (
      <ErrorFallback
        error={this.state.error}
        onReset={this.handleReset}
      />
    )
  }
}

// ---------------------------------------------------------------------------
// Default fallback UI
// ---------------------------------------------------------------------------

interface ErrorFallbackProps {
  error: Error | null
  onReset: () => void
}

function ErrorFallback({ error, onReset }: ErrorFallbackProps) {
  return (
    <div
      role="alert"
      className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-4 text-center"
    >
      {/* Icon */}
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-900/30 text-red-400">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="h-8 w-8"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
          />
        </svg>
      </div>

      {/* Heading */}
      <h1 className="mb-2 text-2xl font-bold text-slate-100">
        Qualcosa è andato storto
      </h1>
      <p className="mb-2 text-slate-400">
        Si è verificato un errore inatteso nell'applicazione.
      </p>

      {/* Error detail — only in development */}
      {import.meta.env.DEV && error && (
        <details className="mb-8 max-w-lg text-left">
          <summary className="cursor-pointer text-sm text-slate-500 hover:text-slate-300">
            Dettaglio tecnico
          </summary>
          <pre className="mt-2 overflow-auto rounded bg-slate-900 p-3 text-xs text-red-400">
            {error.message}
            {error.stack ? `\n\n${error.stack}` : ''}
          </pre>
        </details>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onReset}
          className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-slate-950"
        >
          Riprova
        </button>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="rounded-md border border-slate-600 px-5 py-2.5 text-sm font-medium text-slate-300 hover:border-slate-400 hover:text-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 focus:ring-offset-slate-950"
        >
          Ricarica pagina
        </button>
      </div>
    </div>
  )
}
