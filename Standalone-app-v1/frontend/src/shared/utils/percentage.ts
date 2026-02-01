/**
 * Percentage utilities for precise financial calculations
 * 
 * This module provides type-safe wrappers around decimal.js to handle percentages
 * with precision, matching the backend Python implementation of Percentage value objects.
 * 
 * Percentages support:
 * - Basis points (1 bp = 0.01% = 0.0001 as decimal)
 * - Decimal notation (100% = 1.00, 50% = 0.50)
 * - Application to MoneyValue objects
 * - Arithmetic operations
 * 
 * IMPORTANT: Always use strings for input values to avoid IEEE 754 corruption.
 * 
 * Example ✅ CORRECT:
 *   const percent = createPercentage("50", "add")  // 50%
 *   const bps = createPercentageFromBasisPoints("5000")  // 50%
 * 
 * Example ❌ WRONG:
 *   const percent = createPercentage(50, "add")  // May lose precision
 */

import Decimal from 'decimal.js'
import type { MoneyValue } from './decimal'
import { multiplyMoney, roundMoney, createMoney } from './decimal'

/**
 * Represents a percentage value with amount and operation type
 */
export interface PercentageValue {
  amount: Decimal  // Stored as decimal: 50% = 0.50, 100% = 1.00
  operation: 'add' | 'subtract' | 'multiply' | 'divide'
}

/**
 * Creates a PercentageValue from decimal notation
 * 
 * @param amount - Percentage as decimal or string (50 for 50%, 0.5 for 50%)
 * @param operation - How to apply: 'add' | 'subtract' | 'multiply' | 'divide'
 * @returns PercentageValue object
 * 
 * @example
 * const fifty = createPercentage("50", "add");     // 50% as decimal 0.50
 * const hundred = createPercentage("100", "multiply"); // 100% = 1.00
 * const ten = createPercentage("10", "subtract");  // 10% = 0.10
 */
export function createPercentage(
  amount: string | number | Decimal,
  operation: 'add' | 'subtract' | 'multiply' | 'divide' = 'add'
): PercentageValue {
  const decimalAmount = new Decimal(amount)
  // Normalize to decimal notation: 50 → 0.50
  const normalized = decimalAmount.dividedBy(100)
  
  return {
    amount: normalized,
    operation
  }
}

/**
 * Creates a PercentageValue from basis points
 * 
 * 1 basis point (bp) = 0.01% = 0.0001 as decimal
 * 100 basis points = 1% = 0.01 as decimal
 * 10,000 basis points = 100% = 1.00 as decimal
 * 
 * @param basisPoints - Basis points value (preferably as string)
 * @param operation - How to apply: 'add' | 'subtract' | 'multiply' | 'divide'
 * @returns PercentageValue object
 * 
 * @example
 * createPercentageFromBasisPoints("5000", "add");  // 50% = 0.50
 * createPercentageFromBasisPoints("100", "add");   // 1% = 0.01
 * createPercentageFromBasisPoints("1", "multiply"); // 0.01% = 0.0001
 */
export function createPercentageFromBasisPoints(
  basisPoints: string | number | Decimal,
  operation: 'add' | 'subtract' | 'multiply' | 'divide' = 'add'
): PercentageValue {
  const bp = new Decimal(basisPoints)
  // 1 bp = 0.0001 in decimal notation
  const normalized = bp.dividedBy(10000)
  
  return {
    amount: normalized,
    operation
  }
}

/**
 * Creates a PercentageValue from decimal notation
 * 
 * @param decimal - Percentage as decimal (0.50 for 50%, 1.00 for 100%)
 * @param operation - How to apply: 'add' | 'subtract' | 'multiply' | 'divide'
 * @returns PercentageValue object
 * 
 * @example
 * createPercentageFromDecimal("0.50", "multiply");  // 50%
 * createPercentageFromDecimal("1.00", "add");       // 100%
 */
export function createPercentageFromDecimal(
  decimal: string | number | Decimal,
  operation: 'add' | 'subtract' | 'multiply' | 'divide' = 'add'
): PercentageValue {
  return {
    amount: new Decimal(decimal),
    operation
  }
}

/**
 * Applies percentage to a monetary value
 * 
 * Based on the operation type:
 * - 'add': Returns base + (base * percentage)
 * - 'subtract': Returns base - (base * percentage)
 * - 'multiply': Returns base * percentage
 * - 'divide': Returns base / percentage
 * 
 * @param money - Base monetary value
 * @param percentage - Percentage to apply
 * @returns Result of applying percentage to money
 * 
 * @example
 * const price = createMoney("100", "USD");
 * const markup = createPercentage("20", "add");     // 20% markup
 * applyPercentage(price, markup);  // $120.00
 * 
 * const discount = createPercentage("10", "subtract"); // 10% discount
 * applyPercentage(price, discount);  // $90.00
 */
export function applyPercentage(
  money: MoneyValue,
  percentage: PercentageValue
): MoneyValue {
  const multiplier = percentage.amount
  
  switch (percentage.operation) {
    case 'add':
      // base + (base * percentage)
      return multiplyMoney(money, multiplier.plus(1))
    
    case 'subtract':
      // base - (base * percentage)
      return multiplyMoney(money, new Decimal(1).minus(multiplier))
    
    case 'multiply':
      // base * percentage
      return multiplyMoney(money, multiplier)
    
    case 'divide':
      // base / percentage (handle division by zero)
      if (multiplier.isZero()) {
        throw new Error('Cannot apply percentage: division by zero')
      }
      return multiplyMoney(money, new Decimal(1).dividedBy(multiplier))
    
    default:
      const _exhaustive: never = percentage.operation
      return _exhaustive
  }
}

