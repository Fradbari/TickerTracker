# Frontend

ID: TASK 1.8
Area: frontend
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.8: Setup Wrapper TypeScript per Decimali (Frontend)

**Descrizione:** Creare wrapper TypeScript per gestione decimale precisa nel frontend usando decimal.js.

**Microstep:**

1\. Installare dipendenza `decimal.js` nel progetto frontend

2\. Creare file `frontend/src/shared/utils/decimal.ts`

3\. Definire classe/type `MoneyValue` con proprietà: `amount` (Decimal), `currency` (string)

4\. Implementare funzioni factory: `createMoney(amount: string | number, currency?: string)`

5\. Implementare funzioni di calcolo: `addMoney`, `subtractMoney`, `multiplyMoney`, `divideMoney`

6\. Implementare funzione `formatMoney(money: MoneyValue, locale?: string): string`

7\. Creare file `frontend/src/shared/utils/percentage.ts` con logica analoga

8\. Implementare funzioni: `createPercentage`, `applyPercentage`, `formatPercentage`

9\. Esportare tutto da `frontend/src/shared/utils/financial.ts`

**Acceptance Criteria:**

- [ ] Nessun uso di number nativo per calcoli finanziari

- [ ] Tutte le funzioni accettano string o Decimal, mai float JS

- [ ] Formattazione rispetta locale (separatore migliaia, decimali)

- [ ] Test unitari verificano precisione (es. 0.1 + 0.2 = 0.3 esatto)

---

# SEZIONE 2: BACKEND & DATA

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/utils/decimal.ts, frontend/src/shared/utils/financial.ts, frontend/src/shared/utils/percentage.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.1
Area: frontend
Fase: MVP
Dipendenze: -

## TASK 4.1: Setup Progetto Frontend (Vite + React 19)

**Descrizione:** Inizializzare progetto frontend con stack moderno.

**Microstep:**

1\. Creare progetto con `npm create vite@latest frontend -- --template react-ts`

2\. Installare dipendenze core: `react-router-dom`, `@tanstack/react-query`, `axios`

3\. Installare dipendenze UI: `tailwindcss`, `postcss`, `autoprefixer`

4\. Installare dipendenze form: `react-hook-form`, `zod`, `@hookform/resolvers`

5\. Installare dipendenze charts: `recharts`

6\. Installare dipendenze utility: `decimal.js`, `date-fns`

7\. Configurare TailwindCSS

8\. Configurare path aliases in tsconfig e vite.config

9\. Creare struttura cartelle: `features/`, `shared/`, `app/`

10\. Creare file README con convenzioni

**Acceptance Criteria:**

- [ ] `npm run dev` avvia dev server

- [ ] `npm run build` produce build di produzione

- [ ] TypeScript strict mode abilitato

- [ ] TailwindCSS funzionante

- [ ] Path aliases funzionanti

---

