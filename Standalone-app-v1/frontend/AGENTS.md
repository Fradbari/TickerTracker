# Frontend - React UI & UX

## Scope
Questa sezione contiene SOLO task per il frontend React/TypeScript:
- Feature modules: `features/estimates/`, `features/portfolio/`, `features/market-data/`, `features/chat-ai/`
- Shared: `shared/components/`, `shared/hooks/`, `shared/utils/`, `shared/api/`
- App: `app/router/`, `app/layout/`, `app/providers/`
- Configurazione: Vite, TailwindCSS, React Query, React Hook Form

**Non modificare**:
- File di backend (vedi `Backend/AGENTS.md`)
- File di Docker/compose (vedi `Docker/AGENTS.md`)
- File di test/CI (vedi `Docs/AGENTS.md`)

---

# REGOLE FISSE PER LLM FRONTEND

1. **Tutti i calcoli finanziari DEVONO usare decimal.js** ([`shared/utils/financial.ts`](../src/shared/utils/financial.ts) o [`shared/finance/decimalMoney.ts`](../src/shared/finance/decimalMoney.ts))
2. **Tutte le chiamate API DEVONO passare da [`shared/api/client.ts`](../src/shared/api/client.ts)** (no fetch/axios sparso)
3. **Ogni feature è self-contained**: no import cross-feature diretti (solo via `shared/`)
4. **Componenti riutilizzabili vanno in [`shared/components/`](../src/shared/components)**
5. **Hook riutilizzabili vanno in [`shared/hooks/`](../src/shared/hooks)**

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

## TASK 4.1: Setup Progetto Frontend (Vite + React 19)

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

**Descrizione:** Creare types TypeScript per modelli domain e API responses.

**Microstep:**

1. Creare file [`frontend/src/shared/types/api.ts`](../src/shared/types/api.ts)
2. Definire type `ApiResponse<T>` che corrisponde al backend: `{success: boolean, data: T | null, error: ApiError | null, trace_id: string}`
3. Definire type `ApiError`: `{code: string, message: string, details?: Record<string, any>}`
4. Creare file [`frontend/src/shared/types/domain.ts`](../src/shared/types/domain.ts)
5. Definire types: `Estimate`, `Money`, `PriceTarget`, `MarketData`, `Portfolio`
6. Implementare type guards: `isEstimate(obj: unknown)`, `isMoney(obj: unknown)`
7. Implementare validators Zod per form input

**Acceptance Criteria:**

- [ ] Types corrispondono esattamente al backend
- [ ] Type guards funzionanti
- [ ] Validators Zod per tutti i form
- [ ] Nessun `any` type
- [ ] Documentazione JSDoc per types complessi

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/types/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 4.5
Area: frontend/shared
Fase: MVP
Dipendenze: TASK 4.4

## TASK 4.5: Creazione Componenti UI Shared

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

ID: TASK 4.6
Area: frontend/estimates
Fase: MVP
Dipendenze: TASK 4.5

## TASK 4.6: Implementazione EstimateList Component

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

## TASK 4.8: Implementazione CreateEstimateForm Component

**Descrizione:** Form per creare nuova stima.

**Microstep:**

1. Creare file [`frontend/src/features/estimates/components/CreateEstimateForm.tsx`](../src/features/estimates/components/CreateEstimateForm.tsx)
2. Usare React Hook Form per gestione stato form
3. Implementare campi: Ticker (input text), Direction (radio LONG/SHORT), Stop Loss % (number), Take Profit % (number)
4. Implementare validazione Zod: ticker formato, percentuali > 0
5. Implementare preview: calcola prezzi target in tempo reale da % (fetch current price)
6. Implementare submit: chiamata API POST /estimates tramite hook [`useCreateEstimate`](../src/features/estimates/hooks/useCreateEstimate.ts)
7. Implementare feedback: success toast + redirect a lista
8. Implementare error handling: mostra errori campo specifici

**Acceptance Criteria:**

- [ ] Form completo con tutti i campi
- [ ] Validazione client-side funzionante
- [ ] Preview target prices live
- [ ] Submit funzionante
- [ ] Feedback success/error chiaro
- [ ] Accessibilità form (labels, errors)

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/components/CreateEstimateForm.tsx, frontend/src/features/estimates/hooks/useCreateEstimate.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

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

# NOTE FINALI PER LLM FRONTEND

1. **Sempre usare decimal.js per calcoli finanziari** - mai `number` nativo
2. **Sempre passare da API client centralizzato** - no fetch/axios diretto
3. **Sempre gestire loading/error/empty states** - UX pulita
4. **Sempre tipizzare con TypeScript** - nessun `any`
5. **Sempre validare input utente** - Zod + React Hook Form
6. **Sempre testare responsive** - mobile-first approach

---