/**
 * Gets percentage as a decimal multiplier
 * 
 * Useful for calculations where you need just the multiplier factor.
 * For 'add' operation: 50% = 1.50 multiplier
 * For 'subtract' operation: 50% = 0.50 multiplier
 * For 'multiply' operation: 50% = 0.50 multiplier
 * For 'divide' operation: 50% = 2.00 multiplier (1 / 0.50)
 * 
 * @param percentage - Percentage value
 * @returns Multiplier as Decimal
 * 
 * @example
 * const markup = createPercentage("20", "add");
 * asMultiplier(markup);  // 1.20
 */
export function asMultiplier(percentage: PercentageValue): Decimal {
  switch (percentage.operation) {
    case 'add':
      return percentage.amount.plus(1)
    
    case 'subtract':
      return new Decimal(1).minus(percentage.amount)
    
    case 'multiply':
      return percentage.amount
    
    case 'divide':
      if (percentage.amount.isZero()) {
        throw new Error('Cannot get multiplier: division by zero')
      }
      return new Decimal(1).dividedBy(percentage.amount)
    
    default:
      const _exhaustive: never = percentage.operation
      return _exhaustive
  }
}

/**
 * Adds two percentages (only for 'add' and 'subtract' operations)
 * 
 * @param a - First percentage
 * @param b - Second percentage
 * @returns Sum of percentages
 * @throws Error if operations don't support addition
 * 
 * @example
 * const p1 = createPercentage("10", "add");
 * const p2 = createPercentage("5", "add");
 * addPercentage(p1, p2);  // 15% as decimal 0.15
 */
export function addPercentage(
  a: PercentageValue,
  b: PercentageValue
): PercentageValue {
  if (a.operation !== b.operation) {
    throw new Error(
      `Cannot add percentages with different operations: ${a.operation} and ${b.operation}`
    )
  }
  
  return {
    amount: a.amount.plus(b.amount),
    operation: a.operation
  }
}

/**
 * Subtracts percentage b from a (only for same operations)
 * 
 * @param a - First percentage (minuend)
 * @param b - Second percentage (subtrahend)
 * @returns Difference of percentages
 * @throws Error if operations don't match
 * 
 * @example
 * const p1 = createPercentage("20", "add");
 * const p2 = createPercentage("5", "add");
 * subtractPercentage(p1, p2);  // 15% as decimal 0.15
 */
export function subtractPercentage(
  a: PercentageValue,
  b: PercentageValue
): PercentageValue {
  if (a.operation !== b.operation) {
    throw new Error(
      `Cannot subtract percentages with different operations: ${a.operation} and ${b.operation}`
    )
  }
  
  return {
    amount: a.amount.minus(b.amount),
    operation: a.operation
  }
}

/**
 * Formats percentage for display
 * 
 * @param percentage - Percentage value to format
 * @param decimalPlaces - Decimal places to show (default: 2)
 * @returns Formatted string (e.g., "50.00%", "0.01%")
 * 
 * @example
 * formatPercentage(createPercentage("50", "add"));     // "50.00%"
 * formatPercentage(createPercentage("0.5", "add"), 4); // "0.50%"
 */
export function formatPercentage(
  percentage: PercentageValue,
  decimalPlaces: number = 2
): string {
  // Convert from decimal to percentage notation for display
  const percent = percentage.amount.times(100)
  const rounded = percent.toDecimalPlaces(decimalPlaces, Decimal.ROUND_HALF_UP)
  return `${rounded.toString()}%`
}

/**
 * Serializes PercentageValue to JSON-compatible object
 * 
 * @param percentage - Percentage value to serialize
 * @returns Object with amount as string and operation
 * 
 * @example
 * percentageToJSON(createPercentage("50", "add"));
 * // { amount: "0.50", operation: "add" }
 */
export function percentageToJSON(percentage: PercentageValue): {
  amount: string
  operation: string
} {
  return {
    amount: percentage.amount.toString(),
    operation: percentage.operation
  }
}

/**
 * Deserializes PercentageValue from JSON object
 * 
 * @param data - Object with amount (string/number) in decimal notation and operation
 * @returns PercentageValue object
 * @throws Error if operation is invalid
 * 
 * @example
 * percentageFromJSON({ amount: "0.50", operation: "add" });
 * // { amount: Decimal("0.50"), operation: "add" }
 */
export function percentageFromJSON(data: {
  amount: string | number
  operation: string
}): PercentageValue {
  const validOperations = ['add', 'subtract', 'multiply', 'divide']
  if (!validOperations.includes(data.operation)) {
    throw new Error(
      `Invalid operation: ${data.operation}. Must be one of: ${validOperations.join(', ')}`
    )
  }
  
  return {
    amount: new Decimal(data.amount),
    operation: data.operation as 'add' | 'subtract' | 'multiply' | 'divide'
  }
}

/**
 * Converts percentage to basis points
 * 
 * 1 basis point = 0.01% = 0.0001 as decimal
 * 
 * @param percentage - Percentage value
 * @returns Basis points as Decimal
 * 
 * @example
 * asBasisPoints(createPercentage("50", "add"));  // 5000
 * asBasisPoints(createPercentage("1", "add"));   // 100
 */
export function asBasisPoints(percentage: PercentageValue): Decimal {
  return percentage.amount.times(10000)
}

/**
 * Converts percentage to percentage notation (for display)
 * 
 * @param percentage - Percentage value
 * @returns Percentage as Decimal (0.50 becomes 50)
 * 
 * @example
 * asPercentageNotation(createPercentage("50", "add"));  // 50
 */
export function asPercentageNotation(percentage: PercentageValue): Decimal {
  return percentage.amount.times(100)
}
