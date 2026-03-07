/**
 * Chat-AI feature — API layer.
 *
 * Routes map to the AI Prompt Service (TASK 2.28).
 * Endpoints are not yet available (backend implementation pending).
 */
import apiClient from '@/shared/api/client'
import { unwrapResponse } from '@/shared/types'
import type { ApiResponse } from '@/shared/types'
import type {
  ChatSession,
  SendMessagePayload,
  SendMessageResponse,
  EstimateAnalysisPayload,
  EstimateAnalysisResponse,
} from '../types'

const BASE = '/api/ai'

/** Start a new chat session or continue an existing one. */
export async function sendMessage(
  payload: SendMessagePayload,
): Promise<SendMessageResponse> {
  const { data } = await apiClient.post<ApiResponse<SendMessageResponse>>(
    `${BASE}/chat`,
    payload,
  )
  return unwrapResponse(data)
}

/** Retrieve an existing chat session by id. */
export async function getChatSession(sessionId: string): Promise<ChatSession> {
  const { data } = await apiClient.get<ApiResponse<ChatSession>>(
    `${BASE}/chat/${sessionId}`,
  )
  return unwrapResponse(data)
}

/** Request an AI analysis of an estimate. */
export async function analyseEstimate(
  payload: EstimateAnalysisPayload,
): Promise<EstimateAnalysisResponse> {
  const { data } = await apiClient.post<ApiResponse<EstimateAnalysisResponse>>(
    `${BASE}/analyse`,
    payload,
  )
  return unwrapResponse(data)
}
