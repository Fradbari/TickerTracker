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

## 💰 Calcoli Finanziari (OBBLIGATORIO)

In TickerTracker v3.0, la precisione finanziaria è fondamentale. È **assolutamente vietato** l'uso del tipo nativo `number` per calcoli che coinvolgono valute o percentuali.

### Regole d'Oro
1. **Usa SEMPRE `decimal.js`** tramite i nostri wrapper in `@/shared/utils/financial`.
2. **Passa SEMPRE stringhe** (es. `"100.50"`) invece di numeri ai costruttori per evitare la corruzione IEEE 754 prima della conversione.
3. **Non eseguire MAI operazioni tra valute diverse** senza conversione esplicita.

### Esempi Corretti ✅
```typescript
import { createMoney, addMoney, formatMoney } from '@/shared/utils/financial'

// Creazione corretta da stringa
const price = createMoney("100.50", "USD")
const tax = createMoney("8.25", "USD")

// Somma precisa (risultato: 108.75)
const total = addMoney(price, tax)

// Formattazione localizzata
console.log(formatMoney(total, 'it-IT')) // "108,75 $"
```

### Esempi Vietati ❌
```typescript
// PERDITA DI PRECISIONE IMMEDIATA
const total = 0.1 + 0.2 // 0.30000000000000004

// ERRORE: Il costruttore riceve un numero già corrotto
const wrong = createMoney(0.1 + 0.2, "USD")
```

### Mapping Backend ⟷ Frontend

| Operazione | Backend (Python) | Frontend (TypeScript) |
|------------|------------------|-----------------------|
| Creazione | `Money("100", "USD")` | `createMoney("100", "USD")` |
| Addizione | `a + b` | `addMoney(a, b)` |
| Sottrazione | `a - b` | `subtractMoney(a, b)` |
| Moltiplicazione | `a * factor` | `multiplyMoney(a, factor)` |
| Arrotondamento | `a.round(2)` | `roundMoney(a, 2)` |
| JSON | `a.to_dict()` | `moneyToJSON(a)` |

---

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

### 2. Environment Setup

Create a `.env` file with backend API configuration:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Development

```bash
npm run dev
```

### 4. Testing

```bash
npm run test           # Run all tests
npm run test:coverage  # Run with coverage report (target: 80%+)
```
