# Frontend - React UI & UX

> **Agente:** frontend-dev
>
> ↗ Invarianti architetturali e workflow atomico: vedi [`../CLAUDE.md`](../CLAUDE.md) · Progress Tracker globale e grafo dipendenze: vedi [`../AGENTS.md`](../AGENTS.md)

## Scope
Questa sezione contiene SOLO task per il frontend React/TypeScript:
- Feature modules: `features/estimates/`, `features/portfolio/`, `features/market-data/`, `features/chat-ai/`
- Shared: `shared/components/`, `shared/hooks/`, `shared/utils/`, `shared/api/`
- App: `app/router/`, `app/layout/`, `app/providers/`
- Configurazione: Vite, TailwindCSS, React Query, React Hook Form

**Non modificare**:
- File di backend (vedi [`../backend/AGENTS.md`](../backend/AGENTS.md))
- File di Docker/compose (vedi [`../Docker/AGENTS.md`](../Docker/AGENTS.md))
- File di test/CI (vedi [`../Docs/AGENTS.md`](../Docs/AGENTS.md))

---

# REGOLE FISSE PER LLM FRONTEND

1. **Tutti i calcoli finanziari DEVONO usare decimal.js** ([`shared/utils/financial.ts`](./src/shared/utils/financial.ts) o [`shared/finance/decimalMoney.ts`](./src/shared/finance/decimalMoney.ts))
2. **Tutte le chiamate API DEVONO passare da [`shared/api/client.ts`](./src/shared/api/client.ts)** (no fetch/axios sparso)
3. **Ogni feature è self-contained**: no import cross-feature diretti (solo via `shared/`)
4. **Componenti riutilizzabili vanno in [`shared/components/`](./src/shared/components)**
5. **Hook riutilizzabili vanno in [`shared/hooks/`](./src/shared/hooks)**
6. **Zod v4 (^4.x)**: per campi numerici da `<input>` HTML usa **`z.string().refine(val => !isNaN(parseFloat(val))...)`** — NON `z.coerce.number()` (comportamento cambiato in v4; input HTML produce sempre stringhe)
7. **Toast/notifiche**: usa sempre `useNotify()` da `@/shared/ui` — NON importare `react-hot-toast` direttamente nei componenti feature
8. **Error Boundary**: errori non catturati vengono mostrati da `AppErrorBoundary` in `src/app/components/` — non serve try/catch in ogni componente per errori React; usa `useNotify` per errori API nelle mutation

---

# SEZIONE 1: SETUP FRONTEND (TASK 1.8)

---

## TASK 1.8: Setup Wrapper TypeScript per Decimali (Frontend)

**Descrizione:** Creare wrapper TypeScript per gestione decimale precisa nel frontend usando decimal.js, garantendo coerenza con i Value Objects backend (Money, Percentage) e prevenendo bug di arrotondamento IEEE 754 (es. `0.1 + 0.2 ≠ 0.3` in JavaScript nativo).

**Microstep:**

1. **Installare dipendenze decimal.js**
   - Eseguire: `npm install decimal.js`
   - Eseguire: `npm install --save-dev @types/decimal.js`
   - Verificare che `decimal.js` sia in `dependencies` e `@types/decimal.js` in `devDependencies` del `package.json`

2. **Creare file [`frontend/src/shared/utils/decimal.ts`](../src/shared/utils/decimal.ts)**
   - Definire interface `MoneyValue` con campi: `amount: Decimal`, `currency: string`

3. **Implementare funzione `createMoney(amount: string | number | Decimal, currency?: string): MoneyValue`**
   - Default `currency = "USD"`
   - Validare che `currency` sia esattamente 3 caratteri uppercase (ISO 4217), altrimenti lanciare errore
   - Convertire `amount` in `Decimal` usando costruttore `new Decimal(amount)`

4. **Implementare funzione `addMoney(a: MoneyValue, b: MoneyValue): MoneyValue`**
   - Verificare che `a.currency === b.currency`, altrimenti lanciare errore con messaggio `"Cannot add {currency1} to {currency2}. Convert currencies first!"`
   - Ritornare nuovo `MoneyValue` con `amount` sommato usando `a.amount.plus(b.amount)`

5. **Implementare analogamente: `subtractMoney`, `multiplyMoney`, `divideMoney`**
   - `multiplyMoney` e `divideMoney` accettano secondo parametro `factor: string | number | Decimal`
   - `divideMoney` deve verificare che `divisor` non sia zero

6. **Implementare funzione `roundMoney(money: MoneyValue, decimalPlaces: number = 2): MoneyValue`**
   - Usare `money.amount.toDecimalPlaces(decimalPlaces, Decimal.ROUND_HALF_UP)` per arrotondamento bancario

7. **Implementare funzione `formatMoney(money: MoneyValue, locale?: string): string`**
   - Usare `Intl.NumberFormat` con `style: "currency"`, `currency: money.currency`
   - Default `locale = navigator.language || "en-US"`

8. **Implementare funzioni serializzazione: `moneyToJSON(money: MoneyValue)` → `{amount: string, currency: string}` e `moneyFromJSON(data)` → `MoneyValue`**
   - `amount` deve essere salvato come stringa per evitare perdita precisione

9. **Implementare funzioni comparazione: `compareMoney`, `isPositiveMoney`, `isNegativeMoney`, `isZeroMoney`**

10. **Creare file [`frontend/src/shared/utils/percentage.ts`](../src/shared/utils/percentage.ts)**
    - Definire interface `PercentageValue` con campo: `value: Decimal` (in formato decimale: `0.10 = 10%`)

11. **Implementare funzione `createPercentage(percent: string | number | Decimal): PercentageValue`**
    - Dividere input per 100: `new Decimal(percent).dividedBy(100)`

12. **Implementare funzione `createPercentageFromBasisPoints(bps: number): PercentageValue`**
    - Dividere per 10000: `100 bps = 1% = 0.01`

13. **Implementare funzione `createPercentageFromDecimal(value: string | number | Decimal): PercentageValue`**
    - Per input già in formato decimale (`0.10`)

14. **Implementare funzione `applyPercentage(percentage: PercentageValue, money: MoneyValue): MoneyValue`**
    - Usare `multiplyMoney(money, percentage.value)` da `decimal.ts`

15. **Implementare funzione `asMultiplier(percentage: PercentageValue): Decimal`**
    - Ritornare `new Decimal(1).plus(percentage.value)` per calcoli tipo "prezzo + 10%"

16. **Implementare funzioni: `addPercentage`, `subtractPercentage`, `formatPercentage(percentage, decimalPlaces = 2)`**

17. **Implementare serializzazione: `percentageToJSON` e `percentageFromJSON`**

18. **Creare barrel export [`frontend/src/shared/utils/financial.ts`](../src/shared/utils/financial.ts)**
    - Re-esportare tutti i tipi e funzioni da `decimal.ts` e `percentage.ts`
    - Aggiungere commento JSDoc che specifica questo come unico entry point per import nei componenti

19. **Configurare path alias in [`tsconfig.json`](../tsconfig.json)**
    - Aggiungere in `compilerOptions.paths`: `"@/*": ["src/*"]`, `"@/shared/*": ["src/shared/*"]`
    - Verificare che import tipo `import { createMoney } from '@/shared/utils/financial'` funzioni

20. **Creare test unitari [`frontend/src/shared/utils/__tests__/decimal.test.ts`](../src/shared/utils/__tests__/decimal.test.ts)**
    - Test per `createMoney`: verifica creazione corretta, errore su currency invalida
    - Test per `addMoney`: verifica somma corretta, errore su valute diverse
    - **Test critico JavaScript bug**: `addMoney(createMoney("0.1"), createMoney("0.2"))` deve dare esattamente `"0.3"`
    - Test per `formatMoney`: verifica locale `"en-US"` produce `"$1,234.56"` e `"it-IT"` produce `"1.234,56 €"`
    - Test per `roundMoney`: verifica arrotondamento con `ROUND_HALF_UP` (es. `123.456 → 123.46`)
    - Test per operazioni su valute diverse: verificare che lancino errori espliciti

