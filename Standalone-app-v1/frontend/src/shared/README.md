# Shared Module — Conventions & Architecture

`src/shared/` contains code that is **truly reusable** across multiple features. If something is only used by one feature, it belongs inside that feature folder, not here.

---

## Import Rules

```
✅  import { useDebounce } from '@/shared'
✅  import { createMoney } from '@/shared'
✅  import { parseMoneyFromString, calculatePnL, formatMoney } from '@/shared/finance'
✅  import apiClient from '@/shared/api/client'

❌  import { useDebounce } from '../../shared/hooks/index'       // internal path
❌  import { createMoney } from '@/shared/utils/decimal'         // bypass barrel
❌  import { formatMoney } from '@/shared'  // ambiguous: use @/shared/finance!
```

> **Note on `formatMoney` / `formatPercentage`**: both `utils/` and `finance/` export
> functions with these names but **different signatures**. The `utils/` versions take
> `MoneyValue` / `PercentageValue`; the `finance/` versions take `MoneyDecimal` /
> `DecimalInstance`. Import from `@/shared/finance` for the component-layer helpers.

**Always import from the public barrel `@/shared` or `@/shared/<submodule>`.**
Never import from internal paths (e.g. `@/shared/utils/decimal`).

---

## Folder Structure

| Folder | Contents |
|--------|----------|
| `api/` | Centralised Axios client (`client.ts`). All HTTP calls go through here. |
| `types/` | Generic TypeScript types: `ApiResponse<T>`, pagination helpers. |
| `utils/` | Low-level financial primitives: `createMoney`, `MoneyValue`, `PercentageValue`. All arithmetic via decimal.js. |
| `finance/` | High-level monetary helpers designed for the **component layer**: `MoneyDecimal`, `parseMoneyFromString`, `calculatePnL`, `formatMoney`, `formatPercentage`. Built on top of `utils/`. Use these in feature components. |
| `hooks/` | Generic React hooks: `useDebounce`, `useLocalStorage`. Must be framework-agnostic. |
| `components/` | Purely presentational React components: `Button`, `Modal`, `Badge`. No feature-specific API calls. |

---

## Adding New Code

### New utility function
1. Add to the appropriate file in `utils/` (or create a new file for a new domain).
2. Re-export from `utils/index.ts`.
3. The master `shared/index.ts` barrel picks it up automatically.

### New shared hook
1. Add to `hooks/index.ts` (or create a separate file for complex hooks).
2. Re-export from `hooks/index.ts`.
3. Add a unit test in `hooks/__tests__/`.

### New shared component (TASK 4.5b)
1. Create `components/<ComponentName>.tsx`.
2. Export the component and its props type.
3. Add the export to `components/index.ts`.

### New finance helper (TASK 4.5+)
1. Add to `finance/decimalMoney.ts` (or a new file for a distinct domain).
2. Re-export from `finance/index.ts`.
3. If there is no name clash with `utils/`, add a selective named re-export in `shared/index.ts`.
4. Always use `DecimalInstance` (not raw `Decimal`) for type annotations to stay compatible with `@types/decimal.js`.

---

## Anti-patterns

| ❌ Anti-pattern | ✅ Correct approach |
|-----------------|---------------------|
| Feature-specific API call in a shared component | Pass data as props; do API call in the feature hook |
| Importing from another feature inside `shared/` | `shared/` must have zero feature imports |
| Circular re-exports | Check that `shared/index.ts` does not import from feature modules |

---

## Financial Calculations (MANDATORY)

Use ONLY `decimal.js` wrappers from `@/shared/utils/financial` for any monetary or percentage calculation.

```typescript
// ✅ Correct
import { createMoney, addMoney } from '@/shared'
const total = addMoney(createMoney('100.50', 'USD'), createMoney('8.25', 'USD'))

// ❌ Forbidden — IEEE 754 floating-point loss
const total = 100.50 + 8.25  // might give 108.74999...
```

See the [full README](../README.md#calcoli-finanziari-obbligatorio) for the complete mapping table.
