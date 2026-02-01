/**
 * Decimal utilities for precise financial calculations
 * 
 * This module provides type-safe wrappers around decimal.js to handle monetary values
 * with precision, matching the backend Python implementation of Money value objects.
 * 
 * IMPORTANT: Always use createMoney() with strings for input values to avoid
 * IEEE 754 floating-point corruption before Decimal conversion.
 * 
 * Example ✅ CORRECT:
 *   const price = createMoney("123.45", "USD");
 * 
 * Example ❌ WRONG:
 *   const price = createMoney(123.45, "USD"); // May lose precision
 */

import Decimal from 'decimal.js'

/**
 * Represents a monetary value with amount and currency
 */
export interface MoneyValue {
  amount: Decimal
  currency: string
}

/**
 * Validates that currency code is exactly 3 uppercase letters (ISO 4217)
 * 
 * @param currency - Currency code to validate
 * @throws Error if currency is not valid ISO 4217 format
 */
function validateCurrency(currency: string): void {
  if (!/^[A-Z]{3}$/.test(currency)) {
    throw new Error(
      `Invalid currency code: "${currency}". Must be exactly 3 uppercase letters (ISO 4217).`
    )
  }
}

/**
 * Creates a MoneyValue with precise decimal handling
 * 
 * @param amount - Monetary amount (preferably as string to preserve precision)
 * @param currency - ISO 4217 currency code (default: "USD")
 * @returns MoneyValue object
 * @throws Error if currency format is invalid
 * 
 * @example
 * const price = createMoney("100.50", "USD");
 * const eurPrice = createMoney("99.99", "EUR");
 */
export function createMoney(
  amount: string | number | Decimal,
  currency: string = 'USD'
): MoneyValue {
  validateCurrency(currency)
  return {
    amount: new Decimal(amount),
    currency
  }
}

/**
 * Adds two monetary values
 * 
 * @param a - First monetary value
 * @param b - Second monetary value
 * @returns Sum of a and b
 * @throws Error if currencies don't match
 * 
 * @example
 * const sum = addMoney(
 *   createMoney("100.00", "USD"),
 *   createMoney("50.00", "USD")
 * ); // $150.00
 */
export function addMoney(a: MoneyValue, b: MoneyValue): MoneyValue {
  if (a.currency !== b.currency) {
    throw new Error(
      `Cannot add ${a.currency} to ${b.currency}. Convert currencies first!`
    )
  }
  return {
    amount: a.amount.plus(b.amount),
    currency: a.currency
  }
}

/**
 * Subtracts monetary value b from a
 * 
 * @param a - First monetary value (minuend)
 * @param b - Second monetary value (subtrahend)
 * @returns Difference of a - b
 * @throws Error if currencies don't match
 * 
 * @example
 * const diff = subtractMoney(
 *   createMoney("100.00", "USD"),
 *   createMoney("30.00", "USD")
 * ); // $70.00
 */
export function subtractMoney(a: MoneyValue, b: MoneyValue): MoneyValue {
  if (a.currency !== b.currency) {
    throw new Error(
      `Cannot subtract ${b.currency} from ${a.currency}. Convert currencies first!`
    )
  }
  return {
    amount: a.amount.minus(b.amount),
    currency: a.currency
  }
}

/**
 * Multiplies monetary value by a factor
 * 
 * @param money - Monetary value to multiply
 * @param factor - Multiplication factor (preferably as string)
 * @returns Multiplied monetary value
 * 
 * @example
 * const doubled = multiplyMoney(createMoney("50.00", "USD"), "2");
 * // $100.00
 */
export function multiplyMoney(
  money: MoneyValue,
  factor: string | number | Decimal
): MoneyValue {
  return {
    amount: money.amount.times(new Decimal(factor)),
    currency: money.currency
  }
}

/**
 * Divides monetary value by a divisor
 * 
 * @param money - Monetary value to divide
 * @param divisor - Division factor (preferably as string)
 * @returns Divided monetary value
 * @throws Error if divisor is zero
 * 
 * @example
 * const half = divideMoney(createMoney("100.00", "USD"), "2");
 * // $50.00
 */
export function divideMoney(
  money: MoneyValue,
  divisor: string | number | Decimal
): MoneyValue {
  const decimalDivisor = new Decimal(divisor)
  if (decimalDivisor.isZero()) {
    throw new Error('Cannot divide by zero')
  }
  return {
    amount: money.amount.dividedBy(decimalDivisor),
    currency: money.currency
  }
}

