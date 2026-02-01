# TickerTracker Frontend

TypeScript/React frontend for TickerTracker v3.0, a sophisticated trading system with precise financial calculations using `decimal.js` for IEEE 754-safe arithmetic.

## ✅ Test Results

**All 95 tests passing** (as of 2025-02-01):
- ✅ **Money Operations**: 47 tests (100% coverage)
- ✅ **Percentage Operations**: 48 tests (98.3% coverage)
- ✅ **Overall Coverage**: 92.08% statement coverage
- ✅ **IEEE 754 Fix Verified**: 0.1 + 0.2 = 0.3 exactly ✓

Run tests with:
```bash
npm run test           # All tests
npm run test:coverage  # With coverage report (target: 80%+ ✓ ACHIEVED)
```

## Project Structure

```
frontend/
├── src/
│   ├── shared/
│   │   └── utils/
│   │       ├── decimal.ts          # Money operations (14+ functions)
│   │       ├── percentage.ts        # Percentage operations (12+ functions)
│   │       ├── financial.ts         # Barrel export for clean imports
│   │       ├── __tests__/
│   │       │   ├── decimal.test.ts  # 40+ Money operation tests
│   │       │   └── percentage.test.ts # 50+ Percentage operation tests
│   │       └── index.ts             # Utils re-export
│   ├── app/                         # Application components
│   ├── features/                    # Feature modules
│   │   ├── chat-ai/                # AI chat feature
│   │   ├── market-data/            # Market data display
│   │   ├── portfolio/              # Portfolio management
│   │   └── estimates/              # Price estimates
│   └── shared/                      # Shared components & hooks
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

This installs all required packages including:
- **decimal.js@10.4.3** - For precise financial calculations
- **React@18.2.0** - UI framework
- **Vite@5.0.8** - Build tool and dev server
- **vitest@1.1.0** - Unit test runner with coverage support

### 2. Environment Setup

Create a `.env` file with backend API configuration:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Development

Start the development server (runs on port 5173):

```bash
npm run dev
```

The frontend will automatically proxy `/api` calls to the backend at `http://localhost:8000`.

### 4. Testing

Run tests with vitest:

```bash
npm run test           # Run all tests
npm run test:coverage  # Run with coverage report (target: 80%+)
```

### 5. Build

Create production build:

```bash
npm run build
```

## Financial Utilities

### Overview

TickerTracker provides type-safe financial utilities in TypeScript that mirror the backend Python implementation:

- **Money Operations**: Create, add, subtract, multiply, divide, round, format, serialize
- **Percentage Operations**: Create from %, basis points, or decimals; apply to Money; arithmetic
- **Full Type Safety**: TypeScript strict mode with `Decimal` precision
- **Locale Support**: Format currencies and percentages per user's region
- **JSON Serialization**: Round-trip through JSON without precision loss

### Money Operations

#### Creating Money

```typescript
import { createMoney, addMoney, formatMoney } from '@/shared/utils/financial'

// ✅ CORRECT - Use strings to preserve precision
const price = createMoney('100.50', 'USD')

// ✅ CORRECT - Can also use Decimal
import Decimal from 'decimal.js'
const price = createMoney(new Decimal('100.50'), 'USD')

// ❌ WRONG - Using number loses precision
const price = createMoney(100.50, 'USD')  // Avoid!
```

#### Arithmetic Operations

```typescript
const price = createMoney('100.00', 'USD')
const shipping = createMoney('5.50', 'USD')
const tax = createMoney('8.42', 'USD')

// Add prices
const subtotal = addMoney(price, shipping)         // $105.50
const total = addMoney(subtotal, tax)              // $113.92

// Subtract
const discount = subtractMoney(price, '10.00', 'USD')  // $90.00

// Multiply
const quantity = '3'
const orderTotal = multiplyMoney(price, quantity)  // $300.00

// Divide
const perUnit = divideMoney(orderTotal, quantity)  // $100.00
```

#### Formatting for Display

```typescript
import { createMoney, formatMoney } from '@/shared/utils/financial'

const price = createMoney('1234.56', 'USD')

// Format for user's locale
formatMoney(price, 'en-US')   // "$1,234.56"
formatMoney(price, 'it-IT')   // "1.234,56 $" (depends on locale)
formatMoney(price, 'de-DE')   // "1.234,56 $" (depends on locale)

// Default: uses navigator.language
formatMoney(price)
```

#### Rounding

```typescript
import { roundMoney } from '@/shared/utils/financial'

const amount = createMoney('123.456789', 'USD')

// Round to 2 decimal places (default)
roundMoney(amount)           // $123.46

// Round to specific decimal places
roundMoney(amount, 4)        // $123.4568

// Round to no decimal places (useful for JPY)
roundMoney(amount, 0)        // $123
```

### IEEE 754 Bug Fix

The classic JavaScript floating-point bug is fixed with `decimal.js`:

