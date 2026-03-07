/**
 * Shared module — master barrel.
 *
 * Preferred import path for anything in shared/:
 *   import { apiClient, unwrapResponse } from '@/shared'
 *   import { useDebounce } from '@/shared'
 *   import { createMoney } from '@/shared'
 *
 * Features MUST import from here (not from internal shared/ paths)
 * to maintain stable public interfaces.
 */

// API client
export { default as apiClient } from './api/client'

// Standard response types + helpers
export type { ApiResponse } from './types'
export { unwrapResponse } from './types'

// Financial utilities (decimal.js wrappers)
export * from './utils'

// Custom hooks
export { useDebounce, useLocalStorage } from './hooks'

// UI components — uncomment progressively (TASK 4.5)
// export * from './components'
