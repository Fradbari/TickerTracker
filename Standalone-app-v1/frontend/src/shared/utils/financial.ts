/**
 * Financial utilities barrel export
 * 
 * Re-exports all Money and Percentage operations for clean imports.
 * 
 * Example:
 *   import { createMoney, addMoney } from '@/shared/utils/financial'
 *   import { createPercentage, applyPercentage } from '@/shared/utils/financial'
 */

// Re-export Money types and functions
export type { MoneyValue } from './decimal'
export {
  createMoney,
  addMoney,
  subtractMoney,
  multiplyMoney,
  divideMoney,
  roundMoney,
  formatMoney,
  moneyToJSON,
  moneyFromJSON,
  compareMoney,
  isPositiveMoney,
  isNegativeMoney,
  isZeroMoney
} from './decimal'

// Re-export Percentage types and functions
export type { PercentageValue } from './percentage'
export {
  createPercentage,
  createPercentageFromBasisPoints,
  createPercentageFromDecimal,
  applyPercentage,
  asMultiplier,
  addPercentage,
  subtractPercentage,
  formatPercentage,
  percentageToJSON,
  percentageFromJSON,
  asBasisPoints,
  asPercentageNotation
} from './percentage'