21. **Creare test unitari [`frontend/src/shared/utils/__tests__/percentage.test.ts`](../src/shared/utils/__tests__/percentage.test.ts)**
    - Test per `createPercentage(10)` produce `value: 0.1`
    - Test per `createPercentageFromBasisPoints(100)` produce `value: 0.01`
    - Test per `applyPercentage`: `10%` di `$100` = `$10`
    - Test per `asMultiplier`: `10%` diventa moltiplicatore `1.10`
    - Test per `formatPercentage`: `10.5678%` formattato con 2 decimali = `"10.57%"`

22. **Configurare test runner in [`package.json`](../package.json)**
    - Aggiungere script: `"test": "vitest"`, `"test:coverage": "vitest --coverage"`
    - Aggiungere devDependencies: `vitest`, `@vitest/ui`, `@vitest/coverage-v8`
    - Verificare che `npm run test` esegua tutti i test senza errori
    - Verificare coverage ≥ 80% con `npm run test:coverage`

23. **Documentare nel [`frontend/README.md`](../README.md)**
    - Aggiungere sezione "💰 **Calcoli Finanziari (OBBLIGATORIO)**"
    - Includere esempio corretto (✅): uso di `createMoney` con stringhe
    - Includere esempio vietato (❌): calcoli con `number` nativo
    - Includere tabella mapping Backend Python ⟷ Frontend TypeScript per coerenza API

**Acceptance Criteria:**

- [x] `decimal.js` installato e presente in `package.json`
- [x] File `decimal.ts` creato con tutti i tipi e funzioni richiesti
- [x] File `percentage.ts` creato con tutti i tipi e funzioni richiesti
- [x] File `financial.ts` barrel export creato
- [x] Validazione `currency` verifica 3 caratteri uppercase (ISO 4217)
- [x] Operazioni tra valute diverse lanciano errore esplicito con messaggio chiaro
- [x] Arrotondamento usa `Decimal.ROUND_HALF_UP` (coerente con backend Python `money.py`)
- [x] Formattazione `formatMoney` rispetta locale (separatori migliaia, simbolo valuta)
- [x] Serializzazione JSON produce `{amount: string, currency: string}` (coerente con backend `Money.to_dict()`)
- [x] Path alias `@/shared/utils/financial` configurato e funzionante
- [x] Test unitari coprono tutti i metodi principali
- [x] Test verifica precisione: `0.1 + 0.2 = 0.3` esatto (non `0.30000000000000004`)
- [x] Test verifica errori su valute diverse e divisione per zero
- [x] Coverage test ≥ 80%
- [x] `npm run build` completa senza errori TypeScript
- [x] README aggiornato con sezione calcoli finanziari
- [x] Nessun uso di `number` nativo per calcoli monetari nel codice prodotto

---

### Istruzioni per LLM

- **Non modificare file fuori da** [`frontend/src/shared/utils/decimal.ts`](../src/shared/utils/decimal.ts), [`frontend/src/shared/utils/percentage.ts`](../src/shared/utils/percentage.ts), [`frontend/src/shared/utils/financial.ts`](../src/shared/utils/financial.ts), [`frontend/src/shared/utils/__tests__/`](../src/shared/utils/__tests__), [`frontend/package.json`](../package.json), [`frontend/tsconfig.json`](../tsconfig.json), [`frontend/README.md`](../README.md) **se non strettamente necessario**.
- Segui i microstep in ordine sequenziale e **non introdurre pattern/tecnologie non menzionati** (es. non usare librerie diverse da `decimal.js`).
- **Validazione `currency`** deve essere identica al backend: verifica che sia esattamente 3 caratteri uppercase, lancia errore con messaggio esplicito se non rispetta formato ISO 4217.
- **Arrotondamento** deve usare `Decimal.ROUND_HALF_UP` per garantire coerenza con backend Python che usa `ROUND_HALF_UP` in `money.py`.
- **Serializzazione JSON** deve produrre oggetto con `amount` come stringa (non `number`) per evitare perdita precisione durante trasporto HTTP.
- **Operazioni tra valute diverse** devono sempre lanciare errore con messaggio tipo `"Cannot {operation} {currency1} {with/from/to} {currency2}. Convert currencies first!"` - mai eseguire calcoli su valute diverse silenziosamente.
- **Preferire stringhe per input**: documentare che passare stringhe tipo `"123.45"` è preferibile a numeri `123.45` per evitare corruzione float prima della conversione in Decimal.
- **Coerenza API backend**: studiare i file [`backend/src/shared/domain/value_objects/money.py`](../../backend/src/shared/domain/value_objects/money.py) e [`backend/src/shared/domain/value_objects/percentage.py`](../../backend/src/shared/domain/value_objects/percentage.py) per garantire comportamento identico (stessi metodi, stesse validazioni, stesso output).
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con **file modificati** e **test eseguiti**, includendo risultati coverage test.

---

# SEZIONE 4: FRONTEND & UX

---

ID: TASK 4.1
Area: frontend/setup
Fase: MVP
Dipendenze: -

## TASK 4.1: Setup Progetto Frontend (Vite + React 18)

**Descrizione:** Inizializzare progetto frontend con stack moderno.

**Microstep:**

1. Creare progetto con `npm create vite@latest frontend -- --template react-ts`
2. Installare dipendenze core: `react-router-dom`, `@tanstack/react-query`, `axios`
3. Installare dipendenze UI: `tailwindcss`, `postcss`, `autoprefixer`
4. Installare dipendenze form: `react-hook-form`, `zod`, `@hookform/resolvers`
5. Installare dipendenze charts: `recharts`
6. Installare dipendenze utility: `decimal.js`, `date-fns`
7. Configurare TailwindCSS (file [`tailwind.config.cjs`](../tailwind.config.cjs))
8. Configurare path aliases in [`tsconfig.json`](../tsconfig.json) e [`vite.config.ts`](../vite.config.ts)
9. Creare struttura cartelle: [`features/`](../src/features), [`shared/`](../src/shared), [`app/`](../src/app)
10. Creare file [`README.md`](../README.md) con convenzioni

**Acceptance Criteria:**

- [x] `npm run dev` avvia dev server (porta 3000, host 0.0.0.0)
- [x] `npm run build` produce build di produzione (86 moduli, 208 kB JS, 6.49 kB CSS)
- [x] TypeScript strict mode abilitato
- [x] TailwindCSS v4 funzionante via `@tailwindcss/vite` plugin
- [x] Path aliases funzionanti (`@`, `@/shared`, `@/features`, `@/app`, `@/styles`)

**File creati/modificati (TASK 4.1):**
- `index.html` — entry HTML Vite
- `postcss.config.js` — solo autoprefixer (Tailwind v4 gestito da Vite plugin)
- `src/vite-env.d.ts` — riferimento a `vite/client` per `import.meta.env`
- `src/main.tsx` — entry React 18 con `QueryClientProvider` + `BrowserRouter`
- `src/App.tsx` — routing con React Router v7 + placeholder Dashboard
- `src/styles/globals.css` — `@import "tailwindcss"` (sintassi Tailwind v4)
- `src/shared/api/client.ts` — Axios con interceptors (API key + error normalization)
- `src/shared/api/index.ts` — barrel export
- `src/shared/types/api.ts` — `ApiResponse<T>` + `unwrapResponse<T>()`
- `src/shared/types/index.ts` — barrel export
- `vite.config.ts` — aggiunto plugin Tailwind, aliases, vitest config
- `tsconfig.json` — aggiunti path aliases `@/features/*`, `@/app/*`, `@/styles/*`
- `package.json` — aggiunte dipendenze runtime e dev (vedi sotto)

