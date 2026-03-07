/**
 * Shared API types and typed request helpers.
 *
 * ApiError     — structured error returned by the response interceptor
 * ApiResponse  — backend response envelope (re-exported from shared/types)
 *
 * Typed helpers (get / post / patch / del):
 *   - Call apiClient (which applies auth + correlation-ID interceptors)
 *   - Unwrap ApiResponse<T>.data and throw ApiError on failure
 *   - Infer T from the call site — no manual casting needed
 *
 * @example
 *   import { get, post } from '@/shared/api'
 *
 *   const list = await get<EstimateListResponse>('/api/estimates', { params })
 *   const created = await post<EstimateCreatedResponse>('/api/estimates', payload)
 */
import type { AxiosRequestConfig } from 'axios'
import apiClient from './client'
import type { ApiResponse as _ApiResponse } from '../types/api'

// Re-export so consumers can do: import type { ApiResponse } from '@/shared/api'
export type { ApiResponse } from '../types/api'

// ---------------------------------------------------------------------------
// ApiError — replaces raw Axios errors after the response interceptor runs
// ---------------------------------------------------------------------------

/**
 * Structured error produced by the response interceptor.
 * All rejected promises from `get/post/patch/del` resolve to this type.
 *
 * Matches the backend error envelope:
 *   { success: false, error: { code, message, details }, trace_id }
 */
export interface ApiError {
  /** Short machine-readable error code, e.g. "NOT_FOUND", "VALIDATION_ERROR". */
  code: string
  /** Human-readable error message (from backend or network layer). */
  message: string
  /** Optional validation details or extra context. */
  details?: unknown
  /** HTTP status code (absent for network errors). */
  status?: number
  /** Backend trace_id for request tracing and log correlation. */
  trace_id?: string
}

/**
 * Type-guard: checks if an unknown caught value is an `ApiError`.
 *
 * @example
 *   try { await post(...) }
 *   catch (e) {
 *     if (isApiError(e)) console.error(e.code, e.message)
 *   }
 */
export function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === 'object' &&
    value !== null &&
    'code' in value &&
    'message' in value
  )
}

// ---------------------------------------------------------------------------
// Internal helper — unwrap ApiResponse<T> or throw ApiError
// ---------------------------------------------------------------------------

function unwrap<T>(responseData: _ApiResponse<T>): T {
  if (responseData.success === false || responseData.error) {
    const err: ApiError = {
      code: responseData.error?.code ?? 'REQUEST_FAILED',
      message: responseData.error?.message ?? 'Request failed',
      details: responseData.error?.details,
      trace_id: responseData.trace_id,
    }
    throw err
  }
  if (responseData.data === undefined) {
    const err: ApiError = { code: 'EMPTY_RESPONSE', message: 'Server returned no data' }
    throw err
  }
  return responseData.data as T
}

// ---------------------------------------------------------------------------
// Typed request helpers
// ---------------------------------------------------------------------------

/**
 * HTTP GET — unwraps ApiResponse<T>.data automatically.
 * Throws `ApiError` on HTTP error or backend error envelope.
 */
export async function get<T>(
  url: string,
  config?: AxiosRequestConfig,
): Promise<T> {
  const response = await apiClient.get<_ApiResponse<T>>(url, config)
  return unwrap(response.data)
}

/**
 * HTTP POST — sends `body` as JSON, unwraps ApiResponse<T>.data.
 * Throws `ApiError` on HTTP error or backend error envelope.
 */
export async function post<T>(
  url: string,
  body?: unknown,
  config?: AxiosRequestConfig,
): Promise<T> {
  const response = await apiClient.post<_ApiResponse<T>>(url, body, config)
  return unwrap(response.data)
}

/**
 * HTTP PATCH — partial update, unwraps ApiResponse<T>.data.
 * Throws `ApiError` on HTTP error or backend error envelope.
 */
export async function patch<T>(
  url: string,
  body?: unknown,
  config?: AxiosRequestConfig,
): Promise<T> {
  const response = await apiClient.patch<_ApiResponse<T>>(url, body, config)
  return unwrap(response.data)
}

/**
 * HTTP DELETE — named `del` to avoid collision with JS reserved word.
 * Unwraps ApiResponse<T>.data (backend may return the deleted resource).
 * Throws `ApiError` on HTTP error or backend error envelope.
 */
export async function del<T>(
  url: string,
  config?: AxiosRequestConfig,
): Promise<T> {
  const response = await apiClient.delete<_ApiResponse<T>>(url, config)
  return unwrap(response.data)
}
