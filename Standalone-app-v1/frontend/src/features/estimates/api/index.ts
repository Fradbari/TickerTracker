/**
 * Estimates feature — API layer.
 *
 * All HTTP calls go through the centralised Axios client from @/shared/api.
 * Endpoints are prefixed with /api (handled by the Vite proxy in dev, or
 * VITE_API_TARGET in Docker).
 */
import { unwrapResponse } from '@/shared/types'
import apiClient from '@/shared/api/client'
import type {
  Estimate,
  EstimateListParams,
  EstimateListResponse,
  CreateEstimatePayload,
  CloseEstimatePayload,
  EstimateCreatedResponse,
  EstimateUpdatedResponse,
  EstimateDeletedResponse,
} from '../types'
import type { ApiResponse } from '@/shared/types'

const BASE = '/api/estimates'

// ---------------------------------------------------------------------------
// List
// ---------------------------------------------------------------------------

export async function listEstimates(
  params?: EstimateListParams,
): Promise<EstimateListResponse> {
  const { data } = await apiClient.get<ApiResponse<EstimateListResponse>>(
    BASE,
    { params },
  )
  return unwrapResponse(data)
}

// ---------------------------------------------------------------------------
// Get one
// ---------------------------------------------------------------------------

export async function getEstimate(id: string): Promise<Estimate> {
  const { data } = await apiClient.get<ApiResponse<Estimate>>(`${BASE}/${id}`)
  return unwrapResponse(data)
}

// ---------------------------------------------------------------------------
// Create
// ---------------------------------------------------------------------------

export async function createEstimate(
  payload: CreateEstimatePayload,
): Promise<EstimateCreatedResponse> {
  const { data } = await apiClient.post<ApiResponse<EstimateCreatedResponse>>(
    BASE,
    payload,
  )
  return unwrapResponse(data)
}

// ---------------------------------------------------------------------------
// Close
// ---------------------------------------------------------------------------

export async function closeEstimate(
  id: string,
  payload: CloseEstimatePayload,
): Promise<EstimateUpdatedResponse> {
  const { data } = await apiClient.patch<ApiResponse<EstimateUpdatedResponse>>(
    `${BASE}/${id}/close`,
    payload,
  )
  return unwrapResponse(data)
}

// ---------------------------------------------------------------------------
// Delete (soft-delete on backend)
// ---------------------------------------------------------------------------

export async function deleteEstimate(id: string): Promise<EstimateDeletedResponse> {
  const { data } = await apiClient.delete<ApiResponse<EstimateDeletedResponse>>(
    `${BASE}/${id}`,
  )
  return unwrapResponse(data)
}

// ---------------------------------------------------------------------------
// History / audit trail
// ---------------------------------------------------------------------------

export async function getEstimateHistory(id: string): Promise<unknown> {
  const { data } = await apiClient.get<ApiResponse<unknown>>(
    `${BASE}/${id}/history`,
  )
  return unwrapResponse(data)
}