**Dipendenze aggiunte:**
- Runtime: `react-router-dom ^7`, `@tanstack/react-query ^5`, `axios ^1`, `react-hook-form ^7`, `zod ^4`, `@hookform/resolvers ^5`, `recharts ^3`, `date-fns ^4`
- Dev: `tailwindcss ^4`, `@tailwindcss/vite`, `postcss ^8`, `autoprefixer ^10`, `jsdom`

**Nota tecnica — Tailwind v4**: La sintassi PostCSS `tailwindcss/postcss` non esiste in Tailwind v4. Usare invece il plugin Vite `@tailwindcss/vite` e nel CSS `@import "tailwindcss"` (al posto di `@tailwind base/components/utilities`).

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/, frontend/package.json, frontend/vite.config.ts, frontend/tsconfig.json] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.2
Area: frontend/structure
Fase: MVP
Dipendenze: TASK 4.1

## TASK 4.2: Creazione Struttura Feature Modules

**Descrizione:** Organizzare codice frontend in moduli per funzionalità.

**Microstep:**

1. Creare cartella [`frontend/src/features/estimates/`](../src/features/estimates) con sottocartelle: `components/`, `hooks/`, `api/`, `types/`
2. Creare cartella [`frontend/src/features/portfolio/`](../src/features/portfolio) con stessa struttura
3. Creare cartella [`frontend/src/features/market-data/`](../src/features/market-data) con stessa struttura
4. Creare cartella [`frontend/src/features/chat-ai/`](../src/features/chat-ai) con stessa struttura
5. Creare cartella [`frontend/src/shared/`](../src/shared) con sottocartelle: `components/`, `hooks/`, `utils/`, `types/`, `api/`
6. Creare cartella [`frontend/src/app/`](../src/app) con sottocartelle: `router/`, `layout/`, `providers/`
7. Creare file `index.ts` barrel exports in ogni feature
8. Creare README in `shared/` che documenta regole riuso componenti

**Acceptance Criteria:**

- [x] Struttura cartelle completa (4 feature + shared + app)
- [x] Ogni feature è isolata — `index.ts` pubblico separa interno da esterno
- [x] Barrel exports configurati per tutti i moduli
- [x] `shared/README.md` documenta convenzioni (import, anti-pattern, financial rules)
- [x] Nessun import cross-feature diretto — shared come unica dipendenza condivisa

**File creati (TASK 4.2):**

Feature modules — `estimates/`:
- `src/features/estimates/types/index.ts` — tipi TypeScript allineati a backend (EstimateResponse, EstimateListResponse, CreateEstimateCommand, CloseEstimateCommand, EstimateFilters)
- `src/features/estimates/api/index.ts` — listEstimates, getEstimate, createEstimate, closeEstimate, deleteEstimate, getEstimateHistory
- `src/features/estimates/hooks/index.ts` — useEstimateList, useInfiniteEstimates, useEstimate, useCreateEstimate, useCloseEstimate, useDeleteEstimate + ESTIMATE_KEYS factory
- `src/features/estimates/components/index.ts` — placeholder (TASK 4.6–4.10)
- `src/features/estimates/index.ts` — public barrel

Feature modules — `portfolio/`, `market-data/`, `chat-ai/` (stessa struttura):
- `types/index.ts`, `api/index.ts`, `hooks/index.ts`, `components/index.ts`, `index.ts`

Shared additions:
- `src/shared/components/index.ts` — placeholder (TASK 4.5)
- `src/shared/hooks/index.ts` — `useDebounce<T>()` + `useLocalStorage<T>()` implementati
- `src/shared/index.ts` — master barrel (api, types, utils, hooks)
- `src/shared/README.md` — convenzioni import, anti-pattern, financial rules

App subfolders:
- `src/app/providers/index.tsx` — `AppProviders` component (QueryClient + BrowserRouter + StrictMode) + singleton `queryClient` esportato
- `src/app/layout/index.tsx` — `RootLayout` component (placeholder per TASK 4.16)
- `src/app/router/index.ts` — placeholder con piano route (TASK 4.16)
- `src/app/index.ts` — barrel

Refactoring:
- `src/main.tsx` — semplificato: usa `<AppProviders>` da `./app/providers`
- `src/App.tsx` — usa `<RootLayout>` da `./app/layout`

**Verifica:** `npm run build` → ✅ 88 moduli, build in 1.27s; `npm test` → ✅ 95/95

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.3
Area: frontend/shared
Fase: MVP
Dipendenze: TASK 4.2

## TASK 4.3: Configurazione React Query & API Client

**Descrizione:** Configurare TanStack Query v5 con QueryClient ottimizzato, ReactQueryDevtools, e hook custom per data-fetching e mutation uniformi. L'API client Axios era già stato creato in TASK 4.1.

**Microstep:**

1. Installare `@tanstack/react-query-devtools` ✅
2. Creare [`src/app/providers/QueryProvider.tsx`](../src/app/providers/QueryProvider.tsx) con QueryClient configurato ✅
3. Configurare QueryClient defaults: staleTime 5min, gcTime 30min, retry 3 con backoff esponenziale, refetchOnWindowFocus true ✅
4. Montare `<ReactQueryDevtools>` solo in `import.meta.env.DEV` ✅
5. Aggiornare [`src/app/providers/index.tsx`](../src/app/providers/index.tsx) a usare `<QueryProvider>` ✅
6. Creare [`src/shared/hooks/useApiQuery.ts`](../src/shared/hooks/useApiQuery.ts) — wrapper `useQuery` v5 con `throwOnError: false` ✅
7. Creare [`src/shared/hooks/useApiMutation.ts`](../src/shared/hooks/useApiMutation.ts) — wrapper `useMutation` con error/success logging (placeholder toast) ✅
8. Aggiornare barrel exports: `shared/hooks/index.ts`, `shared/index.ts`, `app/index.ts` ✅

**Acceptance Criteria:**

- [x] QueryClient configurato (staleTime 5min, gcTime 30min, retry backoff)
- [x] Devtools visibili in dev (bottom-right, lazy-loaded, tree-shaken in prod)
- [x] `useApiQuery` semplifica uso con `throwOnError: false` default
- [x] `useApiMutation` gestisce errori uniformemente (console.warn placeholder per toast)
- [x] `npm run build` → ✅ 98 moduli, 0 errori TypeScript
- [x] `npm test` → ✅ 95/95

**File creati/modificati (TASK 4.3):**
- `src/app/providers/QueryProvider.tsx` — QueryClient singleton + QueryProvider component + ReactQueryDevtools
- `src/app/providers/index.tsx` — aggiornato: usa `<QueryProvider>`, re-esporta `queryClient`
- `src/shared/hooks/useApiQuery.ts` — `useApiQuery<TData, TQueryKey>()` wrapper
- `src/shared/hooks/useApiMutation.ts` — `useApiMutation<TData, TVariables>()` con `successMessage`, `errorMessage`
- `src/shared/hooks/index.ts` — aggiunto export `useApiQuery`, `useApiMutation`
- `src/shared/index.ts` — aggiunto `useApiQuery`, `useApiMutation` al barrel
- `src/app/index.ts` — aggiunto export `QueryProvider`
- `package.json` — aggiunta dev dipendenza `@tanstack/react-query-devtools@5.91.3`