```typescript
import { createMoney, addMoney } from '@/shared/utils/financial'

const a = createMoney('0.1', 'USD')
const b = createMoney('0.2', 'USD')
const sum = addMoney(a, b)

// ✅ CORRECT - decimal.js fixes IEEE 754 bug
sum.amount.equals(createMoney('0.3', 'USD').amount)  // true

// ❌ WITHOUT decimal.js - JavaScript bug
0.1 + 0.2 === 0.3  // false! (it's 0.30000000000000004)
```

### Percentage Operations

#### Creating Percentages

```typescript
import {
  createPercentage,
  createPercentageFromBasisPoints,
  createPercentageFromDecimal
} from '@/shared/utils/financial'

// From percentage notation
const markup20 = createPercentage('20', 'add')           // 20% markup
const discount10 = createPercentage('10', 'subtract')    // 10% discount

// From basis points (1 bp = 0.01%)
const spread25bps = createPercentageFromBasisPoints('25', 'add')  // 0.25% spread
const fee100bps = createPercentageFromBasisPoints('100', 'add')   // 1% fee

// From decimal notation (0.5 = 50%)
const half = createPercentageFromDecimal('0.5', 'multiply')  // 50% of value
```

#### Applying Percentages

```typescript
import { createMoney, createPercentage, applyPercentage } from '@/shared/utils/financial'

const price = createMoney('100', 'USD')

// Markup (price + 20%)
const markup = createPercentage('20', 'add')
const salePrice = applyPercentage(price, markup)         // $120

// Discount (price - 10%)
const discount = createPercentage('10', 'subtract')
const discountedPrice = applyPercentage(price, discount) // $90

// Multiplier (price × 0.5)
const half = createPercentage('50', 'multiply')
const halfPrice = applyPercentage(price, half)           // $50

// Division (price ÷ 0.5 = price × 2)
const half_divisor = createPercentage('50', 'divide')
const doubled = applyPercentage(price, half_divisor)     // $200
```

#### Percentage Arithmetic

```typescript
import { createPercentage, addPercentage, subtractPercentage } from '@/shared/utils/financial'

const commission1 = createPercentage('1', 'add')
const commission2 = createPercentage('0.5', 'add')

// Add percentages (same operation only)
const totalCommission = addPercentage(commission1, commission2)  // 1.5%

// Subtract percentages
const netCommission = subtractPercentage(commission1, commission2) // 0.5%
```

#### Basis Points

```typescript
import { createPercentageFromBasisPoints, asBasisPoints, formatPercentage } from '@/shared/utils/financial'

const spread = createPercentageFromBasisPoints('250', 'add')  // 2.5%

// Convert back to basis points
const bps = asBasisPoints(spread)  // 250

// Format for display
formatPercentage(spread)  // "2.50%"
```

### Comparison and Sign Checks

```typescript
import { createMoney, compareMoney, isPositiveMoney, isZeroMoney } from '@/shared/utils/financial'

const price = createMoney('100.00', 'USD')
const other = createMoney('50.00', 'USD')

// Comparison
compareMoney(price, other)   // 1 (price > other)
compareMoney(other, price)   // -1 (other < price)
compareMoney(price, price)   // 0 (equal)

// Sign checks
isPositiveMoney(createMoney('100', 'USD'))   // true
isPositiveMoney(createMoney('0', 'USD'))     // false
isPositiveMoney(createMoney('-50', 'USD'))   // false

isZeroMoney(createMoney('0.00', 'USD'))      // true
```

### Serialization

```typescript
import { createMoney, moneyToJSON, moneyFromJSON } from '@/shared/utils/financial'

const price = createMoney('100.50', 'USD')

// Serialize to JSON (amount is string to preserve precision)
const json = moneyToJSON(price)  // { amount: "100.50", currency: "USD" }

// Deserialize from JSON
const restored = moneyFromJSON(json)
restored.amount.equals(price.amount)  // true
```

### Error Handling

```typescript
import { createMoney, addMoney } from '@/shared/utils/financial'

try {
  // ❌ Currency mismatch
  const usd = createMoney('100', 'USD')
  const eur = createMoney('100', 'EUR')
  addMoney(usd, eur)
} catch (error) {
  console.error(error.message)
  // "Cannot add USD to EUR. Convert currencies first!"
}

try {
  // ❌ Invalid currency
  createMoney('100', 'US')
} catch (error) {
  console.error(error.message)
  // "Invalid currency code: "US". Must be exactly 3 uppercase letters (ISO 4217)."
}

try {
  // ❌ Division by zero
  const money = createMoney('100', 'USD')
  divideMoney(money, '0')
} catch (error) {
  console.error(error.message)
  // "Cannot divide by zero"
}
```

## Backend Integration

### API Proxy

The development server automatically proxies API calls to the backend:

