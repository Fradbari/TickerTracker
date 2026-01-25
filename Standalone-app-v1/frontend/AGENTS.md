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

1. **Tutti i calcoli finanziari DEVONO usare decimal.js** (`shared/utils/financial.ts` o `shared/finance/decimalMoney.ts`)
2. **Tutte le chiamate API DEVONO passare da `shared/api/client.ts`** (no fetch/axios sparso)
3. **Ogni feature è self-contained**: no import cross-feature diretti (solo via `shared/`)
4. **Componenti riutilizzabili vanno in `shared/components/`**
5. **Hook riutilizzabili vanno in `shared/hooks/`**

---

# SEZIONE 1: SETUP FRONTEND (TASK 1.8)

---

ID: TASK 1.8
Area: frontend/shared
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.8: Setup Wrapper TypeScript per Decimali (Frontend)

**Descrizione:** Creare wrapper TypeScript per gestione decimale precisa nel frontend usando decimal.js.

**Microstep:**

1. Installare dipendenza `decimal.js` nel progetto frontend
2. Creare file `frontend/src/shared/utils/decimal.ts`
3. Definire classe/type `MoneyValue` con proprietà: `amount` (Decimal), `currency` (string)
4. Implementare funzioni factory: `createMoney(amount: string | number, currency?: string)`
5. Implementare funzioni di calcolo: `add`, `subtract`, `multiply`, `divide` per MoneyValue
6. Implementare funzione `formatMoney(money: MoneyValue, locale?: string) -> string`
7. Implementare parsing: `parseMoney(formattedString: string) -> MoneyValue`
8. Creare test unitari per tutti i metodi

**Acceptance Criteria:**

- [ ] Tutti i calcoli monetari usano Decimal internamente
- [ ] Formatting locale-aware funzionante (es. $1,234.56 vs 1.234,56 €)
- [ ] Parsing robusto a vari formati input
- [ ] Test unitari coprono edge cases
- [ ] Nessun uso di number nativi per calcoli finanziari

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/utils/decimal.ts, frontend/src/shared/finance/decimalMoney.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

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
7. Configurare TailwindCSS
8. Configurare path aliases in tsconfig e vite.config
9. Creare struttura cartelle: `features/`, `shared/`, `app/`
10. Creare file README con convenzioni

**Acceptance Criteria:**

- [ ] `npm run dev` avvia dev server
- [ ] `npm run build` produce build di produzione
- [ ] TypeScript strict mode abilitato
- [ ] TailwindCSS funzionante
- [ ] Path aliases funzionanti

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/, frontend/package.json, frontend/vite.config.ts, frontend/tsconfig.json, frontend/tailwind.config.cjs] se non strettamente necessario.
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

1. Creare cartella `frontend/src/features/estimates/` con sottocartelle: `components/`, `hooks/`, `api/`, `types/`
2. Creare cartella `frontend/src/features/portfolio/` con stessa struttura
3. Creare cartella `frontend/src/features/market-data/` con stessa struttura
4. Creare cartella `frontend/src/features/chat-ai/` con stessa struttura
5. Creare cartella `frontend/src/shared/` con sottocartelle: `components/`, `hooks/`, `utils/`, `types/`, `api/`
6. Creare cartella `frontend/src/app/` con sottocartelle: `router/`, `layout/`, `providers/`
7. Creare file `index.ts` barrel exports in ogni feature
8. Creare README in `shared/` che documenta regole riuso componenti

**Acceptance Criteria:**

- [ ] Struttura cartelle completa
- [ ] Ogni feature è isolata
- [ ] Barrel exports configurati
- [ ] README documenta convenzioni
- [ ] Nessun import cross-feature diretto

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

## TASK 4.3: Setup API Client Centralizzato

**Descrizione:** Creare client HTTP centralizzato con gestione errori e auth.

**Microstep:**

1. Creare file `frontend/src/shared/api/client.ts`
2. Configurare axios instance con baseURL da env vars
3. Implementare request interceptor: aggiunge JWT token da localStorage
4. Implementare response interceptor: gestisce 401 (redirect login), 500 (toast error)
5. Implementare funzioni wrapper: `apiGet`, `apiPost`, `apiPut`, `apiDelete`
6. Implementare retry logic su errori 5xx (max 3 tentativi)
7. Implementare timeout configurabile (default 30s)
8. Creare file `frontend/.env.example` con `VITE_API_BASE_URL`

