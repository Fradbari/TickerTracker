/**
 * @module finance/decimalMoney
 *
 * High-level financial helpers for the TickerTracker frontend.
 * All monetary and P&L calculations use decimal.js to guarantee bit-exact
 * arithmetic — no IEEE 754 rounding artefacts (e.g. 0.1 + 0.2 === 0.3).
 *
 * This module purposely exposes a thin, opinionated API aimed at the
 * component layer. For lower-level arithmetic (add/subtract/multiply/round)
 * use the primitives in `@/shared/utils` (MoneyValue + createMoney).
 *
 * WHERE THESE HELPERS WILL BE USED (microstep 5 — deferred to TASK 4.6+):
 *   - EstimateCard (TASK 4.6): formatMoney, formatPercentage, calculatePnL
 *   - EstimateForm (TASK 4.8): parseMoneyFromString
 *   - EstimateDetail (TASK 4.7): calculatePnL, formatMoney, formatPercentage
 *   - PortfolioDashboard (TASK 4.11): calculatePnL (aggregated), formatMoney
 *   - PerformanceChart (TASK 4.12): formatPercentage (axis labels)
 *
 * No component files exist yet — implementations will import from
 * `@/shared/finance` once the feature components are scaffolded.
 *
 * @example
 * ```typescript
 * import { parseMoneyFromString, formatMoney, calculatePnL, formatPercentage } from '@/shared/finance'
 *
 * const entry   = parseMoneyFromString('10.50', 'USD')
 * const current = parseMoneyFromString('12.75', 'USD')
 * const qty     = new Decimal('100')
 *
 * const pnl = calculatePnL(entry, current, qty)
 * // pnl.absolute   → Decimal('225.00')   (absolute gain in USD)
 * // pnl.percentage → Decimal('21.42857…') (percent gain)
 *
 * console.log(formatMoney(current))          // "$12.75"
 * console.log(formatPercentage(pnl.percentage)) // "21.43%"
 * ```
 */

import Decimal from 'decimal.js'

// --------------------------------------------------------------------------
// Configure decimal.js global defaults (safe to call multiple times —
// settings are process-global but idempotent within the same values).
// ROUND_HALF_UP matches the Python backend (decimal.ROUND_HALF_UP).
//
// Note: Use Decimal.config() (alias of set()) because @types/decimal.js
// exposes config() on IDecimalStatic but not set().
// --------------------------------------------------------------------------
Decimal.config({
  precision: 28,
  rounding: Decimal.ROUND_HALF_UP,
  toExpPos: 20,
  toExpNeg: -20,
})

/**
 * TypeScript-safe Decimal instance type.
 *
 * `@types/decimal.js` declares `Decimal` as a value (`IDecimalStatic`), not a
 * class instance type. To annotate variables holding decimal.js instances,
 * use this alias — identical pattern to `utils/decimal.ts`.
 *
 * @example
 * const x: DecimalInstance = new Decimal('1.5')
 */
export type DecimalInstance = InstanceType<typeof Decimal>

// --------------------------------------------------------------------------
// Types
// --------------------------------------------------------------------------

/**
 * Represents a monetary amount with its ISO 4217 currency code.
 *
 * Always construct via {@link parseMoneyFromString} or
 * {@link fromDecimalAmount} to guarantee precision — never from raw `number`.
 */
export interface MoneyDecimal {
  /** Exact decimal amount — never a JS `number`. */
  amount: DecimalInstance
  /** ISO 4217 currency code, e.g. "USD", "EUR". */
  currency: string
}

/**
 * Result of a P&L calculation produced by {@link calculatePnL}.
 */
export interface PnLResult {
  /**
   * Absolute gain/loss in the entry currency.
   * Positive → profit; negative → loss.
   *
   * Formula: (currentPrice − entryPrice) × quantity
   */
  absolute: DecimalInstance

  /**
   * Percentage gain/loss relative to total invested capital.
   * Already expressed in percentage points (e.g. 21.43 means +21.43 %).
   * Positive → profit; negative → loss.
   *
   * Formula: ((currentPrice − entryPrice) / entryPrice) × 100
   */
  percentage: DecimalInstance
}

// --------------------------------------------------------------------------
// Construction helpers
// --------------------------------------------------------------------------

