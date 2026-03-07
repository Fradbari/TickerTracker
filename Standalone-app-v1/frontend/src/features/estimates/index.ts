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
  // Key factory
  estimateKeys,
  ESTIMATE_KEYS,         // @deprecated alias — use estimateKeys

  // Read hooks
  useEstimates,
  useEstimateList,       // @deprecated alias — use useEstimates
  useEstimate,
  useEstimateHistory,
  useInfiniteEstimates,

  // Write hooks
  useCreateEstimate,
  useCloseEstimate,
  useDeleteEstimate,
  useUpdateEstimate,     // placeholder — backend endpoint not yet implemented
} from './hooks'

// Components — TASK 4.8: EstimateForm ✅
export { EstimateForm } from './components'
export type { EstimateFormProps } from './components'
// export { EstimateList } from './components'    // TASK 4.6
// export { EstimateDetail } from './components'  // TASK 4.7
// export { CloseEstimateModal } from './components' // TASK 4.10