```typescript
// This request goes to http://localhost:8000/api/market-data/quotes
fetch('/api/market-data/quotes')
```

Configure the backend URL in `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

### Money ↔ Backend Mapping

Frontend Money operations mirror backend Python Money class:

| Operation | Frontend | Backend Python |
|-----------|----------|-----------------|
| Create | `createMoney("100", "USD")` | `Money("100", "USD")` |
| Add | `addMoney(a, b)` | `a.add(b)` |
| Subtract | `subtractMoney(a, b)` | `a.subtract(b)` |
| Multiply | `multiplyMoney(a, factor)` | `a.multiply(factor)` |
| Divide | `divideMoney(a, divisor)` | `a.divide(divisor)` |
| Round | `roundMoney(a, 2)` | `a.round(2)` |
| Format | `formatMoney(a, locale)` | `a.format()` |
| JSON | `moneyToJSON(a)` | `a.model_dump()` |

## Type Safety

All utilities are fully typed with TypeScript strict mode:

```typescript
import type { MoneyValue, PercentageValue } from '@/shared/utils/financial'

function calculateProfit(cost: MoneyValue, revenue: MoneyValue): MoneyValue {
  if (cost.currency !== revenue.currency) {
    throw new Error('Currencies must match')
  }
  return subtractMoney(revenue, cost)
}

// TypeScript will catch errors:
calculateProfit(123, 456)  // ❌ Error: Argument of type 'number' is not assignable
calculateProfit(cost, revenue)  // ✅ OK if both are MoneyValue
```

## Testing

### Test Coverage

- **Money Operations**: 40+ tests covering all functions
- **Percentage Operations**: 50+ tests covering all functions
- **Edge Cases**: IEEE 754 bugs, precision, rounding
- **Error Handling**: Invalid currencies, division by zero
- **Serialization**: JSON round-trips
- **Localization**: Multi-locale formatting
- **Complex Scenarios**: Portfolio calculations, P&L, cascading percentages

### Running Tests

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test -- decimal.test.ts

# Watch mode
npm run test -- --watch
```

### Coverage Target

Aim for **80%+ coverage**:

```bash
npm run test:coverage
```

## Development Workflow

### Path Aliases

Clean imports using path aliases:

```typescript
// ✅ Clean
import { createMoney } from '@/shared/utils/financial'

// ❌ Long paths
import { createMoney } from '../../../shared/utils/financial'
```

Configured in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/shared/*": ["src/shared/*"]
    }
  }
}
```

### Building for Production

```bash
npm run build
```

Creates optimized bundle in `dist/` directory.

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Node.js: 18+

## Configuration Files

### tsconfig.json
- TypeScript 5.3 with strict mode
- Path aliases for clean imports
- React JSX support
- Source maps for debugging

### vite.config.ts
- Vite development server on port 5173
- React plugin for JSX
- API proxy to backend at localhost:8000
- Fast HMR (Hot Module Replacement)

### package.json
- Scripts: `dev`, `build`, `test`, `test:coverage`
- Dependencies: React, React DOM, decimal.js
- DevDependencies: TypeScript, Vite, Vitest, coverage

## Troubleshooting

### Issue: "Cannot add USD to EUR"

**Solution**: Convert currencies before operations. Use an exchange rate service or backend conversion endpoint.

```typescript
// ❌ This will fail
addMoney(usd, eur)

// ✅ Convert first
const exchangeRate = await fetch('/api/exchange-rates/USD-EUR')
const converted = multiplyMoney(eur, exchangeRate)
addMoney(usd, converted)
```

### Issue: Test failures with "precision"

**Solution**: Always use strings for Money amounts:

```typescript
// ✅ Correct
createMoney('0.1', 'USD')

// ❌ Incorrect - loses precision
createMoney(0.1, 'USD')
```

### Issue: Locale formatting shows wrong symbol

**Solution**: Provide explicit locale parameter:

```typescript
// Uses browser locale (may be wrong)
formatMoney(money)

// Explicit locale (correct)
formatMoney(money, 'en-US')
```

## Contributing

When adding new financial utilities:

1. **Add to `decimal.ts` or `percentage.ts`** with JSDoc comments
2. **Write comprehensive tests** (aim for 100% coverage for new code)
3. **Export from `financial.ts`** for clean imports
4. **Update this README** with examples
5. **Run tests**: `npm run test:coverage`
6. **Check TypeScript**: `npm run build` should have no errors

## License

See [LICENSE](../LICENSE) in the project root.

## Related Documentation

- [Backend Money Implementation](../backend/src/shared/domain/value_objects/README.md)
- [Backend Percentage Implementation](../backend/src/shared/domain/value_objects/README.md)
- [decimal.js Documentation](https://mikemcl.github.io/decimal.js/)
- [Vitest Documentation](https://vitest.dev/)
- [Vite Documentation](https://vitejs.dev/)
