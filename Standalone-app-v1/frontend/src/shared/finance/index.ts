/**
 * Finance module — public barrel.
 *
 * Exports the high-level monetary helpers designed for the component layer.
 * All calculations use decimal.js to avoid IEEE 754 floating-point artefacts.
 *
 * @example
 * import {
 *   parseMoneyFromString,
 *   fromDecimalAmount,
 *   formatMoney,
 *   formatPercentage,
 *   calculatePnL,
 * } from '@/shared/finance'
 *
 * // or via the master shared barrel:
 * import { parseMoneyFromString, calculatePnL } from '@/shared'
 */

// Types
export type { MoneyDecimal, PnLResult, DecimalInstance } from './decimalMoney'

// Construction helpers
export { parseMoneyFromString, fromDecimalAmount } from './decimalMoney'

// Formatting helpers
export { formatMoney, formatPercentage } from './decimalMoney'

// Financial calculations
export { calculatePnL } from './decimalMoney'
