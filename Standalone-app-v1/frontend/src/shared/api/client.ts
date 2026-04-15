/**
 * Centralised Axios API client.
 *
 * Responsibilities:
 *   - Base URL from VITE_API_BASE_URL (empty = Vite proxy handles /api/* in dev)
 *   - REQUEST interceptor:
 *       • X-API-Key   from VITE_API_KEY env var
 *       • Authorization: Bearer <token>  from localStorage (placeholder — no OAuth yet)
 *       • X-Correlation-ID  new UUID per request (backend logs + trace)
 *   - RESPONSE interceptor:
 *       • Errors rejected as ApiError objects (structured, not raw Axios errors)
 *
 * NOTE: success-response unwrapping (extracting ApiResponse<T>.data) is done
 * in the typed helper functions (get/post/patch/del in ./types.ts), NOT here.
 * Unwrapping in the interceptor would break Axios generic type inference.
 *
 * Usage: import typed helpers, not this file directly.
 *   import { get, post } from '@/shared/api'
 */
import axios from 'axios'
import type { ApiError } from './types'

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30_000,
})

// ---------------------------------------------------------------------------
// REQUEST interceptor — auth + tracing headers
// ---------------------------------------------------------------------------

apiClient.interceptors.request.use((config) => {
  // API key (backend security middleware expects X-API-Key)
  const apiKey = import.meta.env.VITE_API_KEY
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }

  // Bearer token — placeholder until proper auth is implemented (TASK 2.7/2.8)
  const token = typeof window !== 'undefined'
    ? window.localStorage.getItem('auth_token')
    : null
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }

  // Correlation ID — unique per request; propagated through backend logs
  config.headers['X-Correlation-ID'] = crypto.randomUUID()

  return config
})

// ---------------------------------------------------------------------------
// RESPONSE interceptor — normalise errors into ApiError
// ---------------------------------------------------------------------------

apiClient.interceptors.response.use(
  // Success path — pass through unchanged (unwrapping happens in typed helpers)
  (response) => response,

  // Error path — build a structured ApiError and reject with it
  (error) => {
    const responseData = error.response?.data

    const apiError: ApiError = {
      code: responseData?.error?.code ?? String(error.response?.status ?? 'NETWORK_ERROR'),
      message:
        responseData?.error?.message ??
        responseData?.detail ??
        error.message ??
        'Errore sconosciuto',
      details: responseData?.error?.details ?? undefined,
      status: error.response?.status,
      trace_id: responseData?.trace_id ?? undefined,
    }

    // Log the error to backend if it's not a log request itself
    if (error.config && !error.config.url?.includes('/api/logs/frontend')) {
      import('./logger').then(({ logToBackend }) => {
        logToBackend({
          level: 'error',
          message: `API HTTP Error ${apiError.status}: ${apiError.message}`,
          trace_id: apiError.trace_id || error.config?.headers?.['X-Correlation-ID'],
          meta: { url: error.config?.url, method: error.config?.method, code: apiError.code }
        })
      }).catch(console.error)
    }

    return Promise.reject(apiError)
  },
)

export default apiClient