**Nota tecnica — callback spread in v5**: In `@tanstack/react-query` v5, le callback `onError`/`onSuccess` di `UseMutationOptions` (ereditato da `MutationObserverOptions`) accettano un 4° argomento `Mutation`. L'uso di `...args` (rest params) è il pattern corretto per forward-compatibility.

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/app/providers/, frontend/src/shared/hooks/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.4
Area: frontend/shared
Fase: MVP
Dipendenze: TASK 4.3

## TASK 4.4: Definizione Types e API Response Models

> ✅ **COMPLETATO** — `ApiError`, typed helpers (`get/post/patch/del`), `isApiError` guard implementati. Build: 98 moduli. Test: 95/95. Nessun `any` type.

**Descrizione:** Creare types TypeScript per modelli domain e API responses.

**Microstep:**

1. ~~Creare file `frontend/src/shared/types/api.ts`~~ — già presente da TASK 4.1 con `ApiResponse<T>` + `unwrapResponse<T>`
2. ~~Definire type `ApiResponse<T>`~~ — già presente
3. Definire type `ApiError`: `{code: string, message: string, details?: unknown, status?: number, trace_id?: string}` — ✅ in `src/shared/api/types.ts`
4. Implementare typed helpers `get<T>`, `post<T>`, `patch<T>`, `del<T>` — ✅ in `src/shared/api/types.ts`
5. Implementare type guard `isApiError(value: unknown)` — ✅
6. Aggiornare barrel `src/shared/api/index.ts` con tutti gli export — ✅
7. Aggiornare `src/shared/index.ts` con gli helper tipizzati — ✅
8. Interceptor Axios in `client.ts` produce `ApiError` strutturato — ✅

**Acceptance Criteria:**

- [x] `ApiError` interface definita con tutti i campi (`code`, `message`, `details`, `status`, `trace_id`)
- [x] Typed helpers funzionanti — unwrappano `ApiResponse<T>.data` automaticamente
- [x] `isApiError` type-guard per i catch block
- [x] Nessun `any` type
- [x] Documentazione JSDoc per types e helper functions
- [x] Build: 98 moduli, 0 errori TypeScript
- [x] Test: 95/95 passati

**File creati/modificati (TASK 4.4):**
- `src/shared/api/client.ts` — request interceptor (X-API-Key, Authorization Bearer, X-Correlation-ID) + error interceptor (→ `ApiError`)
- `src/shared/api/types.ts` — `ApiError`, `isApiError`, `get<T>`, `post<T>`, `patch<T>`, `del<T>`
- `src/shared/api/index.ts` — barrel aggiornato con tutti gli export
- `src/shared/index.ts` — master barrel aggiornato

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/types/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.5
Area: frontend/shared/finance
Fase: MVP
Dipendenze: TASK 4.4

## TASK 4.5: Wrapper Decimale per Calcoli Finanziari

> ✅ **COMPLETATO** — `MoneyDecimal`, `PnLResult`, `DecimalInstance` + tutti gli helper implementati. Build: 98 moduli. Test: 95/95. Nessun calcolo usa `number` JS puro.

**Descrizione:** Wrapper decimale preciso (decimal.js) per tutti i calcoli monetari e percentuali del frontend, eliminando gli errori IEEE 754.

**Note tecniche:**
- `@types/decimal.js` (vecchio) coesiste con i tipi built-in di decimal.js 10+, causando conflitti
- `Decimal` è esposto come `declare var Decimal: IDecimalStatic` → non usabile come tipo diretto
- Soluzione: `export type DecimalInstance = InstanceType<typeof Decimal>` (come in `utils/decimal.ts`)
- `Decimal.set()` non esiste su `IDecimalStatic` → usare `Decimal.config()` (alias)
- `formatMoney` e `formatPercentage` hanno firme diverse tra `utils/` (prendono `MoneyValue`/`PercentageValue`) e `finance/` (prendono `MoneyDecimal`/`DecimalInstance`) → NON re-esportati dal master barrel `shared/index.ts` per evitare conflitti; importare da `@/shared/finance` direttamente

**Acceptance Criteria:**

- [x] `MoneyDecimal` type: `{ amount: DecimalInstance, currency: string }`
- [x] `PnLResult` type: `{ absolute: DecimalInstance, percentage: DecimalInstance }`
- [x] `DecimalInstance` type alias esportato per type-safety downstream
- [x] `parseMoneyFromString(value, currency)` — gestisce locale EU e US, strisce simboli valuta
- [x] `fromDecimalAmount(amount, currency)` — costruttore da `DecimalInstance`/stringa già sicura
- [x] `formatMoney(m: MoneyDecimal, locale?) ` — `Intl.NumberFormat` localizzato
- [x] `formatPercentage(value: DecimalInstance, decimals?)` — percentage-point notation, `ROUND_HALF_UP`
- [x] `calculatePnL(entry, current, quantity)` — `absolute = (current−entry)×qty`, `percentage = (current−entry)/entry×100`
- [x] Nessun calcolo usa `number` JS puro
- [x] `Decimal.config()` configura precision=28, ROUND_HALF_UP, toExpPos=20, toExpNeg=−20
- [x] Build: 98 moduli, 0 errori TypeScript
- [x] Test: 95/95 passati

**File creati/modificati (TASK 4.5):**
- `src/shared/finance/decimalMoney.ts` ← **NUOVO** — implementazione completa
- `src/shared/finance/index.ts` ← **NUOVO** — barrel del modulo
- `src/shared/index.ts` — aggiunto re-export selettivo di `finance/` (senza conflitti di nome)

---

ID: TASK 4.5b
Area: frontend/shared
Fase: MVP
Dipendenze: TASK 4.5

## TASK 4.5b: Creazione Componenti UI Shared

**Descrizione:** Implementare componenti riutilizzabili base per l'UI.

**Microstep:**

1. Creare file [`frontend/src/shared/components/Button.tsx`](../src/shared/components/Button.tsx): varianti primary/secondary/danger, sizes sm/md/lg
2. Creare file [`frontend/src/shared/components/Input.tsx`](../src/shared/components/Input.tsx): supporto error state, label, helper text
3. Creare file [`frontend/src/shared/components/Card.tsx`](../src/shared/components/Card.tsx): container con padding/shadow
4. Creare file [`frontend/src/shared/components/Badge.tsx`](../src/shared/components/Badge.tsx): status badge (open, closed, profit, loss)
5. Creare file [`frontend/src/shared/components/Spinner.tsx`](../src/shared/components/Spinner.tsx): loading indicator
6. Creare file [`frontend/src/shared/components/Toast.tsx`](../src/shared/components/Toast.tsx): notification system
7. Creare file [`frontend/src/shared/components/Modal.tsx`](../src/shared/components/Modal.tsx): dialog generico
8. Implementare storybook per ogni componente (opzionale)

**Acceptance Criteria:**

- [ ] Componenti seguono design system Tailwind
- [ ] Props tipizzati con TypeScript
- [ ] Accessibilità (ARIA labels, keyboard navigation)
- [ ] Responsive su mobile
- [ ] Documentazione props con JSDoc

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/components/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.6-hooks
Area: frontend/estimates/api
Fase: MVP
Dipendenze: TASK 4.5

## TASK 4.6-hooks: Implementazione API Hooks per Estimates

> ✅ **COMPLETATO** — `api/queries.ts` + `api/mutations.ts` creati. `hooks/index.ts` refactored come barrel. Build: 98 moduli. Test: 95/95.

**Descrizione:** Creare hook React Query per operazioni su stime (read e write), co-locati nel layer API per discoverability.

**Acceptance Criteria:**