**Acceptance Criteria:**

- [ ] Client centralizzato configurato
- [ ] Auth token automaticamente incluso
- [ ] Errori gestiti globalmente
- [ ] Retry su errori transitori
- [ ] Env vars documentate

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/api/client.ts, frontend/.env.example] se non strettamente necessario.
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

1. Creare file `frontend/src/shared/types/api.ts`
2. Definire type `ApiResponse<T>` che corrisponde al backend: `{success: boolean, data: T | null, error: ApiError | null, trace_id: string}`
3. Definire type `ApiError`: `{code: string, message: string, details?: Record<string, any>}`
4. Creare file `frontend/src/shared/types/domain.ts`
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

1. Creare file `frontend/src/shared/components/Button.tsx`: varianti primary/secondary/danger, sizes sm/md/lg
2. Creare file `frontend/src/shared/components/Input.tsx`: supporto error state, label, helper text
3. Creare file `frontend/src/shared/components/Card.tsx`: container con padding/shadow
4. Creare file `frontend/src/shared/components/Badge.tsx`: status badge (open, closed, profit, loss)
5. Creare file `frontend/src/shared/components/Spinner.tsx`: loading indicator
6. Creare file `frontend/src/shared/components/Toast.tsx`: notification system
7. Creare file `frontend/src/shared/components/Modal.tsx`: dialog generico
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

1. Creare file `frontend/src/features/estimates/components/EstimateList.tsx`
2. Implementare fetching data con React Query: `useEstimates(filters)`
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

1. Creare file `frontend/src/features/estimates/components/EstimateDetail.tsx`
2. Implementare fetching con React Query: `useEstimate(id)`
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

1. Creare file `frontend/src/features/estimates/components/CreateEstimateForm.tsx`
2. Usare React Hook Form per gestione stato form
3. Implementare campi: Ticker (input text), Direction (radio LONG/SHORT), Stop Loss % (number), Take Profit % (number)
4. Implementare validazione Zod: ticker formato, percentuali > 0
5. Implementare preview: calcola prezzi target in tempo reale da % (fetch current price)
6. Implementare submit: chiamata API POST /estimates
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

1. Creare file `frontend/src/shared/components/TickerSearch.tsx`
2. Implementare input con debounced search (300ms)
3. Implementare fetch suggestions da backend: GET /api/tickers/search?q=...
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

1. Creare file `frontend/src/features/estimates/components/CloseEstimateModal.tsx`
2. Implementare Modal con titolo "Close Estimate"
3. Implementare form: Exit Price (prefilled con current price), Reason (optional text)
4. Implementare preview: calcola PnL finale, win/loss %
5. Implementare azioni: Cancel, Confirm Close
6. Implementare chiamata API: PUT /estimates/{id}/close
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

1. Creare file `frontend/src/features/portfolio/components/PortfolioDashboard.tsx`
2. Implementare fetching stats con React Query: `usePortfolioStats()`
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

1. Creare file `frontend/src/features/portfolio/components/PerformanceChart.tsx`
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

1. Creare file `frontend/src/features/market-data/components/MarketDataChart.tsx`
2. Usare Recharts per candlestick chart (o alternative library)
3. Implementare fetching dati: GET /api/market-data/{ticker}/historical
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

1. Creare file `frontend/src/features/market-data/components/TickerWatchlist.tsx`
2. Implementare lista ticker: visualizza ticker + current price + change %
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

1. Creare file `frontend/src/features/chat-ai/components/ChatAI.tsx`
2. Implementare UI chat: message list + input field
3. Implementare fetching: POST /api/chat/message
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

1. Creare file `frontend/src/app/router/routes.tsx`
2. Definire routes: `/` (dashboard), `/estimates` (lista), `/estimates/:id` (detail), `/estimates/new` (form)
3. Creare file `frontend/src/app/layout/AppLayout.tsx`
4. Implementare layout: sidebar navigation, header, main content area
5. Implementare sidebar: links a Dashboard, Estimates, Market Data, Chat AI
6. Implementare header: logo, user menu (logout)
7. Implementare mobile menu (hamburger)
8. Configurare Router in `App.tsx`

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
