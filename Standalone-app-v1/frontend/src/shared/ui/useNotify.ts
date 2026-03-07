/**
 * useNotify — uniform toast notifications for the TickerTracker frontend.
 *
 * Wraps `react-hot-toast` with an opinionated API that:
 *   1. Applies consistent default durations per severity
 *   2. Deduplicates toasts by id (pass `error.code` from ApiError)
 *   3. Limits simultaneous visible toasts to avoid UI chaos
 *
 * The hook is intentionally thin — it does NOT create a new QueryClient or
 * context. Use it freely inside any component or custom hook.
 *
 * @example
 * ```tsx
 * import { useNotify } from '@/shared'
 *
 * function MyComponent() {
 *   const notify = useNotify()
 *
 *   const handleSave = async () => {
 *     try {
 *       await save()
 *       notify.success('Salvato con successo')
 *     } catch (e) {
 *       if (isApiError(e)) notify.error(e.message, { id: e.code })
 *       else notify.error('Errore sconosciuto')
 *     }
 *   }
 * }
 * ```
 *
 * @example — inside useApiMutation (automatic error toasting):
 * ```tsx
 * useApiMutation(createEstimate, { errorMessage: 'Creazione stima fallita' })
 * ```
 */
import { useCallback } from 'react'
import toast from 'react-hot-toast'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface NotifyOptions {
  /**
   * Stable identifier for this toast.
   * If a toast with the same id is already visible, react-hot-toast will
   * UPDATE it in place instead of stacking a duplicate.
   *
   * Recommended: pass `ApiError.code` so identical network errors are
   * deduplicated automatically.
   */
  id?: string
  /** Duration in milliseconds. Defaults per severity if omitted. */
  duration?: number
}

export interface Notify {
  /**
   * Show a green success toast.
   * Default duration: 3 000 ms.
   */
  success: (message: string, options?: NotifyOptions) => void
  /**
   * Show a red error toast.
   * Default duration: 5 000 ms (longer so users can read the message).
   */
  error: (message: string, options?: NotifyOptions) => void
  /**
   * Show a neutral informational toast.
   * Default duration: 3 000 ms.
   */
  info: (message: string, options?: NotifyOptions) => void
  /**
   * Dismiss a specific toast by id, or all toasts if no id is provided.
   */
  dismiss: (id?: string) => void
}

// ---------------------------------------------------------------------------
// Default durations (ms)
// ---------------------------------------------------------------------------

const DURATION = {
  success: 3_000,
  error: 5_000,
  info: 3_000,
} as const

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

/**
 * Returns a stable `Notify` object with `success`, `error`, `info`, `dismiss`
 * methods backed by `react-hot-toast`.
 *
 * The returned object reference is stable across re-renders (all methods are
 * memoised with `useCallback`).
 */
export function useNotify(): Notify {
  const success = useCallback((message: string, options?: NotifyOptions) => {
    toast.success(message, {
      id: options?.id,
      duration: options?.duration ?? DURATION.success,
    })
  }, [])

  const error = useCallback((message: string, options?: NotifyOptions) => {
    toast.error(message, {
      id: options?.id,
      duration: options?.duration ?? DURATION.error,
    })
  }, [])

  const info = useCallback((message: string, options?: NotifyOptions) => {
    toast(message, {
      id: options?.id,
      duration: options?.duration ?? DURATION.info,
    })
  }, [])

  const dismiss = useCallback((id?: string) => {
    if (id) toast.dismiss(id)
    else toast.dismiss()
  }, [])

  return { success, error, info, dismiss }
}