/**
 * Parses a monetary string into a {@link MoneyDecimal}.
 *
 * Strips locale formatting characters (spaces, commas, currency symbols)
 * before conversion so both "1,234.56" and "1.234,56" (European) work.
 * Always pass the raw *numeric string* from an API response to preserve
 * full precision.
 *
 * @param value    - Numeric string, optionally with thousand-separators or
 *                   currency symbols (e.g. "1,234.56", "€ 99.9", "1.234,56").
 * @param currency - ISO 4217 currency code (e.g. "USD", "EUR").
 * @returns A {@link MoneyDecimal} with the parsed amount.
 * @throws {Error} If the cleaned string cannot be parsed as a finite number.
 * @throws {Error} If `currency` is not a 3-uppercase-letter ISO 4217 code.
 *
 * @example
 * parseMoneyFromString('1,234.56', 'USD') // { amount: Decimal('1234.56'), currency: 'USD' }
 * parseMoneyFromString('99.90',    'EUR') // { amount: Decimal('99.90'),   currency: 'EUR' }
 */
export function parseMoneyFromString(value: string, currency: string): MoneyDecimal {
  validateCurrency(currency)

  // Strip everything that is not a digit, a minus sign, or a decimal point.
  // European format "1.234,56" → replace last comma with period → "1234.56"
  let cleaned = value.trim()
  // Remove locale-specific thousand separators and currency symbols
  cleaned = cleaned.replace(/[^\d,.\-]/g, '')

  // Detect European decimal notation: if last separator is a comma and
  // there is at most one comma, treat it as the decimal point.
  const hasComma  = cleaned.includes(',')
  const hasPeriod = cleaned.includes('.')
  if (hasComma && !hasPeriod) {
    // e.g. "1.234,56" was already stripped to "1234,56" → "1234.56"
    cleaned = cleaned.replace(',', '.')
  } else if (hasComma && hasPeriod) {
    // Both separators: assume European "1.234,56" → last one is decimal
    const lastComma  = cleaned.lastIndexOf(',')
    const lastPeriod = cleaned.lastIndexOf('.')
    if (lastComma > lastPeriod) {
      // Comma is decimal → remove periods (thousand sep), replace comma
      cleaned = cleaned.replace(/\./g, '').replace(',', '.')
    } else {
      // Period is decimal → remove commas (thousand sep)
      cleaned = cleaned.replace(/,/g, '')
    }
  }

  if (cleaned === '' || cleaned === '-') {
    throw new Error(`Cannot parse monetary value from empty string: "${value}"`)
  }

  const parsed = new Decimal(cleaned)
  if (!parsed.isFinite()) {
    throw new Error(`Parsed monetary value is not finite: "${value}" → "${cleaned}"`)
  }

  return { amount: parsed, currency }
}

/**
 * Constructs a {@link MoneyDecimal} directly from a {@link Decimal} instance
 * or a numeric string.
 *
 * Prefer this over the constructor when you already have a `Decimal` value
 * from intermediate calculations.
 *
 * @param amount   - Decimal instance or numeric string.
 * @param currency - ISO 4217 currency code.
 *
 * @example
 * fromDecimalAmount(new Decimal('0'), 'USD')
 */
export function fromDecimalAmount(amount: DecimalInstance | string, currency: string): MoneyDecimal {
  validateCurrency(currency)
  return {
    amount: amount instanceof Decimal ? amount : new Decimal(amount),
    currency,
  }
}

// --------------------------------------------------------------------------
// Formatting helpers
// --------------------------------------------------------------------------

/**
 * Formats a {@link MoneyDecimal} into a locale-aware currency string.
 *
 * Uses the browser's `Intl.NumberFormat` for correct symbol placement and
 * thousand-separator style.  Falls back to `"en-US"` in non-browser contexts
 * (e.g. SSR or unit-test environments).
 *
 * @param m      - Monetary value to format.
 * @param locale - BCP 47 language tag (default: `navigator.language`).
 * @returns Formatted string, e.g. `"$1,234.56"` or `"1.234,56 €"`.
 *
 * @example
 * formatMoney({ amount: new Decimal('1234.56'), currency: 'USD' })
 * // → "$1,234.56"
 *
 * formatMoney({ amount: new Decimal('1234.56'), currency: 'EUR' }, 'it-IT')
 * // → "1.234,56 €"
 */
