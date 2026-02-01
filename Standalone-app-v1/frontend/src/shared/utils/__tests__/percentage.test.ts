/**
 * Tests for percentage.ts Percentage utilities
 * 
 * Coverage targets:
 * - Creation from percentage, basis points, and decimal notation
 * - Application to MoneyValue objects
 * - Basis points conversion
 * - Percentage arithmetic
 * - Formatting and serialization
 * - Multiplier calculation
 */

import { describe, it, expect } from 'vitest'
import Decimal from 'decimal.js'
import {
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
} from '../percentage'
import { createMoney } from '../decimal'

describe('Percentage Utilities', () => {
  describe('createPercentage', () => {
    it('should create percentage from percentage notation', () => {
      const p = createPercentage('50', 'add')
      expect(p.amount.toString()).toBe('0.5')
      expect(p.operation).toBe('add')
    })

    it('should normalize percentage to decimal notation', () => {
      const p50 = createPercentage('50', 'add')
      const p100 = createPercentage('100', 'add')
      const p1 = createPercentage('1', 'add')
      
      expect(p50.amount.toString()).toBe('0.5')    // 50% = 0.50
      expect(p100.amount.toString()).toBe('1')     // 100% = 1.00
      expect(p1.amount.toString()).toBe('0.01')    // 1% = 0.01
    })

    it('should default to "add" operation', () => {
      const p = createPercentage('50')
      expect(p.operation).toBe('add')
    })

    it('should support different operations', () => {
      const add = createPercentage('50', 'add')
      const subtract = createPercentage('50', 'subtract')
      const multiply = createPercentage('50', 'multiply')
      const divide = createPercentage('50', 'divide')
      
      expect(add.operation).toBe('add')
      expect(subtract.operation).toBe('subtract')
      expect(multiply.operation).toBe('multiply')
      expect(divide.operation).toBe('divide')
    })

    it('should handle Decimal input', () => {
      const p = createPercentage(new Decimal('50'), 'add')
      expect(p.amount.toString()).toBe('0.5')
    })
  })

  describe('createPercentageFromBasisPoints', () => {
    it('should create percentage from basis points', () => {
      const p = createPercentageFromBasisPoints('5000', 'add')  // 5000 bp = 50%
      expect(p.amount.toString()).toBe('0.5')
    })

    it('should handle basis points conversions', () => {
      const p1bp = createPercentageFromBasisPoints('1', 'add')       // 0.01%
      const p100bp = createPercentageFromBasisPoints('100', 'add')   // 1%
      const p5000bp = createPercentageFromBasisPoints('5000', 'add') // 50%
      const p10000bp = createPercentageFromBasisPoints('10000', 'add') // 100%
      
      expect(p1bp.amount.toString()).toBe('0.0001')
      expect(p100bp.amount.toString()).toBe('0.01')
      expect(p5000bp.amount.toString()).toBe('0.5')
      expect(p10000bp.amount.toString()).toBe('1')
    })

    it('should default to "add" operation', () => {
      const p = createPercentageFromBasisPoints('5000')
      expect(p.operation).toBe('add')
    })

    it('should support different operations', () => {
      const p = createPercentageFromBasisPoints('1000', 'multiply')
      expect(p.operation).toBe('multiply')
      expect(p.amount.toString()).toBe('0.1')  // 1000 bp = 10%
    })
  })

  describe('createPercentageFromDecimal', () => {
    it('should create percentage from decimal notation', () => {
      const p = createPercentageFromDecimal('0.50', 'add')
      expect(p.amount.toString()).toBe('0.5')
      expect(p.operation).toBe('add')
    })

    it('should handle decimal notations', () => {
      const p001 = createPercentageFromDecimal('0.01', 'add')    // 1%
      const p05 = createPercentageFromDecimal('0.5', 'add')      // 50%
      const p1 = createPercentageFromDecimal('1', 'add')         // 100%
      const p125 = createPercentageFromDecimal('1.25', 'add')    // 125%
      
      expect(p001.amount.toString()).toBe('0.01')
      expect(p05.amount.toString()).toBe('0.5')
      expect(p1.amount.toString()).toBe('1')
      expect(p125.amount.toString()).toBe('1.25')
    })

    it('should default to "add" operation', () => {
      const p = createPercentageFromDecimal('0.5')
      expect(p.operation).toBe('add')
    })
  })

  describe('applyPercentage', () => {
    it('should apply add operation (markup)', () => {
      const price = createMoney('100', 'USD')
      const markup = createPercentage('20', 'add')  // 20% markup
      const result = applyPercentage(price, markup)
      
      expect(result.amount.toString()).toBe('120')
      expect(result.currency).toBe('USD')
    })

    it('should apply subtract operation (discount)', () => {
      const price = createMoney('100', 'USD')
      const discount = createPercentage('10', 'subtract')  // 10% discount
      const result = applyPercentage(price, discount)
      
      expect(result.amount.toString()).toBe('90')
      expect(result.currency).toBe('USD')
    })

    it('should apply multiply operation', () => {
      const price = createMoney('100', 'USD')
      const multiplier = createPercentage('50', 'multiply')  // 50% of value
      const result = applyPercentage(price, multiplier)
      
      expect(result.amount.toString()).toBe('50')
      expect(result.currency).toBe('USD')
    })

    it('should apply divide operation', () => {
      const price = createMoney('100', 'USD')
      const divisor = createPercentage('50', 'divide')  // Divide by 50% = multiply by 2
      const result = applyPercentage(price, divisor)
      
      expect(result.amount.toString()).toBe('200')
      expect(result.currency).toBe('USD')
    })

    it('should throw error for division by zero', () => {
      const price = createMoney('100', 'USD')
      const zero = createPercentage('0', 'divide')
      
      expect(() => applyPercentage(price, zero)).toThrow('division by zero')
    })

    it('should handle 100% add (double value)', () => {
      const price = createMoney('100', 'USD')
      const add100 = createPercentage('100', 'add')
      const result = applyPercentage(price, add100)
      
      expect(result.amount.toString()).toBe('200')
    })
  })

  describe('asMultiplier', () => {
    it('should get multiplier for add operation', () => {
      const p = createPercentage('20', 'add')
      const multiplier = asMultiplier(p)
      expect(multiplier.toString()).toBe('1.2')
    })

    it('should get multiplier for subtract operation', () => {
      const p = createPercentage('20', 'subtract')
      const multiplier = asMultiplier(p)
      expect(multiplier.toString()).toBe('0.8')
    })

    it('should get multiplier for multiply operation', () => {
      const p = createPercentage('50', 'multiply')
      const multiplier = asMultiplier(p)
      expect(multiplier.toString()).toBe('0.5')
    })

    it('should get multiplier for divide operation', () => {
      const p = createPercentage('50', 'divide')
      const multiplier = asMultiplier(p)
      expect(multiplier.toString()).toBe('2')
    })

    it('should throw error for divide by zero', () => {
      const p = createPercentage('0', 'divide')
      expect(() => asMultiplier(p)).toThrow('division by zero')
    })
  })

  describe('Arithmetic Operations', () => {
    it('should add percentages with same operation', () => {
      const p1 = createPercentage('10', 'add')
      const p2 = createPercentage('5', 'add')
      const result = addPercentage(p1, p2)
      
      expect(result.amount.toString()).toBe('0.15')  // 15%
      expect(result.operation).toBe('add')
    })

    it('should subtract percentages with same operation', () => {
      const p1 = createPercentage('20', 'subtract')
      const p2 = createPercentage('5', 'subtract')
      const result = subtractPercentage(p1, p2)
      
      expect(result.amount.toString()).toBe('0.15')  // 15%
      expect(result.operation).toBe('subtract')
    })

    it('should throw error for operations mismatch in add', () => {
      const p1 = createPercentage('10', 'add')
      const p2 = createPercentage('5', 'multiply')
      
      expect(() => addPercentage(p1, p2)).toThrow(
        'Cannot add percentages with different operations'
      )
    })

    it('should throw error for operations mismatch in subtract', () => {
      const p1 = createPercentage('10', 'add')
      const p2 = createPercentage('5', 'multiply')
      
      expect(() => subtractPercentage(p1, p2)).toThrow(
        'Cannot subtract percentages with different operations'
      )
    })
  })

  describe('Formatting', () => {
    it('should format percentage with default precision', () => {
      const p = createPercentage('50', 'add')
      const formatted = formatPercentage(p)
      // Decimal removes trailing zeros, so "50" becomes "50" not "50.00"
      expect(formatted).toBe('50%')
    })

    it('should format percentage with custom precision', () => {
      const p = createPercentage('50.123456', 'add')
      const formatted = formatPercentage(p, 4)
      expect(formatted).toBe('50.1235%')
    })

    it('should format small percentages', () => {
      const p = createPercentageFromBasisPoints('1', 'add')  // 0.01%
      const formatted = formatPercentage(p, 4)
      expect(formatted).toContain('0.01%')
    })

    it('should format large percentages', () => {
      const p = createPercentage('200', 'add')  // 200%
      const formatted = formatPercentage(p)
      expect(formatted).toBe('200%')
    })

    it('should format zero percentage', () => {
      const p = createPercentage('0', 'add')
      const formatted = formatPercentage(p)
      expect(formatted).toBe('0%')
    })
  })

  describe('Serialization', () => {
    it('should serialize to JSON with decimal amount', () => {
      const p = createPercentage('50', 'add')
      const json = percentageToJSON(p)
      
      expect(json).toEqual({
        amount: '0.5',
        operation: 'add'
      })
      expect(typeof json.amount).toBe('string')
    })

    it('should deserialize from JSON', () => {
      const json = { amount: '0.5', operation: 'add' }
      const p = percentageFromJSON(json)
      
      expect(p.amount.toString()).toBe('0.5')
      expect(p.operation).toBe('add')
    })

    it('should round-trip through JSON', () => {
      const original = createPercentage('12.5', 'multiply')
      const json = percentageToJSON(original)
      const restored = percentageFromJSON(json)
      
      expect(restored.amount.toString()).toBe(original.amount.toString())
      expect(restored.operation).toBe(original.operation)
    })

    it('should throw error on invalid operation', () => {
      const json = { amount: '0.5', operation: 'invalid' }
      expect(() => percentageFromJSON(json)).toThrow('Invalid operation')
    })

    it('should deserialize with number amount', () => {
      const json = { amount: 0.5, operation: 'add' }
      const p = percentageFromJSON(json)
      
      expect(p.amount.toString()).toBe('0.5')
      expect(p.operation).toBe('add')
    })
  })

  describe('Conversion', () => {
    it('should convert to basis points', () => {
      const p1 = createPercentage('50', 'add')      // 50%
      const p100 = createPercentage('100', 'add')   // 100%
      const p001 = createPercentage('0.01', 'add')  // 0.01%
      
      expect(asBasisPoints(p1).toString()).toBe('5000')
      expect(asBasisPoints(p100).toString()).toBe('10000')
      expect(asBasisPoints(p001).toString()).toBe('1')
    })

    it('should convert to percentage notation', () => {
      const p05 = createPercentageFromDecimal('0.5', 'add')  // 0.5 in decimal = 50%
      const p1 = createPercentageFromDecimal('1', 'add')     // 1.0 in decimal = 100%
      const p0001 = createPercentageFromDecimal('0.0001', 'add') // 0.0001 = 0.01%
      
      expect(asPercentageNotation(p05).toString()).toBe('50')
      expect(asPercentageNotation(p1).toString()).toBe('100')
      expect(asPercentageNotation(p0001).toString()).toBe('0.01')
    })
  })

  describe('Complex Scenarios', () => {
    it('should calculate markup price', () => {
      const costPrice = createMoney('100', 'USD')
      const markup = createPercentage('25', 'add')  // 25% markup
      const salePrice = applyPercentage(costPrice, markup)
      
      expect(salePrice.amount.toString()).toBe('125')
    })

    it('should calculate discounted price', () => {
      const originalPrice = createMoney('100', 'USD')
      const discount = createPercentage('15', 'subtract')  // 15% off
      const discountedPrice = applyPercentage(originalPrice, discount)
      
      expect(discountedPrice.amount.toString()).toBe('85')
    })

    it('should calculate commission on transaction', () => {
      const transactionAmount = createMoney('10000', 'USD')
      const commission = createPercentage('0.5', 'multiply')  // 0.5% commission
      const commissionFee = applyPercentage(transactionAmount, commission)
      
      expect(commissionFee.amount.toString()).toBe('50')
    })

    it('should calculate total return on investment', () => {
      const investment = createMoney('1000', 'USD')
      const return_percent = createPercentage('25', 'add')  // 25% return
      const finalValue = applyPercentage(investment, return_percent)
      
      expect(finalValue.amount.toString()).toBe('1250')
    })

    it('should handle cascading percentages', () => {
      const price = createMoney('100', 'USD')
      const tax = createPercentage('10', 'add')     // 10% tax
      const priceWithTax = applyPercentage(price, tax)  // $110
      
      const discount = createPercentage('10', 'subtract')  // 10% discount
      const finalPrice = applyPercentage(priceWithTax, discount)  // $99
      
      // This demonstrates that order matters: (100 + 10%) - 10% = 99
      expect(finalPrice.amount.toString()).toBe('99')
    })

    it('should convert basis points from market data', () => {
      // Market data often uses basis points
      const spreadBps = '25'  // 25 basis points
      const spread = createPercentageFromBasisPoints(spreadBps, 'add')
      
      const bid = createMoney('100', 'USD')
      const ask = applyPercentage(bid, spread)
      
      expect(ask.amount.toString()).toBe('100.25')
    })
  })

  describe('Edge Cases', () => {
    it('should handle very small percentages', () => {
      const p = createPercentageFromBasisPoints('0.1', 'add')  // 0.001%
      expect(p.amount.toString()).toBe('0.00001')
    })

    it('should handle very large percentages', () => {
      const p = createPercentage('10000', 'add')  // 10000%
      expect(p.amount.toString()).toBe('100')
    })

    it('should handle negative percentages', () => {
      const p = createPercentage('-20', 'add')
      expect(p.amount.toString()).toBe('-0.2')
      
      const price = createMoney('100', 'USD')
      const result = applyPercentage(price, p)
      expect(result.amount.toString()).toBe('80')
    })
  })
})
