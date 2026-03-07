/**
 * Shared API barrel.
 *
 * Named exports:
 *   apiClient         — raw Axios instance (auth + correlation-ID interceptors)
 *   get / post / patch / del — typed helpers that unwrap ApiResponse<T>
 *   ApiError          — structured error type produced by the interceptor
 *   ApiResponse       — backend response envelope type
 *   isApiError        — type-guard for catch blocks
 */
export { default as apiClient } from './client'
export type { ApiError, ApiResponse } from './types'
export { get, post, patch, del, isApiError } from './types'