/**
 * Rounds monetary value to specified decimal places using ROUND_HALF_UP
 * 
 * This matches the backend Python implementation using ROUND_HALF_UP for
 * consistent rounding behavior across frontend and backend.
 * 
 * @param money - Monetary value to round
 * @param decimalPlaces - Number of decimal places (default: 2)
 * @returns Rounded monetary value
 * 
 * @example
 * const rounded = roundMoney(createMoney("123.456", "USD"), 2);
 * // $123.46
 */
export function roundMoney(
  money: MoneyValue,
  decimalPlaces: number = 2
): MoneyValue {
  return {
    amount: money.amount.toDecimalPlaces(decimalPlaces, Decimal.ROUND_HALF_UP),
    currency: money.currency
  }
}

/**
 * Formats monetary value for display according to locale
 * 
 * @param money - Monetary value to format
 * @param locale - BCP 47 language tag (default: navigator.language or "en-US")
 * @returns Formatted string with currency symbol (e.g., "$1,234.56")
 * 
 * @example
 * formatMoney(createMoney("1234.56", "USD"), "en-US");
 * // "$1,234.56"
 * 
 * formatMoney(createMoney("1234.56", "EUR"), "it-IT");
 * // "1.234,56 €"
 */
export function formatMoney(money: MoneyValue, locale?: string): string {
  const lang = locale || (typeof navigator !== 'undefined' ? navigator.language : 'en-US')
  
  return new Intl.NumberFormat(lang, {
    style: 'currency',
    currency: money.currency
  }).format(money.amount.toNumber())
}

/**
 * Serializes MoneyValue to JSON-compatible object
 * 
 * Amount is stored as string to preserve precision during serialization.
 * 
 * @param money - Monetary value to serialize
 * @returns Object with amount as string and currency
 * 
 * @example
 * moneyToJSON(createMoney("100.50", "USD"));
 * // { amount: "100.50", currency: "USD" }
 */
export function moneyToJSON(money: MoneyValue): {
  amount: string
  currency: string
} {
  return {
    amount: money.amount.toString(),
    currency: money.currency
  }
}

/**
 * Deserializes MoneyValue from JSON object
 * 
 * @param data - Object with amount (string or number) and currency
 * @returns MoneyValue object
 * @throws Error if data is invalid or currency is invalid
 * 
 * @example
 * moneyFromJSON({ amount: "100.50", currency: "USD" });
 * // { amount: Decimal("100.50"), currency: "USD" }
 */
export function moneyFromJSON(data: {
  amount: string | number
  currency: string
}): MoneyValue {
  return createMoney(data.amount, data.currency)
}

/**
 * Compares two monetary values
 * 
 * @param a - First monetary value
 * @param b - Second monetary value
 * @returns -1 if a < b, 0 if a === b, 1 if a > b
 * @throws Error if currencies don't match
 * 
 * @example
 * compareMoney(createMoney("100", "USD"), createMoney("50", "USD"));
 * // 1 (100 > 50)
 */
export function compareMoney(a: MoneyValue, b: MoneyValue): -1 | 0 | 1 {
  if (a.currency !== b.currency) {
    throw new Error(
      `Cannot compare ${a.currency} with ${b.currency}. Convert currencies first!`
    )
  }
  if (a.amount.lessThan(b.amount)) return -1
  if (a.amount.greaterThan(b.amount)) return 1
  return 0
}

/**
 * Checks if monetary value is positive (> 0)
 * 
 * @param money - Monetary value to check
 * @returns true if amount is greater than zero
 * 
 * @example
 * isPositiveMoney(createMoney("100.00", "USD")); // true
 * isPositiveMoney(createMoney("0.00", "USD"));   // false
 */
export function isPositiveMoney(money: MoneyValue): boolean {
  return money.amount.greaterThan(0)
}

/**
 * Checks if monetary value is negative (< 0)
 * 
 * @param money - Monetary value to check
 * @returns true if amount is less than zero
 * 
 * @example
 * isNegativeMoney(createMoney("-50.00", "USD")); // true
 */
export function isNegativeMoney(money: MoneyValue): boolean {
  return money.amount.lessThan(0)
}

/**
 * Checks if monetary value is exactly zero
 * 
 * @param money - Monetary value to check
 * @returns true if amount is exactly zero
 * 
 * @example
 * isZeroMoney(createMoney("0.00", "USD")); // true
 */
export function isZeroMoney(money: MoneyValue): boolean {
  return money.amount.isZero()
}
