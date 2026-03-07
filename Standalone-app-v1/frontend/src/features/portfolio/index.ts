/**
 * Portfolio feature — public API.
 *
 * @example
 *   import { usePortfolioSummary, type PortfolioSummary } from '@/features/portfolio'
 */

export type {
  PortfolioSummary,
  PortfolioPosition,
  PerformanceByPeriod,
} from './types'

export {
  getPortfolioSummary,
  getOpenPositions,
  getPerformanceByPeriod,
} from './api'

export {
  PORTFOLIO_KEYS,
  usePortfolioSummary,
  useOpenPositions,
  usePerformanceByPeriod,
} from './hooks'

// export * from './components'  // TASK 4.11, 4.12