export function formatMoney(m: MoneyDecimal, locale?: string): string {
  const lang =
    locale ??
    (typeof navigator !== 'undefined' ? navigator.language : 'en-US')

  return new Intl.NumberFormat(lang, {
    style: 'currency',
    currency: m.currency,
  }).format(m.amount.toNumber())
}

/**
 * Formats a raw {@link Decimal} percentage value for display.
 *
 * The input is expected to be already in *percentage-point* notation
 * (e.g. `21.43` for 21.43 %, NOT the decimal `0.2143`).
 * This matches the `percentage` field returned by {@link calculatePnL}.
 *
 * @param value    - Percentage in percentage-point notation (e.g. `21.43`).
 * @param decimals - Decimal places to display (default: `2`).
 * @returns Formatted string with `%` suffix (e.g. `"21.43%"` or `"-5.00%"`).
 *
 * @example
 * formatPercentage(new Decimal('21.4285714'))  // "21.43%"
 * formatPercentage(new Decimal('-5'),    1)    // "-5.0%"
 * formatPercentage(new Decimal('0'))           // "0.00%"
 */
export function formatPercentage(value: DecimalInstance, decimals: number = 2): string {
  const rounded = value.toDecimalPlaces(decimals, Decimal.ROUND_HALF_UP)
  return `${rounded.toFixed(decimals)}%`
}

// --------------------------------------------------------------------------
// Financial calculations
// --------------------------------------------------------------------------

/**
 * Calculates unrealised P&L (Profit & Loss) for a position.
 *
 * Matches the backend Python calculation exactly:
 *   - absolute:   `(currentPrice − entryPrice) × quantity`
 *   - percentage: `(currentPrice − entryPrice) / entryPrice × 100`
 *
 * Both `entry` and `current` must share the same currency.
 * `quantity` is unit-less (number of shares / contracts / units).
 *
 * @param entry    - Entry (purchase) price per unit.
 * @param current  - Current market price per unit.
 * @param quantity - Number of units held (must be positive).
 * @returns {@link PnLResult} with `absolute` and `percentage` fields.
 * @throws {Error} If currencies differ.
 * @throws {Error} If `entry.amount` is zero (cannot divide by zero).
 * @throws {Error} If `quantity` is negative.
 *
 * @example
 * const entry   = parseMoneyFromString('10.00', 'USD')
 * const current = parseMoneyFromString('12.50', 'USD')
 * const qty     = new Decimal('200')
 *
 * const { absolute, percentage } = calculatePnL(entry, current, qty)
 * // absolute   → Decimal('500.00')   ($2.50 gain × 200 shares)
 * // percentage → Decimal('25')       (25% gain)
 *
 * formatMoney({ amount: absolute, currency: 'USD' }) // "$500.00"
 * formatPercentage(percentage)                        // "25.00%"
 */
export function calculatePnL(
  entry: MoneyDecimal,
  current: MoneyDecimal,
  quantity: DecimalInstance,
): PnLResult {
  if (entry.currency !== current.currency) {
    throw new Error(
      `calculatePnL: currency mismatch — entry is ${entry.currency}, current is ${current.currency}`,
    )
  }
  if (entry.amount.isZero()) {
    throw new Error('calculatePnL: entry price must not be zero')
  }
  if (quantity.isNegative()) {
    throw new Error('calculatePnL: quantity must be non-negative')
  }

  // Absolute P&L = (currentPrice - entryPrice) * quantity
  const priceDiff = current.amount.minus(entry.amount)
  const absolute  = priceDiff.times(quantity)

  // Percentage P&L = (currentPrice - entryPrice) / entryPrice * 100
  const percentage = priceDiff.dividedBy(entry.amount).times(100)

  return { absolute, percentage }
}

// --------------------------------------------------------------------------
// Internal utilities
// --------------------------------------------------------------------------

/**
 * Validates that a currency code matches ISO 4217 (3 uppercase ASCII letters).
 *
 * @throws {Error} if the currency code is invalid.
 */
function validateCurrency(currency: string): void {
  if (!/^[A-Z]{3}$/.test(currency)) {
    throw new Error(
      `Currency must be a 3-character uppercase ISO 4217 code, received: "${currency}"`,
    )
  }
}
