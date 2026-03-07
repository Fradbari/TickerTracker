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

// API client (raw Axios instance — prefer typed helpers below)
export { default as apiClient } from './api/client'

// Typed request helpers — unwrap ApiResponse<T> automatically
export { get, post, patch, del, isApiError } from './api'
export type { ApiError } from './api'

// Standard response types + helpers
export type { ApiResponse } from './types'
export { unwrapResponse } from './types'

// Financial utilities — low-level primitives (MoneyValue, createMoney, etc.)
export * from './utils'

// Finance module — high-level monetary helpers for components (TASK 4.5)
// Note: formatMoney and formatPercentage are intentionally not re-exported here
// because ./utils exports same-named functions with different signatures.
// Import them directly from '@/shared/finance' when you need the MoneyDecimal variants.
export type { MoneyDecimal, PnLResult } from './finance'
export { parseMoneyFromString, fromDecimalAmount, calculatePnL } from './finance'

// Custom hooks
export { useDebounce, useLocalStorage, useApiQuery, useApiMutation } from './hooks'

// UI utilities — toast notifications and cross-cutting UI helpers (TASK 4.7)
export { useNotify } from './ui'
export type { Notify, NotifyOptions } from './ui'
