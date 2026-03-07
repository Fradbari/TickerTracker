/**
 * Estimates feature — public API.
 *
 * RULE: All imports from outside this feature MUST use this file as entry
 * point. Never import from internal paths (api/, hooks/, types/, components/).
 *
 * @example
 *   import { useEstimateList, type Estimate } from '@/features/estimates'
 */

// Types (read & write models)
export type {
  Estimate,
  EstimateDirection,
  EstimateStatus,
  EstimateListResponse,
  EstimateCreatedResponse,
  EstimateUpdatedResponse,
  EstimateDeletedResponse,
  PageInfo,
  CreateEstimatePayload,
  CloseEstimatePayload,
  EstimateListParams,
} from './types'

// API functions (use hooks in components; API layer for non-React code)
export {
  listEstimates,
  getEstimate,
  createEstimate,
  closeEstimate,
  deleteEstimate,
  getEstimateHistory,
} from './api'

// TanStack Query hooks
export {
  ESTIMATE_KEYS,
  useEstimateList,
  useInfiniteEstimates,
  useEstimate,
  useCreateEstimate,
  useCloseEstimate,
  useDeleteEstimate,
} from './hooks'

// Components — uncomment progressively as tasks are completed
// export * from './components'
