# TickerTracker Frontend

> ↗ Entry point di progetto e invarianti architetturali: vedi [`../CLAUDE.md`](../CLAUDE.md) · Task ledger frontend e completed-task history: vedi [`AGENTS.md`](AGENTS.md)

TypeScript/React 18 frontend for TickerTracker v3.0, a sophisticated trading system with precise financial calculations using `decimal.js` for IEEE 754-safe arithmetic.

## Testing

```bash
npm run test           # Vitest (jsdom) — NB: senza --run entra in watch, in CI usa test:coverage
npm run test:coverage  # con coverage report (target: 80%+)
npm run lint           # ESLint
npm run type-check     # TypeScript
```

> Stato/avanzamento dei task e coverage ufficiale: [`AGENTS.md`](AGENTS.md) Progress Tracker (fonte di verità unica).

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
├── index.html                         # Vite HTML entry point
├── vite.config.ts                     # Vite + Tailwind + Vitest config
├── tsconfig.json                      # TypeScript strict + path aliases
├── postcss.config.js                  # PostCSS (autoprefixer only)
├── package.json
└── src/
    ├── vite-env.d.ts                  # import.meta.env type declarations
    ├── main.tsx                       # React entry: <AppProviders><App/>
    ├── App.tsx                        # Route definitions + RootLayout
    ├── styles/
    │   └── globals.css                # Tailwind v4 (@import "tailwindcss")
    │
    ├── app/                           # Application shell
    │   ├── index.ts                   # Barrel: AppProviders, RootLayout, AppErrorBoundary
    │   ├── components/
    │   │   └── AppErrorBoundary.tsx   # Global React Error Boundary (class component)
    │   ├── providers/
    │   │   └── index.tsx              # AppProviders (QueryClient + BrowserRouter + Toaster)
    │   ├── layout/
    │   │   └── index.tsx              # RootLayout (navigation chrome)
    │   └── router/
    │       └── index.ts               # Route tree (implemented in TASK 4.16)
    │
    ├── features/                      # Feature modules — each self-contained
    │   │                              # RULE: import only from feature/index.ts
    │   ├── estimates/                 # TASK 4.6–4.10
    │   │   ├── index.ts               # Public barrel (types + api + hooks + components)
    │   │   ├── types/index.ts         # Estimate, EstimateStatus, payloads, filters
    │   │   ├── api/index.ts           # listEstimates, createEstimate, closeEstimate…
    │   │   │   ├── queries.ts         # estimateKeys + read hooks (useEstimates, useEstimate…)
    │   │   │   └── mutations.ts       # write hooks (useCreateEstimate, useCloseEstimate…)
    │   │   ├── hooks/index.ts         # re-exports from api/ + useInfiniteEstimates
    │   │   └── components/
    │   │       ├── index.ts           # Components barrel
    │   │       ├── EstimateForm.tsx   # ✅ TASK 4.8 — create form with real-time preview
    │   │       ├── EstimateCard.tsx   # ✅ TASK 4.9 — individual estimate display card
    │   │       └── EstimateList.tsx   # ✅ TASK 4.6 — paginated and virtualized list with tracking
    │   │
    │   ├── portfolio/                 # TASK 4.11–4.12
    │   │   ├── index.ts
    │   │   ├── types/index.ts         # PortfolioSummary, PortfolioPosition…
    │   │   ├── api/index.ts           # getPortfolioSummary, getOpenPositions…
    │   │   ├── hooks/index.ts         # usePortfolioSummary, useOpenPositions…
    │   │   └── components/index.ts    # Placeholder (TASK 4.11–4.12)
    │   │
    │   ├── market-data/               # TASK 4.9, 4.13–4.14
    │   │   ├── index.ts
    │   │   ├── types/index.ts         # MarketQuote, OHLCVBar, params
    │   │   ├── api/index.ts           # getQuotes, getQuote, getHistoricalData
    │   │   ├── hooks/index.ts         # useMarketQuote, useHistoricalData…
    │   │   └── components/index.ts    # Placeholder (TASK 4.9, 4.13–4.14)
    │   │
    │   └── chat-ai/                   # TASK 4.15
    │       ├── index.ts
    │       ├── types/index.ts         # ChatMessage, ChatSession, analysis types
    │       ├── api/index.ts           # sendMessage, getChatSession, analyseEstimate
    │       ├── hooks/index.ts         # useSendMessage, useAnalyseEstimate…
    │       └── components/index.ts    # Placeholder (TASK 4.15)
    │
    └── shared/                        # Cross-feature reusable code
        ├── README.md                  # Import rules & conventions
        ├── index.ts                   # Master barrel (api + types + utils + hooks)
        ├── api/
        │   ├── client.ts              # Axios instance with interceptors
        │   └── index.ts
        ├── types/
        │   ├── api.ts                 # ApiResponse<T> + unwrapResponse<T>
        │   └── index.ts
        ├── utils/
        │   ├── decimal.ts             # Money operations (47 tests)
        │   ├── percentage.ts          # Percentage operations (48 tests)
        │   ├── financial.ts           # Barrel for financial utils
        │   ├── index.ts
        │   └── __tests__/
        │       ├── decimal.test.ts
        │       └── percentage.test.ts
        ├── hooks/
        │   ├── useApiQuery.ts         # Typed useQuery wrapper (+ showErrorToast flag)
        │   ├── useApiMutation.ts      # Typed useMutation wrapper (auto-toast on error/success)
        │   └── index.ts
        ├── ui/
        │   ├── useNotify.ts           # useNotify() hook — uniform toast API
        │   └── index.ts               # Barrel: useNotify, Notify, NotifyOptions
        └── components/
            └── index.ts               # Placeholder (TASK 4.5b)