### Istruzioni per LLM
- Non modificare file fuori da [@hookform/resolvers, @tanstack/react-query, app/, features/, shared/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.2
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.1

## TASK 4.2: Creazione Struttura Feature Modules

**Descrizione:** Organizzare codice frontend in moduli per funzionalità.

**Microstep:**

1\. Creare cartella `frontend/src/features/estimates/` con sottocartelle: `components/`, `hooks/`, `api/`, `types/`

2\. Creare cartella `frontend/src/features/portfolio/` con stessa struttura

3\. Creare cartella `frontend/src/features/market-data/` con stessa struttura

4\. Creare cartella `frontend/src/features/chat-ai/` con stessa struttura

5\. Creare cartella `frontend/src/shared/` con sottocartelle: `components/`, `hooks/`, `utils/`, `types/`, `api/`

6\. Creare cartella `frontend/src/app/` per routing e layout

7\. Creare file index.ts in ogni cartella per esportazioni pubbliche

8\. Documentare convenzione in README

**Acceptance Criteria:**

- [ ] Ogni feature è self-contained

- [ ] Shared contiene solo codice riutilizzabile

- [ ] Import tra feature passano per index pubblici

- [ ] Nessun import circolare

---

### Istruzioni per LLM
- Non modificare file fuori da [api/, components/, frontend/src/app/, frontend/src/features/chat-ai/, frontend/src/features/estimates/, frontend/src/features/market-data/, frontend/src/features/portfolio/, frontend/src/shared/, ...] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.3
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.2

## TASK 4.3: Configurazione React Query

**Descrizione:** Configurare TanStack Query per data fetching centralizzato.

**Microstep:**

1\. Creare file `frontend/src/app/providers/QueryProvider.tsx`

2\. Configurare QueryClient con defaults:

- staleTime: 5 minuti per dati generici

- gcTime: 30 minuti

- retry: 3 con backoff

- refetchOnWindowFocus: true

3\. Creare QueryClientProvider wrapper

4\. Configurare devtools in development

5\. Creare hook custom `useApiQuery` che wrappa useQuery con gestione errori standard

6\. Creare hook custom `useApiMutation` che wrappa useMutation con gestione errori e toast

**Acceptance Criteria:**

- [ ] QueryClient configurato correttamente

- [ ] Devtools visibili in dev

- [ ] Hook custom semplificano uso

- [ ] Errori gestiti uniformemente

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/app/providers/QueryProvider.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.4
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.3

## TASK 4.4: Creazione Client API Tipizzato

**Descrizione:** Creare client HTTP tipizzato per comunicazione con backend.

**Microstep:**

1\. Creare file `frontend/src/shared/api/client.ts`

2\. Configurare istanza axios con baseURL da variabile ambiente

3\. Aggiungere interceptor request per:

- Aggiungere header Authorization (se presente token)

- Aggiungere header X-Correlation-ID (genera UUID)

4\. Aggiungere interceptor response per:

- Estrarre data da ApiResponse

- Trasformare errori in formato uniforme

5\. Creare file `frontend/src/shared/api/types.ts` con tipi ApiResponse, ApiError

6\. Creare funzioni tipizzate: `get&lt;T&gt;`, `post&lt;T&gt;`, `patch&lt;T&gt;`, `delete&lt;T&gt;`

**Acceptance Criteria:**

- [ ] Tutte le chiamate usano client centralizzato

- [ ] Tipi response inferiti correttamente

- [ ] Errori hanno struttura uniforme

- [ ] Correlation ID propagato

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/api/client.ts, frontend/src/shared/api/types.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.5
Area: frontend
Fase: Fase 2
Dipendenze: -

**TASK 4.5: Wrapper Decimale per Calcoli Finanziari (FE)**

**Descrizione:**  
Usare una libreria decimale in frontend per tutti i calcoli monetari e percentuali, evitando i number JS nativi.

**Microstep:**

- Aggiungere dipendenza decimal.js (o big.js) al progetto frontend.
- Creare file frontend/src/shared/finance/decimalMoney.ts.
- Definire type MoneyDecimal con campi: amount: Decimal, currency: string.
- Implementare funzioni helper:
  - parseMoneyFromString(value: string, currency: string) -> MoneyDecimal
  - formatMoney(m: MoneyDecimal) -> string
  - calculatePnL(entry: MoneyDecimal, current: MoneyDecimal, quantity: Decimal).
- Sostituire nei componenti EstimateCard, EstimateForm, Dashboard l'uso di number per importi con MoneyDecimal/helper.

**Acceptance Criteria:**

- Nessun calcolo di P&L, prezzi o percentuali usa più number JS puro.
- I risultati di P&L coincidono con quelli calcolati dal backend a parità di input.
- I valori mostrati all'utente non soffrono di errori di arrotondamento "classici" JS (es. 0.1+0.2 ≠ 0.3000004).

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.6
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.5

## TASK 4.6: Implementazione API Hooks per Estimates

**Descrizione:** Creare hook React Query per operazioni su stime.

**Microstep:**

1\. Creare file `frontend/src/features/estimates/api/queries.ts`

2\. Implementare `useEstimates(filters)`: lista stime con filtri

3\. Implementare `useEstimate(id)`: singola stima con dettagli

4\. Implementare `useEstimateHistory(id)`: audit trail stima

5\. Creare file `frontend/src/features/estimates/api/mutations.ts`

6\. Implementare `useCreateEstimate()`: creazione nuova stima

7\. Implementare `useUpdateEstimate()`: aggiornamento stima

8\. Implementare `useCloseEstimate()`: chiusura stima

9\. Configurare invalidation corretta delle query dopo mutation

**Acceptance Criteria:**

- [ ] Hook restituiscono stati: loading, error, data

- [ ] Filtri riflessi in query key per caching corretto

- [ ] Mutation invalida query correlate

- [ ] Tipi TypeScript completi

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/api/mutations.ts, frontend/src/features/estimates/api/queries.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.7
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.5

**TASK 4.7: Error Boundary Globale & Gestione Errori UX**

**Descrizione:**  
Gestire in modo uniforme errori runtime e di rete, con un ErrorBoundary e notifiche consistenti.

**Microstep:**

- Creare componente frontend/src/app/components/AppErrorBoundary.tsx che:
  - intercetta errori React e mostra una schermata di fallback con bottone "Riprova/Ricarica pagina".
- Wrappare il router principale / App root con AppErrorBoundary.
- Creare hook useNotify in frontend/src/shared/ui/useNotify.ts per mostrare toast di errore/successo (riusando il sistema di toast che già hai).
- Integrare useNotify nei hook useApiQuery/useApiMutation per mostrare errori di business (es. ticker non trovato) in modo uniforme.

**Acceptance Criteria:**

- Un errore JavaScript in un componente non "rompe" tutta l'app ma mostra la schermata di fallback.
- Gli errori di rete/API sono mostrati all'utente con messaggio leggibile e coerente.
- I toast non si sovrappongono caoticamente (throttling/raggruppamento base).

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.8
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.5

## TASK 4.8: Implementazione Componente EstimateForm

**Descrizione:** Creare form per creazione/modifica stime con validazione.

**Microstep:**

1\. Creare file `frontend/src/features/estimates/components/EstimateForm.tsx`

2\. Definire schema Zod per validazione: ticker (required), direction, target_profit_percent, stop_loss_percent, notes

3\. Configurare react-hook-form con zodResolver

4\. Implementare campo ticker con autocomplete (usa API search)

5\. Implementare campi numerici con validazione range

6\. Implementare preview calcoli (target price, stop loss price) in tempo reale

7\. Implementare submit con useCreateEstimate

8\. Mostrare errori validazione inline

9\. Mostrare errori API con toast/alert

**Acceptance Criteria:**

- [ ] Validazione client-side completa

- [ ] Autocomplete ticker funzionante

- [ ] Preview calcoli aggiornato in tempo reale

- [ ] Submit disabilitato durante invio

- [ ] Errori mostrati chiaramente

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/components/EstimateForm.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.9
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.5

## TASK 4.9: Implementazione Componente EstimateCard

**Descrizione:** Creare card per visualizzazione singola stima in lista.

**Microstep:**

1\. Creare file `frontend/src/features/estimates/components/EstimateCard.tsx`

2\. Mostrare: ticker, direction badge, status badge

3\. Mostrare prezzi: entry, current, target, stop loss

4\. Mostrare P&L: valore assoluto e percentuale con colore (verde/rosso)

5\. Mostrare: data apertura, giorni aperti

6\. Mostrare: AI model badge, confidence score

7\. Implementare click handler per navigazione a dettaglio

8\. Implementare menu azioni: edit, close, delete

9\. Rendere componente responsive (card su mobile, row su desktop)

**Acceptance Criteria:**

- [ ] Tutti i dati chiave visibili

- [ ] Colori P&L corretti (verde positivo, rosso negativo)

- [ ] Azioni accessibili

- [ ] Layout responsive

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/components/EstimateCard.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.10
Area: frontend
Fase: MVP
Dipendenze: TASK 4.5

## TASK 4.10: Implementazione Componente EstimatesList

**Descrizione:** Creare lista stime con filtri e ordinamento.

**Microstep:**

1\. Creare file `frontend/src/features/estimates/components/EstimatesList.tsx`

2\. Usare useEstimates hook per dati

3\. Implementare filtri: status (dropdown), ticker (autocomplete), date range (date picker)

4\. Implementare ordinamento: by date, by P&L, by ticker

5\. Implementare virtualizzazione lista per performance (react-window)

6\. Mostrare skeleton durante loading

7\. Mostrare empty state quando nessun risultato

8\. Mostrare error state con retry button

9\. Implementare infinite scroll o paginazione

**Acceptance Criteria:**

- [ ] Filtri aggiornano query in tempo reale

- [ ] Ordinamento funzionante

- [ ] Virtualizzazione per liste lunghe (>100 items)

- [ ] Stati loading/empty/error gestiti

- [ ] Scroll infinito o paginazione funzionante

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/estimates/components/EstimatesList.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.11
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.5

## TASK 4.11: PWA Base (Manifest + Service Worker)

**Descrizione:**

Abilitare una PWA base per permettere installazione su desktop/mobile e caching leggero delle risorse statiche.

**Microstep:**

1\. Creare `frontend/public/manifest.webmanifest` con nome app, icone, theme/background color e start_url.

2\. Aggiungere il link al manifest in `index.html` e meta tag base (theme-color).

3\. Aggiungere un service worker semplice (workbox o custom) per:

- cache-first su asset statici (JS/CSS/font),

- network-first sulle API (nessun caching aggressivo dei dati di mercato).

4\. Aggiornare la build Vite per includere registrazione del service worker solo in production.

5\. Verificare con Lighthouse che l'app sia installabile come PWA.

**Acceptance Criteria:**

- [ ] L'app è installabile come PWA in Chrome/Edge.

- [ ] Le risorse statiche sono servite dalla cache in offline/connessione lenta.

- [ ] Le chiamate API continuano a usare il network per evitare dati di mercato stantii.

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/public/manifest.webmanifest] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.12
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.5

