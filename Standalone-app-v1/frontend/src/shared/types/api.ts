/**
 * Standard backend response envelope — matches ApiResponse[T] from the backend.
 */
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
    details?: unknown
  }
  trace_id?: string
}

/**
 * Unwrap an ApiResponse data field, throwing if the response indicates failure.
 */
export function unwrapResponse<T>(response: ApiResponse<T>): T {
  if (!response.success || response.data === undefined) {
    throw new Error(response.error?.message ?? 'Request failed')
  }
  return response.data
}