- [x] `estimateKeys` query-key factory con: `all`, `list(filters)`, `detail(id)`, `history(id)`
- [x] `useEstimates(filters?)` — lista con filtri encodati nella query key
- [x] `useEstimate(id)` — singola stima, `enabled: Boolean(id)`
- [x] `useEstimateHistory(id)` — audit trail, `useQuery<unknown>`, `enabled: Boolean(id)`
- [x] `useCreateEstimate()` — POST, invalida `estimateKeys.all` on success
- [x] `useCloseEstimate()` — PATCH /close, invalida `all` + `detail(id)` on success
- [x] `useDeleteEstimate()` — soft-delete, invalida `estimateKeys.all` on success
- [x] `useUpdateEstimate()` — placeholder, rigetta con Error esplicito (backend endpoint non esiste)
- [x] `hooks/index.ts` refactored: re-esporta da `api/queries` e `api/mutations`; `useInfiniteEstimates` rimasto in hooks
- [x] Feature barrel aggiornato con tutti gli hook
- [x] Build: 98 moduli, 0 errori TS
- [x] Test: 95/95

**Note tecniche:**
- Circolare ESM tra `api/index.ts` → `queries.ts` → `api/index.ts` è safe: le funzioni HTTP sono hoisted e disponibili prima che `export * from './queries'` sia raggiunto; Vite/Rollup e TypeScript lo gestiscono correttamente
- `useUpdateEstimate` non ha endpoint corrispondente nel backend MVP: rigetta con `Promise.reject(new Error(...))` per segnalarlo chiaramente agli sviluppatori
- `ESTIMATE_KEYS` (uppercase) rimane come alias `@deprecated` per backward compat
- `useEstimateList` rimane come alias `@deprecated` per `useEstimates`

**File creati/modificati (TASK 4.6-hooks):**
- `src/features/estimates/api/queries.ts` ← **NUOVO** — `estimateKeys`, `useEstimates`, `useEstimate`, `useEstimateHistory`
- `src/features/estimates/api/mutations.ts` ← **NUOVO** — `useCreateEstimate`, `useCloseEstimate`, `useDeleteEstimate`, `useUpdateEstimate`
- `src/features/estimates/api/index.ts` — aggiunto `export * from './queries'` + `export * from './mutations'`
- `src/features/estimates/hooks/index.ts` — refactored: re-esporta da api/, aggiunge `useInfiniteEstimates` locale
- `src/features/estimates/index.ts` — feature barrel aggiornato con tutti gli hook

---

ID: TASK 4.7-ui
Area: frontend/app + frontend/shared/ui
Fase: MVP
Dipendenze: TASK 4.5

## TASK 4.7-ui: Error Boundary & Toast Notifications

> ✅ **COMPLETATO** — `AppErrorBoundary`, `useNotify` e integrazione `react-hot-toast` completati. Build: 101 moduli. Test: 95/95.

**Descrizione:** Aggiungere gestione globale degli errori React (class component Error Boundary) e notifiche toast uniformi via `react-hot-toast`. Qualsiasi errore non gestito nel component tree mostra una schermata di fallback con opzione Riprova / Ricarica. Errori API e successi mutation vengono surfacati automaticamente come toast.

**Acceptance Criteria:**

- [x] `react-hot-toast@^2.6.0` installato
- [x] `AppErrorBoundary` class component (React limitazione: no function components) in `src/app/components/AppErrorBoundary.tsx`
  - `getDerivedStateFromError` → `{ hasError, error }`
  - `componentDidCatch` → `console.error` per monitoring tools
  - Fallback UI: icona warning + messaggio + pulsanti "Riprova" (reset state) + "Ricarica pagina" (`window.location.reload()`)
  - Dettaglio tecnico (`<details>`) visibile solo in `import.meta.env.DEV`
  - Props: `children: ReactNode`, `fallback?: ReactNode`
- [x] `useNotify()` hook in `src/shared/ui/useNotify.ts`
  - `success(msg, opts?)` — toast verde, 3 000 ms
  - `error(msg, opts?)` — toast rosso, 5 000 ms
  - `info(msg, opts?)` — toast neutro, 3 000 ms
  - `dismiss(id?)` — rimuove toast
  - `opts.id` → deduplicazione (react-hot-toast aggiorna il toast invece di stackare)
- [x] `<Toaster />` aggiunto in `AppProviders` (fuori da `AppErrorBoundary` così funziona anche durante crash)
- [x] `useApiMutation` aggiornato: sostituisce `console.warn/info` con `notify.error(msg, { id: ApiError.code })` / `notify.success(msg)`
- [x] `useApiQuery` aggiornato: nuovo flag `showErrorToast?: boolean` + `useEffect` watching `result.error` (TanStack Query v5 ha rimosso `onError` da `useQuery`)
- [x] `app/index.ts` esporta `AppErrorBoundary`
- [x] `shared/index.ts` esporta `useNotify`, `Notify`, `NotifyOptions` da `./ui`
- [x] Build: 101 moduli, 0 errori TS
- [x] Test: 95/95

**Note tecniche:**
- `AppErrorBoundary` DEVE essere class component: `getDerivedStateFromError` e `componentDidCatch` non esistono per function components
- `<Toaster />` è sibling di `{children}` (non dentro `AppErrorBoundary`) per garantire che le notifiche toast funzionino anche durante un crash del component tree figlio
- TanStack Query v5 ha rimosso `onError` da `useQuery`. L'error notification in `useApiQuery` usa `useEffect` watching `result.error` (pattern raccomandato)
- `error.code` come toast `id` garantisce deduplicazione: se la stessa richiesta fallisce 3 volte con `NETWORK_ERROR`, si vede 1 solo toast (aggiornato in-place)
- `useNotify()` non dipende da Context: tutti i metodi chiamano direttamente l'istanza singleton di react-hot-toast

**File creati/modificati (TASK 4.7-ui):**
- `src/app/components/AppErrorBoundary.tsx` ← **NUOVO** — class component + fallback UI
- `src/shared/ui/useNotify.ts` ← **NUOVO** — hook toast
- `src/shared/ui/index.ts` ← **NUOVO** — barrel `ui/`
- `src/app/providers/index.tsx` — aggiunto `<Toaster />` + `<AppErrorBoundary>` wrapping children
- `src/app/index.ts` — aggiunta export `AppErrorBoundary`
- `src/shared/index.ts` — aggiunta export `useNotify`, `Notify`, `NotifyOptions`
- `src/shared/hooks/useApiMutation.ts` — sostituisce console.warn/info con notify.error/success
- `src/shared/hooks/useApiQuery.ts` — aggiunge `showErrorToast` + `useEffect` per auto-toast errori query



## TASK 4.6: Implementazione EstimateList Component

ID: TASK 4.6
Area: frontend/estimates
Fase: MVP
Dipendenze: TASK 4.6-hooks

> Nota: 4.5b NON è prerequisito di 4.6: task completato tramite hook proprio (useEstimates) prima che 4.5b esistesse — dipendenza storica da 4.6-hooks confermata da microstep interni.

**Descrizione:** Componente per visualizzare lista stime con filtri.

**Microstep:**

1. Creare file [`frontend/src/features/estimates/components/EstimateList.tsx`](../src/features/estimates/components/EstimateList.tsx)
2. Implementare fetching data con React Query: `useEstimates(filters)` in [`frontend/src/features/estimates/hooks/useEstimates.ts`](../src/features/estimates/hooks/useEstimates.ts)
3. Implementare UI: tabella con colonne (Ticker, Direction, Entry Price, Current Price, PnL, Status)
4. Implementare filtri: status (open/closed), ticker search
5. Implementare ordinamento: click su header colonna
6. Implementare paginazione: prev/next buttons
7. Implementare loading state (Spinner) e empty state
8. Implementare error handling con Toast

**Acceptance Criteria:**

- [ ] Lista stime visibile
- [ ] Filtri funzionanti
- [ ] Ordinamento funzionante
- [ ] Paginazione funzionante
- [ ] Loading/error/empty states gestiti
- [ ] Responsive su mobile (tabella -> card list)

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/components/EstimateList.tsx, frontend/src/features/estimates/hooks/useEstimates.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.7
Area: frontend/estimates
Fase: MVP
Dipendenze: TASK 4.6

