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
  usePortfolioMetrics
} from './hooks'

export { Dashboard } from './components'