## TASK 4.12: Accessibilità Base & Skeleton i18n

**Descrizione:**

Migliorare l'accessibilità dei componenti chiave e preparare lo scheletro per localizzazione futura (es. IT/EN).

**Microstep:**

1\. Installare `react-aria` o libreria analoga solo se necessario; in alternativa, usare pattern accessibili manuali (ruoli ARIA, label, focus management).

2\. Aggiornare i componenti chiave (`EstimateForm`, `EstimatesList`, `Dashboard`) per:

- avere `aria-label`/`aria-describedby` sui controlli di input,

- supportare navigazione da tastiera (tab order corretto, focus visibile),

- avere contrasti colore adeguati (verifica con strumenti DevTools).

3\. Aggiungere libreria di i18n leggera (`react-i18next`) e creare:

- `frontend/src/shared/i18n/config.ts`,

- file `locales/it/common.json` e `locales/en/common.json` con un piccolo set di stringhe (titolo app, menu, etichette principali).

4\. Collegare il router/layout principale al provider i18n e usare `t()` in almeno 2-3 punti (es. titoli pagina, label bottoni principali).

5\. Documentare nel README di frontend come aggiungere nuove chiavi di traduzione.

**Acceptance Criteria:**

- [ ] I principali flussi (creazione stima, lista stime) sono navigabili da tastiera.

