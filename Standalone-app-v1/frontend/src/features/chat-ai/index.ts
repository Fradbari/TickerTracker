/**
 * Chat-AI feature — public API.
 *
 * @example
 *   import { useSendMessage, type ChatMessage } from '@/features/chat-ai'
 */

export type {
  MessageRole,
  ChatMessage,
  ChatSession,
  SendMessagePayload,
  SendMessageResponse,
  EstimateAnalysisPayload,
  EstimateAnalysisResponse,
} from './types'

export {
  sendMessage,
  getChatSession,
  analyseEstimate,
} from './api'

export {
  CHAT_KEYS,
  useChatSession,
  useSendMessage,
  useAnalyseEstimate,
} from './hooks'

// export * from './components'  // TASK 4.15
