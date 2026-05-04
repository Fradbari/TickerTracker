/**
 * Frontend logger — sends errors/logs to backend for centralised logging.
 *
 * Responsibilities:
 *   - logToBackend: async function to POST frontend logs to backend
 *   - Used by API client interceptor to log HTTP errors
 *   - Integrates with backend logging endpoint at /api/logs/frontend
 */

export interface FrontendLogPayload {
  level: 'error' | 'warn' | 'info' | 'debug'
  message: string
  trace_id?: string
  meta?: Record<string, unknown>
}

/**
 * Send a frontend log entry to the backend.
 * Silently fails if the backend is unreachable (avoid infinite error loops).
 */
export async function logToBackend(payload: FrontendLogPayload): Promise<void> {
  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL ?? ''}/api/logs/frontend`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(import.meta.env.VITE_API_KEY && {
            'X-API-Key': import.meta.env.VITE_API_KEY,
          }),
        },
        body: JSON.stringify(payload),
      }
    )

    // Log sent successfully; don't throw on non-success response
    if (!response.ok) {
      console.warn(`[logToBackend] backend returned ${response.status}`)
    }
  } catch (error) {
    // Network error or other failure — log locally and move on
    // (avoid infinite loop if backend is down)
    console.warn('[logToBackend] failed to send log to backend:', error)
  }
}