- [ ] I controlli di form hanno label chiare e leggibili anche da screen reader.

- [ ] Esiste un setup i18n funzionante con almeno IT/EN, anche se l'app resta principalmente in italiano.

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/shared/i18n/config.ts, locales/en/common.json, locales/it/common.json] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.13
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.6

## TASK 4.13: Implementazione Dashboard Portfolio

**Descrizione:** Creare dashboard con metriche aggregate portfolio.

**Microstep:**

1\. Creare file `frontend/src/features/portfolio/components/Dashboard.tsx`

2\. Mostrare metriche top-level: total P&L, total invested, active estimates count

3\. Mostrare breakdown per status: open, closed win, closed loss

4\. Implementare grafico P&L cumulativo nel tempo (Recharts)

5\. Implementare grafico distribuzione per ticker (pie chart)

6\. Implementare tabella top performers / worst performers

7\. Usare aggregazioni server-side per performance

8\. Implementare refresh periodico (ogni 5 min)

**Acceptance Criteria:**

- [ ] Metriche aggregate corrette

- [ ] Grafici interattivi con tooltip

- [ ] Performance accettabile con molti dati

- [ ] Refresh automatico funzionante

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/portfolio/components/Dashboard.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.14
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.6

## TASK 4.14: Implementazione Price Chart

**Descrizione:** Creare componente grafico prezzi con candlestick/line.

**Microstep:**

1\. Creare file `frontend/src/features/market-data/components/PriceChart.tsx`

2\. Accettare props: ticker, dateRange, chartType (line/candlestick)

3\. Usare hook per fetch dati storici con aggregazione appropriata

4\. Implementare grafico linea con Recharts

5\. Implementare overlay con entry price, target, stop loss della stima associata

6\. Implementare zoom in/out con cambio aggregazione (1D -> 1W -> 1M)

7\. Implementare tooltip con dettagli OHLCV

8\. Mostrare loading skeleton durante fetch

**Acceptance Criteria:**

- [ ] Grafico renderizza correttamente dati storici

- [ ] Zoom cambia livello aggregazione

- [ ] Overlay livelli prezzo visibili

- [ ] Tooltip informativo

- [ ] Performance fluida anche con molti datapoint

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/market-data/components/PriceChart.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.15
Area: frontend
Fase: Fase 2
Dipendenze: TASK 4.5

## TASK 4.15: Implementazione Chat AI Component

**Descrizione:** Creare componente chat per interazione con AI.

**Microstep:**

1\. Creare file `frontend/src/features/chat-ai/components/ChatInterface.tsx`

2\. Implementare lista messaggi con distinzione user/assistant

3\. Implementare input con invio su Enter e bottone

4\. Implementare hook `useSendChatMessage` per POST a /api/chat

5\. Mostrare indicatore typing durante attesa risposta

6\. Supportare markdown nella risposta AI

7\. Implementare scroll automatico a nuovo messaggio

8\. Persistere cronologia chat in sessionStorage

**Acceptance Criteria:**

- [ ] Messaggi distinti visivamente per ruolo

- [ ] Input funziona con Enter e click

- [ ] Indicatore loading durante attesa

- [ ] Markdown renderizzato (grassetto, elenchi, codice)

- [ ] Scroll a nuovo messaggio

---

# SEZIONE 5: TESTING, CI/CD, OPERAZIONI

---

### Istruzioni per LLM
- Non modificare file fuori da [frontend/src/features/chat-ai/components/ChatInterface.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.