## TASK 4.7: Implementazione EstimateDetail Component

**Descrizione:** Componente per visualizzare dettaglio singola stima.

**Microstep:**

1. Creare file [`frontend/src/features/estimates/components/EstimateDetail.tsx`](../src/features/estimates/components/EstimateDetail.tsx)
2. Implementare fetching con React Query: `useEstimate(id)` in [`frontend/src/features/estimates/hooks/useEstimate.ts`](../src/features/estimates/hooks/useEstimate.ts)
3. Implementare UI: sezione info (ticker, direction, entry, stop, target)
4. Implementare sezione PnL: grafico price history, PnL realizzato/non realizzato
5. Implementare azioni: Close Estimate button (se aperta)
6. Implementare chart con Recharts: candlestick o line chart
7. Implementare refresh automatico ogni 60s per prezzi live
8. Implementare skeleton loading per chart

**Acceptance Criteria:**

- [ ] Dettaglio completo visibile
- [ ] Chart prezzi funzionante
- [ ] Refresh automatico prezzi
- [ ] Close action funzionante
- [ ] Loading states per chart e dati
- [ ] Responsive layout

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/components/EstimateDetail.tsx, frontend/src/features/estimates/hooks/useEstimate.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.8
Area: frontend/estimates
Fase: MVP
Dipendenze: TASK 4.5

## TASK 4.8: Implementazione EstimateForm Component

> ✅ **COMPLETATO** — `EstimateForm` creato con Zod v4 + react-hook-form v7, preview Decimal, toast errori. Build: 101 moduli (tsc clean). Test: 95/95.

**Descrizione:** Form completo per creare nuova stima di trading con validazione client-side, preview calcoli in tempo reale e gestione errori API.

**Acceptance Criteria:**

- [x] Zod schema: `ticker` (uppercase, 1-10 alfanumerici+punto), `direction` (LONG/SHORT), `entry_price` (preview-only, > 0), `target_profit_percent` (0.01–100), `stop_loss_percent` (0.01–100), `notes` (opzionale)
- [x] Tutti i campi numerici usano `z.string().refine()` (Zod v4 pattern: no `z.coerce.number()`)
- [x] LONG/SHORT toggle — LONG verde smeraldo, SHORT rosso, `aria-pressed` accessibile
- [x] Campo ticker: auto-uppercase real-time via `onChange` override + `register()` combinato
- [x] Campo `entry_price` chiaramente marcato come "solo per il preview — non inviato all'API"
- [x] Preview in tempo reale via `watch()` + `useMemo` + arithmetic Decimal:
  - LONG: `targetPrice = entry × (1 + profit/100)`, `stopPrice = entry × (1 − stop/100)`
  - SHORT: `targetPrice = entry × (1 − profit/100)`, `stopPrice = entry × (1 + stop/100)`
  - Preview nascosto finché almeno un valore è disponibile
  - `aria-live="polite"` per accessibilità screen reader
- [x] Submit via `useCreateEstimate()` con `onSuccess(id)` callback per redirect/modal close
- [x] Submit button disabilitato durante mutation + spinner animato
- [x] Errori inline per ogni campo (id + aria-describedby per accessibilità)
- [x] Errori API via `useNotify().error(msg, { id: error.code })` con deduplicazione
- [x] `onCancel` prop opzionale per pulsante Annulla
- [x] `components/index.ts` aggiornato con `export { EstimateForm }` + `export type { EstimateFormProps }`
- [x] Feature barrel `estimates/index.ts` aggiornato
- [x] Build: 101 moduli, 0 errori TS
- [x] Test: 95/95

**Note tecniche:**
- `ticker_id` in `CreateEstimatePayload` è UUID. Poiché `/api/tickers/search` non esiste nel MVP, il ticker symbol viene usato come placeholder. `// TODO: replace with UUID from /api/tickers/search (TASK 4.x)`
- `notes` è presente nel form per UX ma non in `CreateEstimatePayload`. `// TODO: map to notes field when backend schema is extended (TASK 4.x)`
- `useCreateEstimate` usa `useMutation` raw (non `useApiMutation`) quindi gli errori API sono gestiti manualmente con `useNotify()` nell'`onError` callback del form
- `entry_price` non è inviato all'API — il backend usa il prezzo di mercato corrente al momento della creazione
- Zod v4: `z.string().refine()` mantiene tipo `string` come output → nessuna conversione necessaria per `CreateEstimatePayload` che già usa stringhe per i campi percentuale
- Style functions (`inputClass`, `directionButtonClass`) evitano la concatenazione dinamica di classe Tailwind che potrebbe non essere rilevata da purging

**File creati/modificati (TASK 4.8):**
- `src/features/estimates/components/EstimateForm.tsx` ← **NUOVO** — componente completo
- `src/features/estimates/components/index.ts` — aggiunto `export { EstimateForm }` + `export type { EstimateFormProps }`
- `src/features/estimates/index.ts` — aggiunto export `EstimateForm`, `EstimateFormProps`

---

### Istruzioni per LLM
- Non modificare file fuori da `src/features/estimates/components/EstimateForm.tsx` se non strettamente necessario.
- Il campo `ticker_id` in `CreateEstimatePayload` è un UUID — quando `/api/tickers/search` sarà disponibile, sostituire il ticker symbol con il UUID risolto.
- Il campo `notes` non è in `CreateEstimatePayload` MVP — tenerlo nel form per UX futura.
- Il preview usa `formatMoney` da `@/shared/finance` (con `MoneyDecimal`), non da `@/shared` (con `MoneyValue`).

---

ID: TASK 4.9
Area: frontend/estimates
Fase: MVP
Dipendenze: TASK 4.8

## TASK 4.9: Implementazione TickerSearch Component

**Descrizione:** Autocomplete per ricerca ticker.

**Microstep:**

1. Creare file [`frontend/src/shared/components/TickerSearch.tsx`](../src/shared/components/TickerSearch.tsx)
2. Implementare input con debounced search (300ms)
3. Implementare fetch suggestions da backend: GET /api/tickers/search?q=... tramite hook [`useTickerSearch`](../src/shared/hooks/useTickerSearch.ts)
4. Implementare dropdown risultati: mostra ticker + nome azienda
5. Implementare selezione: click su risultato popola form
6. Implementare keyboard navigation (arrow up/down, enter)
7. Implementare cache risultati recenti (localStorage)
8. Implementare loading indicator durante search

**Acceptance Criteria:**

- [ ] Autocomplete funzionante
- [ ] Debouncing riduce chiamate API
- [ ] Keyboard navigation smooth
- [ ] Cache risultati recenti
- [ ] Loading state visibile
- [ ] Accessibilità completa

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/components/TickerSearch.tsx, frontend/src/shared/hooks/useTickerSearch.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.10
Area: frontend/estimates
Fase: MVP
Dipendenze: TASK 4.7

## TASK 4.10: Implementazione CloseEstimateModal Component

**Descrizione:** Modal per chiusura stima con conferma.

**Microstep:**

1. Creare file [`frontend/src/features/estimates/components/CloseEstimateModal.tsx`](../src/features/estimates/components/CloseEstimateModal.tsx)
2. Implementare Modal con titolo "Close Estimate"
3. Implementare form: Exit Price (prefilled con current price), Reason (optional text)
4. Implementare preview: calcola PnL finale, win/loss %
5. Implementare azioni: Cancel, Confirm Close
6. Implementare chiamata API: PUT /estimates/{id}/close tramite hook [`useCloseEstimate`](../src/features/estimates/hooks/useCloseEstimate.ts)
7. Implementare feedback: success toast, chiudi modal, refresh lista
8. Implementare validazione: exit price > 0

