/**
 * Chat-AI feature — TypeScript types.
 *
 * The chat-AI feature integrates with Gemini for estimate reasoning
 * and analysis (TASK 4.15). Types are defined now to allow progressive
 * implementation without breaking changes.
 */

// ---------------------------------------------------------------------------
// Message
// ---------------------------------------------------------------------------

export type MessageRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  timestamp: string    // ISO 8601
  /** Optional: the estimate_id this message is scoped to. */
  estimate_id?: string
  /** Optional: AI model used (e.g. "gemini-1.5-pro"). */
  model?: string
  /** Confidence score returned by the AI (0–100). */
  confidence?: number
}

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------

export interface ChatSession {
  id: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
  estimate_id?: string
}

// ---------------------------------------------------------------------------
// Payloads
// ---------------------------------------------------------------------------

export interface SendMessagePayload {
  message: string
  session_id?: string
  estimate_id?: string
  context?: Record<string, unknown>
}

export interface SendMessageResponse {
  session_id: string
  reply: ChatMessage
}

// ---------------------------------------------------------------------------
// Analysis request (ask AI to analyse an estimate)
// ---------------------------------------------------------------------------

export interface EstimateAnalysisPayload {
  estimate_id: string
  /** Additional free-form context from the user. */
  context?: string
}

export interface EstimateAnalysisResponse {
  estimate_id: string
  reasoning: string
  confidence: number     // 0–100
  recommendation: 'BUY' | 'HOLD' | 'AVOID'
  model: string
  created_at: string
}
