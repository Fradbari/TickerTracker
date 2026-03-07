# Shared Module — Conventions & Architecture

`src/shared/` contains code that is **truly reusable** across multiple features. If something is only used by one feature, it belongs inside that feature folder, not here.

---

## Import Rules

```
✅  import { useDebounce } from '@/shared'
✅  import { createMoney } from '@/shared'
✅  import apiClient from '@/shared/api/client'

❌  import { useDebounce } from '../../shared/hooks/index'   // internal path
❌  import { createMoney } from '@/shared/utils/decimal'     // bypass barrel
```

**Always import from the public barrel `@/shared` or `@/shared/<submodule>`.**
Never import from internal paths (e.g. `@/shared/utils/decimal`).

---

## Folder Structure

| Folder | Contents |
|--------|----------|
| `api/` | Centralised Axios client (`client.ts`). All HTTP calls go through here. |
| `types/` | Generic TypeScript types: `ApiResponse<T>`, pagination helpers. |
| `utils/` | Pure utility functions: `createMoney`, `formatPercentage`, etc. All financial maths lives here. |
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

### New shared component (TASK 4.5)
1. Create `components/<ComponentName>.tsx`.
2. Export the component and its props type.
3. Add the export to `components/index.ts`.

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
