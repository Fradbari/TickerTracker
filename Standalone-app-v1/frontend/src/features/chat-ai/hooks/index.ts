/**
 * Chat-AI feature — TanStack Query hooks.
 *
 * Chat uses mutations (send message) + queries (load session history).
 * Backend AI endpoints are pending (TASK 2.28).
 */
import { useQuery, useMutation } from '@tanstack/react-query'
import { sendMessage, getChatSession, analyseEstimate } from '../api'
import type { SendMessagePayload, EstimateAnalysisPayload } from '../types'

export const CHAT_KEYS = {
  all: ['chat-ai'] as const,
  session: (id: string) => [...CHAT_KEYS.all, 'session', id] as const,
  analysis: (estimateId: string) =>
    [...CHAT_KEYS.all, 'analysis', estimateId] as const,
} as const

/** Load a chat session by id (message history). */
export function useChatSession(sessionId: string) {
  return useQuery({
    queryKey: CHAT_KEYS.session(sessionId),
    queryFn: () => getChatSession(sessionId),
    enabled: Boolean(sessionId),
    // Chat history doesn't go stale — only new messages mutate it
    staleTime: Infinity,
  })
}

/**
 * Send a user message (creates or continues a chat session).
 * Returns the AI reply. The caller is responsible for updating local state
 * with the optimistic message and the confirmed reply.
 */
export function useSendMessage() {
  return useMutation({
    mutationFn: (payload: SendMessagePayload) => sendMessage(payload),
  })
}

/** Request an AI analysis of an estimate. */
export function useAnalyseEstimate() {
  return useMutation({
    mutationFn: (payload: EstimateAnalysisPayload) => analyseEstimate(payload),
  })
}
