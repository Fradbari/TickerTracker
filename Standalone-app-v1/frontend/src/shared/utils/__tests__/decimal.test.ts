/**
 * Tests for decimal.ts Money utilities
 * 
 * Coverage targets:
 * - IEEE 754 floating-point bug fix (0.1 + 0.2 = 0.3 exactly)
 * - Currency validation and error handling
 * - All arithmetic operations
 * - Formatting across locales
 * - Serialization round-trips
 * - Comparison operations
 */

import { describe, it, expect } from 'vitest'
import Decimal from 'decimal.js'
import {
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
} from '../decimal'

describe('Money Utilities', () => {
  describe('createMoney', () => {
    it('should create money with string amount to preserve precision', () => {
      const money = createMoney('100.50', 'USD')
      expect(money.amount.equals(new Decimal('100.50'))).toBe(true)
      expect(money.currency).toBe('USD')
    })

    it('should create money with Decimal amount', () => {
      const money = createMoney(new Decimal('100.50'), 'USD')
      expect(money.amount.equals(new Decimal('100.50'))).toBe(true)
      expect(money.currency).toBe('USD')
    })

    it('should use USD as default currency', () => {
      const money = createMoney('100.50')
      expect(money.currency).toBe('USD')
    })

    it('should throw error for invalid currency format', () => {
      expect(() => createMoney('100', 'US')).toThrow('Invalid currency code')
      expect(() => createMoney('100', 'USDA')).toThrow('Invalid currency code')
      expect(() => createMoney('100', 'usd')).toThrow('Invalid currency code')
      expect(() => createMoney('100', 'US1')).toThrow('Invalid currency code')
    })

    it('should accept valid ISO 4217 currency codes', () => {
      const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
      currencies.forEach(currency => {
        const money = createMoney('100', currency)
        expect(money.currency).toBe(currency)
      })
    })
  })

  describe('IEEE 754 Bug Fix', () => {
    it('should fix 0.1 + 0.2 = 0.3 exactly', () => {
      const a = createMoney('0.1', 'USD')
      const b = createMoney('0.2', 'USD')
      const result = addMoney(a, b)
      expect(result.amount.toString()).toBe('0.3')
      expect(result.amount.equals(new Decimal('0.3'))).toBe(true)
    })

    it('should handle many decimal places', () => {
      const money = createMoney('0.123456789', 'USD')
      expect(money.amount.toString()).toBe('0.123456789')
    })

    it('should preserve precision through multiple operations', () => {
      const a = createMoney('0.1', 'USD')
      const b = createMoney('0.2', 'USD')
      const c = createMoney('0.3', 'USD')
      
      const sum = addMoney(addMoney(a, b), c)
      expect(sum.amount.toString()).toBe('0.6')
    })
  })

  describe('addMoney', () => {
    it('should add two monetary values with same currency', () => {
      const a = createMoney('100.00', 'USD')
      const b = createMoney('50.00', 'USD')
      const result = addMoney(a, b)
      expect(result.amount.equals(new Decimal('150'))).toBe(true)
      expect(result.currency).toBe('USD')
    })

    it('should handle negative amounts', () => {
      const a = createMoney('100.00', 'USD')
      const b = createMoney('-30.00', 'USD')
      const result = addMoney(a, b)
      expect(result.amount.equals(new Decimal('70'))).toBe(true)
    })

    it('should throw error for currency mismatch', () => {
      const a = createMoney('100.00', 'USD')
      const b = createMoney('50.00', 'EUR')
      expect(() => addMoney(a, b)).toThrow(
        'Cannot add USD to EUR. Convert currencies first!'
      )
    })

    it('should preserve decimal precision', () => {
      const a = createMoney('10.55', 'USD')
      const b = createMoney('20.45', 'USD')
      const result = addMoney(a, b)
      expect(result.amount.toString()).toBe('31')
    })
  })

  describe('subtractMoney', () => {
    it('should subtract two monetary values with same currency', () => {
      const a = createMoney('100.00', 'USD')
      const b = createMoney('30.00', 'USD')
      const result = subtractMoney(a, b)
      expect(result.amount.equals(new Decimal('70'))).toBe(true)
      expect(result.currency).toBe('USD')
    })

    it('should handle negative results', () => {
      const a = createMoney('30.00', 'USD')
      const b = createMoney('100.00', 'USD')
      const result = subtractMoney(a, b)
      expect(result.amount.equals(new Decimal('-70'))).toBe(true)
    })

    it('should throw error for currency mismatch', () => {
      const a = createMoney('100.00', 'USD')
      const b = createMoney('50.00', 'EUR')
      expect(() => subtractMoney(a, b)).toThrow(
        'Cannot subtract EUR from USD. Convert currencies first!'
      )
    })
  })

  describe('multiplyMoney', () => {
    it('should multiply money by factor', () => {
      const money = createMoney('50.00', 'USD')
      const result = multiplyMoney(money, '2')
      expect(result.amount.toString()).toBe('100')
      expect(result.currency).toBe('USD')
    })

    it('should handle Decimal factor', () => {
      const money = createMoney('100.00', 'USD')
      const result = multiplyMoney(money, new Decimal('0.5'))
      expect(result.amount.toString()).toBe('50')
    })

    it('should handle decimal factors', () => {
      const money = createMoney('100.00', 'USD')
      const result = multiplyMoney(money, '1.5')
      expect(result.amount.toString()).toBe('150')
    })

    it('should preserve currency', () => {
      const money = createMoney('25.00', 'EUR')
      const result = multiplyMoney(money, '4')
      expect(result.currency).toBe('EUR')
    })
  })

  describe('divideMoney', () => {
    it('should divide money by divisor', () => {
      const money = createMoney('100.00', 'USD')
      const result = divideMoney(money, '2')
      expect(result.amount.toString()).toBe('50')
      expect(result.currency).toBe('USD')
    })

    it('should handle decimal divisors', () => {
      const money = createMoney('100.00', 'USD')
      const result = divideMoney(money, '2.5')
      expect(result.amount.toString()).toBe('40')
    })

    it('should throw error for division by zero', () => {
      const money = createMoney('100.00', 'USD')
      expect(() => divideMoney(money, '0')).toThrow('Cannot divide by zero')
      expect(() => divideMoney(money, new Decimal('0'))).toThrow('Cannot divide by zero')
    })

    it('should preserve currency', () => {
      const money = createMoney('100.00', 'GBP')
      const result = divideMoney(money, '5')
      expect(result.currency).toBe('GBP')
    })
  })

  describe('roundMoney', () => {
    it('should round to 2 decimal places by default', () => {
      const money = createMoney('123.456', 'USD')
      const result = roundMoney(money)
      expect(result.amount.toString()).toBe('123.46')
    })

    it('should use ROUND_HALF_UP for consistent rounding', () => {
      const money = createMoney('123.445', 'USD')
      const result = roundMoney(money, 2)
      expect(result.amount.toString()).toBe('123.45')
    })

    it('should support custom decimal places', () => {
      const money = createMoney('123.456789', 'USD')
      const result = roundMoney(money, 4)
      expect(result.amount.toString()).toBe('123.4568')
    })

    it('should round to 0 decimal places', () => {
      const money = createMoney('123.6', 'USD')
      const result = roundMoney(money, 0)
      expect(result.amount.toString()).toBe('124')
    })

    it('should preserve currency', () => {
      const money = createMoney('123.456', 'JPY')
      const result = roundMoney(money, 2)
      expect(result.currency).toBe('JPY')
    })
  })

  describe('formatMoney', () => {
    it('should format USD in en-US locale', () => {
      const money = createMoney('1234.56', 'USD')
      const formatted = formatMoney(money, 'en-US')
      expect(formatted).toContain('$')
      expect(formatted).toContain('1,234.56')
    })

    it('should format EUR in en-US locale', () => {
      const money = createMoney('1234.56', 'EUR')
      const formatted = formatMoney(money, 'en-US')
      expect(formatted).toContain('€')
      expect(formatted).toContain('1,234.56')
    })

    it('should format EUR in it-IT locale', () => {
      const money = createMoney('1234.56', 'EUR')
      const formatted = formatMoney(money, 'it-IT')
      expect(formatted).toContain('€')
      // Italian format may vary: "1.234,56" or "1234,56" depending on browser/OS
      expect(formatted).toMatch(/1\.?234,56/)
    })

    it('should handle negative amounts', () => {
      const money = createMoney('-100.00', 'USD')
      const formatted = formatMoney(money, 'en-US')
      expect(formatted).toContain('-')
      expect(formatted).toContain('100')
    })

    it('should handle zero', () => {
      const money = createMoney('0.00', 'USD')
      const formatted = formatMoney(money, 'en-US')
      expect(formatted).toContain('0')
    })
  })

  describe('Serialization', () => {
    it('should serialize to JSON with string amount', () => {
      const money = createMoney('100.50', 'USD')
      const json = moneyToJSON(money)
      // Decimal.toString() doesn't keep trailing zeros
      expect(json.amount).toBe('100.5')
      expect(json.currency).toBe('USD')
      expect(typeof json.amount).toBe('string')
    })

    it('should deserialize from JSON', () => {
      const json = { amount: '100.50', currency: 'USD' }
      const money = moneyFromJSON(json)
      expect(money.amount.equals(new Decimal('100.50'))).toBe(true)
      expect(money.currency).toBe('USD')
    })

    it('should deserialize with number amount', () => {
      const json = { amount: 100.5, currency: 'USD' }
      const money = moneyFromJSON(json)
      expect(money.amount.toString()).toBe('100.5')
      expect(money.currency).toBe('USD')
    })

    it('should round-trip through JSON', () => {
      const original = createMoney('123.456', 'EUR')
      const json = moneyToJSON(original)
      const restored = moneyFromJSON(json)
      expect(restored.amount.equals(original.amount)).toBe(true)
      expect(restored.currency).toBe(original.currency)
    })

    it('should throw error on invalid currency during deserialization', () => {
      const json = { amount: '100.50', currency: 'USDA' }
      expect(() => moneyFromJSON(json)).toThrow('Invalid currency code')
    })
  })

  describe('Comparison', () => {
    it('should compare money values correctly', () => {
      const a = createMoney('100.00', 'USD')
      const b = createMoney('50.00', 'USD')
      const c = createMoney('100.00', 'USD')
      
      expect(compareMoney(a, b)).toBe(1)   // a > b
      expect(compareMoney(b, a)).toBe(-1)  // b < a
      expect(compareMoney(a, c)).toBe(0)   // a === c
    })

    it('should throw error for currency mismatch', () => {
      const a = createMoney('100.00', 'USD')
      const b = createMoney('100.00', 'EUR')
      expect(() => compareMoney(a, b)).toThrow(
        'Cannot compare USD with EUR. Convert currencies first!'
      )
    })
  })

  describe('Sign Checks', () => {
    it('should detect positive money', () => {
      const positive = createMoney('100.00', 'USD')
      const zero = createMoney('0.00', 'USD')
      const negative = createMoney('-100.00', 'USD')
      
      expect(isPositiveMoney(positive)).toBe(true)
      expect(isPositiveMoney(zero)).toBe(false)
      expect(isPositiveMoney(negative)).toBe(false)
    })

    it('should detect negative money', () => {
      const positive = createMoney('100.00', 'USD')
      const zero = createMoney('0.00', 'USD')
      const negative = createMoney('-100.00', 'USD')
      
      expect(isNegativeMoney(positive)).toBe(false)
      expect(isNegativeMoney(zero)).toBe(false)
      expect(isNegativeMoney(negative)).toBe(true)
    })

    it('should detect zero money', () => {
      const positive = createMoney('100.00', 'USD')
      const zero = createMoney('0.00', 'USD')
      const negative = createMoney('-100.00', 'USD')
      
      expect(isZeroMoney(positive)).toBe(false)
      expect(isZeroMoney(zero)).toBe(true)
      expect(isZeroMoney(negative)).toBe(false)
    })

    it('should detect zero with different representations', () => {
      const zero1 = createMoney('0.00', 'USD')
      const zero2 = createMoney('0', 'USD')
      const zero3 = createMoney('0.000', 'USD')
      
      expect(isZeroMoney(zero1)).toBe(true)
      expect(isZeroMoney(zero2)).toBe(true)
      expect(isZeroMoney(zero3)).toBe(true)
    })
  })

  describe('Complex Scenarios', () => {
    it('should handle portfolio value calculation', () => {
      const position1 = createMoney('1000.00', 'USD')
      const position2 = createMoney('500.00', 'USD')
      const position3 = createMoney('-200.00', 'USD')  // Short position
      
      const total = addMoney(addMoney(position1, position2), position3)
      expect(total.amount.toString()).toBe('1300')
    })

    it('should handle P&L calculation', () => {
      const entryPrice = createMoney('100.00', 'USD')
      const exitPrice = createMoney('120.00', 'USD')
      const shares = '10'
      
      const profitPerShare = subtractMoney(exitPrice, entryPrice)
      const totalProfit = multiplyMoney(profitPerShare, shares)
      
      expect(totalProfit.amount.toString()).toBe('200')
    })

    it('should handle currency conversion scenario', () => {
      // Note: This is a mock scenario. Real conversion would involve rates.
      const usd = createMoney('100.00', 'USD')
      
      // Simulate 1 USD = 0.92 EUR
      const exchangeRate = '0.92'
      const eur = multiplyMoney(usd, exchangeRate)
      
      expect(eur.amount.toString()).toBe('92')
      expect(eur.currency).toBe('USD')  // Would be EUR in real scenario
    })
  })
})