**Acceptance Criteria:**

- [ ] Modal si apre correttamente
- [ ] Preview PnL finale corretto
- [ ] Validazione exit price funzionante
- [ ] Chiusura via API funzionante
- [ ] Feedback success/error chiaro
- [ ] Modal chiude su success/cancel

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/components/CloseEstimateModal.tsx, frontend/src/features/estimates/hooks/useCloseEstimate.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.11
Area: frontend/portfolio
Fase: MVP
Dipendenze: TASK 4.6

## TASK 4.11: Implementazione PortfolioDashboard Component

**Descrizione:** Dashboard con overview portfolio e statistiche.

**Microstep:**

1. Creare file [`frontend/src/features/portfolio/components/PortfolioDashboard.tsx`](../src/features/portfolio/components/PortfolioDashboard.tsx)
2. Implementare fetching stats con React Query: `usePortfolioStats()` in [`frontend/src/features/portfolio/hooks/usePortfolioStats.ts`](../src/features/portfolio/hooks/usePortfolioStats.ts)
3. Implementare sezione KPI cards: Total PnL, Win Rate, Avg RR Ratio, Open Positions
4. Implementare sezione chart: PnL history (line chart 30d)
5. Implementare sezione recenti: ultimi 5 estimates
6. Implementare refresh button per aggiornamento manuale
7. Implementare skeleton loading per tutte le sezioni
8. Implementare responsive grid layout (2 colonne desktop, 1 mobile)

**Acceptance Criteria:**

- [ ] KPI cards visualizzate correttamente
- [ ] Chart PnL history funzionante
- [ ] Lista recenti aggiornata
- [ ] Refresh manuale funziona
- [ ] Loading states per ogni sezione
- [ ] Layout responsive

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/portfolio/components/PortfolioDashboard.tsx, frontend/src/features/portfolio/hooks/usePortfolioStats.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.12
Area: frontend/portfolio
Fase: MVP
Dipendenze: TASK 4.11

## TASK 4.12: Implementazione PerformanceChart Component

**Descrizione:** Chart interattivo per performance portfolio.

**Microstep:**

1. Creare file [`frontend/src/features/portfolio/components/PerformanceChart.tsx`](../src/features/portfolio/components/PerformanceChart.tsx)
2. Usare Recharts per line chart
3. Implementare asse X: date (range selezionabile: 7d, 30d, 1y, all)
4. Implementare asse Y: cumulative PnL
5. Implementare tooltip: data + PnL value
6. Implementare legend: colore profit/loss
7. Implementare zoom/pan (opzionale)
8. Implementare export chart as image (opzionale)

**Acceptance Criteria:**

- [ ] Chart visualizza dati correttamente
- [ ] Range selector funzionante
- [ ] Tooltip informativo
- [ ] Colori profit (green) / loss (red)
- [ ] Responsive su mobile
- [ ] Animazioni smooth

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/portfolio/components/PerformanceChart.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.13
Area: frontend/market-data
Fase: Fase 2
Dipendenze: TASK 4.6

## TASK 4.13: Implementazione MarketDataChart Component

**Descrizione:** Chart candlestick per dati storici ticker.

**Microstep:**

1. Creare file [`frontend/src/features/market-data/components/MarketDataChart.tsx`](../src/features/market-data/components/MarketDataChart.tsx)
2. Usare Recharts per candlestick chart (o alternative library)
3. Implementare fetching dati: GET /api/market-data/{ticker}/historical tramite hook [`useMarketData`](../src/features/market-data/hooks/useMarketData.ts)
4. Implementare asse X: date, asse Y: price
5. Implementare tooltip: OHLCV values
6. Implementare interval selector: daily, weekly, monthly
7. Implementare overlay: stime target prices (linee orizzontali)
8. Implementare zoom temporal range

**Acceptance Criteria:**

- [ ] Candlestick chart funzionante
- [ ] Dati storici caricati correttamente
- [ ] Interval selector funzionante
- [ ] Overlay target prices visibile
- [ ] Tooltip completo OHLCV
- [ ] Performance con grandi dataset (1000+ candles)

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/market-data/components/MarketDataChart.tsx, frontend/src/features/market-data/hooks/useMarketData.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.14
Area: frontend/market-data
Fase: Fase 2
Dipendenze: TASK 4.13

## TASK 4.14: Implementazione TickerWatchlist Component

**Descrizione:** Watchlist ticker con prezzi live.

**Microstep:**

1. Creare file [`frontend/src/features/market-data/components/TickerWatchlist.tsx`](../src/features/market-data/components/TickerWatchlist.tsx)
2. Implementare lista ticker: visualizza ticker + current price + change % tramite hook [`useWatchlist`](../src/features/market-data/hooks/useWatchlist.ts)
3. Implementare add/remove ticker da watchlist
4. Implementare persistent storage watchlist (localStorage)
5. Implementare refresh automatico prezzi ogni 60s
6. Implementare colore change: green (positive), red (negative)
7. Implementare click su ticker: naviga a detail view
8. Implementare drag-and-drop per riordinare (opzionale)

**Acceptance Criteria:**

- [ ] Watchlist visualizzata correttamente
- [ ] Add/remove funzionante
- [ ] Persistence tra sessioni
- [ ] Refresh automatico prezzi
- [ ] Colori change dinamici
- [ ] Click navigation funzionante

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/market-data/components/TickerWatchlist.tsx, frontend/src/features/market-data/hooks/useWatchlist.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.15
Area: frontend/chat-ai
Fase: Fase 2
Dipendenze: TASK 4.5

## TASK 4.15: Implementazione ChatAI Component (Gemini Integration)

**Descrizione:** Chat interface per assistente AI (Gemini).

**Microstep:**

1. Creare file [`frontend/src/features/chat-ai/components/ChatAI.tsx`](../src/features/chat-ai/components/ChatAI.tsx)
2. Implementare UI chat: message list + input field
3. Implementare fetching: POST /api/chat/message tramite hook [`useChatAI`](../src/features/chat-ai/hooks/useChatAI.ts)
4. Implementare streaming response (SSE o WebSocket)
5. Implementare context: passa portfolio data come context
6. Implementare quick actions: "Analyze portfolio", "Suggest new estimates"
7. Implementare message history (localStorage)
8. Implementare typing indicator durante risposta

**Acceptance Criteria:**

- [ ] Chat UI funzionante
- [ ] Invio messaggi + ricezione risposte
- [ ] Streaming response smooth
- [ ] Context portfolio incluso
- [ ] Quick actions funzionanti
- [ ] History persistente
- [ ] Typing indicator visibile

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/chat-ai/components/ChatAI.tsx, frontend/src/features/chat-ai/hooks/useChatAI.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

# SEZIONE AGGIUNTIVA: ROUTER & LAYOUT

---

ID: TASK 4.16
Area: frontend/app
Fase: MVP
Dipendenze: TASK 4.6, TASK 4.11

## TASK 4.16: Setup React Router e Layout

**Descrizione:** Configurare routing e layout principale app.

**Microstep:**

1. Creare file [`frontend/src/app/router/routes.tsx`](../src/app/router/routes.tsx)
2. Definire routes: `/` (dashboard), `/estimates` (lista), `/estimates/:id` (detail), `/estimates/new` (form)
3. Creare file [`frontend/src/app/layout/AppLayout.tsx`](../src/app/layout/AppLayout.tsx)
4. Implementare layout: sidebar navigation, header, main content area
5. Implementare sidebar: links a Dashboard, Estimates, Market Data, Chat AI
6. Implementare header: logo, user menu (logout)
7. Implementare mobile menu (hamburger)
8. Configurare Router in [`App.tsx`](../src/App.tsx)