```

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Setup

Copy `.env.example` (root project level) or create a local `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=dev-secret-key
VITE_API_TARGET=http://localhost:8000
```

> When running via Docker Compose, `VITE_API_TARGET` is automatically injected as `http://backend:8000`.

### 3. Development

```bash
npm run dev          # Vite dev server on http://localhost:3000
```

### 4. Production Build

```bash
npm run build        # TypeScript compile + Vite bundle → dist/
npm run preview      # Preview production build locally
```

### 5. Testing

Vedi la sezione [Testing](#testing) in cima — comandi e coverage. Avanzamento ufficiale in [`AGENTS.md`](AGENTS.md).

---

## Tech Stack (TASK 4.1)

| Library | Version | Purpose |
|---------|---------|---------|
| React | ^18.2.0 | UI framework |
| Vite | ^5.0.8 | Build tool (port 3000) |
| TypeScript | strict mode | Type safety |
| TailwindCSS | ^4.2.1 | Styling (via `@tailwindcss/vite`) |
| React Router | ^7 | Client-side routing |
| TanStack Query | ^5 | Server state & caching |
| Axios | ^1 | HTTP client (centralized in `shared/api/client.ts`) |
| React Hook Form | ^7 | Form management |
| Zod | ^4 | Schema validation (**use `z.string().refine()` for numeric HTML inputs**, not `z.coerce.number()`) |
| @hookform/resolvers | ^5 | Zod ↔ React Hook Form bridge |
| Recharts | ^3 | Charts & data visualization |
| date-fns | ^4 | Date formatting |
| react-hot-toast | ^2.6.0 | Toast notifications (zero deps, Tailwind v4 compatible) |
| Vitest | ^1 | Unit testing (jsdom environment) |

### TailwindCSS v4 Notes
- **No** `tailwind.config.cjs` needed — content detection is automatic
- **No** `@tailwind base/components/utilities` in CSS — use `@import "tailwindcss"` instead
- **No** `tailwindcss/postcss` subpath — configured via `@tailwindcss/vite` Vite plugin

## Path Aliases

Configured in both `tsconfig.json` and `vite.config.ts`:

| Alias | Resolves to |
|-------|-------------|
| `@/*` | `src/*` |
| `@/shared/*` | `src/shared/*` |
| `@/features/*` | `src/features/*` |
| `@/app/*` | `src/app/*` |
| `@/styles/*` | `src/styles/*` |

## Aggiungere Traduzioni (i18n)

Per aggiungere o modificare testi localizzati:
1. Aprire il file `public/locales/it/common.json`.
2. Aggiungere le nuove chiavi e le rispettive traduzioni italiane (creando una nuova cartella es. `en` e file con la stessa struttura per l'inglese).
3. Utilizzare l'hook `useTranslation('common')` nei componenti React:

```tsx
import { useTranslation } from 'react-i18next';

// Dentro il componente:
const { t } = useTranslation('common');
return <button>{t('bottoni.crea')}</button>;
```