**Acceptance Criteria:**

- [ ] Routes configurate correttamente
- [ ] Navigation tra pagine funzionante
- [ ] Layout responsive con sidebar collapsible
- [ ] Mobile menu funzionante
- [ ] Active route highlighted in sidebar

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/app/router/, frontend/src/app/layout/, frontend/src/App.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.17
Area: frontend/shared
Fase: Fase 2
Dipendenze: TASK 4.5b

## TASK 4.17: Accessibilità base & i18n

**Descrizione:** Audit di accessibilità base sui componenti interattivi e formalizzazione dell'infrastruttura i18n esistente (italiano = locale base).

**Microstep:**

1. Censire i componenti interattivi reali (form, modal, bottoni, toast) in `frontend/src/shared/components/` e nelle feature (`estimates`, `admin`, `portfolio`)
2. Audit accessibilità: attributi `aria-*` su input e modal, focus-trap nei modal, `aria-live` per Toast/notifiche
3. Verificare contrasto colore di testi e stati warning/danger (soglia WCAG AA)
4. Navigazione da tastiera: tab order coerente, `Esc` chiude i modal, focus visibile
5. Censire l'infrastruttura esistente in `frontend/src/shared/i18n/` e le stringhe utente hardcoded nei componenti
6. Formalizzare l'italiano come locale base: stringhe utente centralizzate via `shared/i18n/` (nessuna nuova libreria se già presente)
7. Documentare le convenzioni a11y/i18n adottate in `frontend/README.md`

**Acceptance Criteria:**

- [ ] Modal con focus-trap e chiusura via `Esc`
- [ ] Input dei form con label/`aria` associati
- [ ] Toast/notifiche annunciati via `aria-live`
- [ ] Contrasto conforme WCAG AA su stati normale/warning/danger
- [ ] Stringhe utente censite e servite via `shared/i18n/` (locale base: it)
- [ ] Convenzioni documentate in `frontend/README.md`
- [ ] `npx tsc --noEmit` verde e `npm run test:coverage` verde

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/, frontend/src/features/*/components/, frontend/README.md] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati (nessuna nuova libreria i18n se `shared/i18n/` è già presente).
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

# SPRINT UX — Fix operatività

> Sprint di rifinitura UX/operatività. Ordine consigliato: C → D → B → A. Checklist/overview in [`../AGENTS.md`](../AGENTS.md) §Sprint UX. Parti backend in [`../backend/AGENTS.md`](../backend/AGENTS.md) §Sprint UX.
> **Vincoli:** stringhe utente in italiano; nessuna API key esposta al frontend; riusare endpoint esistenti (no duplicati); `npx tsc --noEmit` verde dopo ogni task.

## TASK C — Barra inferiore: rimuovi `Sync Now`, aggiungi indicatore Yahoo
**File target:** [`frontend/src/components/layout/AppStatusBar.tsx`](../src/components/layout/AppStatusBar.tsx)
**Microstep:**
1. Confermare che `AppStatusBar.tsx` è il componente realmente renderizzato nella barra inferiore (nessuna seconda implementazione attiva).
2. Rimuovere il pulsante `Sync Now` e tutto il wiring UI usato solo da esso (handler, props, import icone, stato locale). Nessun dead code. Non rimuovere la capability backend.
3. Rimuovere il badge `GDrive: Non configurato` dalla barra globale (lo stato GDrive resta consultabile in Admin).
4. Aggiungere indicatore elapsed-time dell'ultima chiamata Yahoo usando il timestamp esposto dall'endpoint di status (vedi backend §Sprint UX). Testi: `Yahoo: aggiornato 24s fa` / `3m fa` / `1h 12m fa`; assente → `Yahoo: nessun aggiornamento registrato`; ultimo tentativo fallito → `Yahoo: ultimo tentativo fallito 4m fa`.
5. Aggiornare l'elapsed con timer locale leggero (nessuna chiamata API aggiuntiva oltre al polling status esistente).
6. Stato visivo a soglie documentate nel codice: <5m normale, 5–30m warning discreto, >30m o ultimo esito fallito warning/danger.

## TASK D — Nuova Stima: stato Finnhub + fallback simbolo
**File target:** [`frontend/src/features/estimates/components/EstimateForm.tsx`](../src/features/estimates/components/EstimateForm.tsx), [`frontend/src/features/estimates/components/InsertEstimate.tsx`](../src/features/estimates/components/InsertEstimate.tsx)
**Microstep:**
1. Leggere il flag `finnhub_key_configured` (booleano) via query dedicata dall'endpoint config/admin (vedi backend §Sprint UX). Caching ragionevole, no refetch aggressivo, naming coerente col layer API.
2. Quando Finnhub NON è configurata: banner inline non invasivo vicino al campo simbolo — avvisa che la ricerca automatica è disabilitata, che si può inserire il ticker manualmente, con CTA verso Admin.
3. Fallback manuale: al blur del campo simbolo, validare via endpoint Yahoo/market-validate esistente; feedback sintetico: valido / non trovato / verifica non disponibile.
4. Se Finnhub È configurata: montare/usare davvero il flusso di symbol-search assistita (nessun codice ricerca scollegato).
5. Copy in italiano, esempi ticker `AAPL`, `MSFT`, `ENI.MI`. Mai esporre la API key.

## TASK B — Admin operativa completa
**File target:** [`frontend/src/features/admin/components/AdminSettings.tsx`](../src/features/admin/components/AdminSettings.tsx)
**Microstep:**
1. Censire le config backend reali e distinguere config di sistema (persistite backend) da preferenze UI (localStorage).
2. Finnhub: inserimento + verifica esplicita + salvataggio a verifica riuscita + stato configurata/non configurata senza mostrare il segreto.
3. Google Drive: aggiungere il campo folder (`DRIVE_FOLDER_ID` o semantica backend reale), con caricamento valore corrente e salvataggio via backend (no persistenza solo locale).
4. Backup/ripristino GDrive con feedback chiaro (usa endpoint status/backup esistenti; estendi, non duplicare).
5. `PRICE_UPDATE_INTERVAL_MINUTES`: mostra valore reale backend, salvataggio via endpoint esistente, copy che spiega la frequenza di aggiornamento prezzi.

## TASK A — System Logs: eventi frontend + backend unificati
**File target:** nuovo [`frontend/src/shared/services/frontendLogger.ts`](../src/shared/services/frontendLogger.ts) + viewer System Logs esistente
**Microstep:**
1. Creare servizio centralizzato `frontendLogger` (buffer + flush, fire-and-forget, fallback silenzioso, niente `console.log` in prod).
2. Inviare eventi a `POST /api/logs/frontend` (vedi backend §Sprint UX) con payload tipizzato: `timestamp`, `level` (info|warn|error), `event`, `message`, `path?`, `component?`, `details?` sanitizzato, `source: frontend`. Mai API key/Authorization/cookie/body sensibili.
3. Coprire: cambio route (`page_navigation`), errori API principali (`api_error`), boundary error se presente, click su azioni importanti (backup/ripristino GDrive, verifica/salvataggio Finnhub, salvataggio Admin).
4. Aggiornare il viewer System Logs: distinguere `frontend`/`backend`, mostrare `timestamp/source/level/event/message`, filtro `source`, compatibilità con i log backend esistenti.

---

# NOTE FINALI PER LLM FRONTEND

1. **Sempre usare decimal.js per calcoli finanziari** - mai `number` nativo
2. **Sempre passare da API client centralizzato** - no fetch/axios diretto
3. **Sempre gestire loading/error/empty states** - UX pulita
4. **Sempre tipizzare con TypeScript** - nessun `any`
5. **Sempre validare input utente** - Zod + React Hook Form
6. **Sempre testare responsive** - mobile-first approach

---
