# AGENTS — features (common)

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 4.2
Area: features_common
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

6. Creare cartella `frontend/src/app/` per routing e layout

7. Creare file index.ts in ogni cartella per esportazioni pubbliche

8. Documentare convenzione in README

**Acceptance Criteria:**

- [ ] Ogni feature è self-contained

- [ ] Shared contiene solo codice riutilizzabile

- [ ] Import tra feature passano per index pubblici

- [ ] Nessun import circolare

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/, api/, components/, frontend/src/app/, frontend/src/features/chat-ai/, frontend/src/features/estimates/, frontend/src/features/market-data/, frontend/src/features/portfolio/, frontend/src/shared/, hooks/, types/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.6
Area: estimates
Fase: MVP
Dipendenze: TASK 4.4

## TASK 4.6: Implementazione API Hooks per Estimates

**Descrizione:** Creare hook React Query per operazioni su stime.

**Microstep:**

1. Creare file `frontend/src/features/estimates/api/queries.ts`

2. Implementare `useEstimates(filters)`: lista stime con filtri

3. Implementare `useEstimate(id)`: singola stima con dettagli

4. Implementare `useEstimateHistory(id)`: audit trail stima

5. Creare file `frontend/src/features/estimates/api/mutations.ts`

6. Implementare `useCreateEstimate()`: creazione nuova stima

7. Implementare `useUpdateEstimate()`: aggiornamento stima

8. Implementare `useCloseEstimate()`: chiusura stima

9. Configurare invalidation corretta delle query dopo mutation

**Acceptance Criteria:**

- [ ] Hook restituiscono stati loading, error, data

- [ ] Filtri riflessi in query key per caching corretto

- [ ] Mutation invalida query correlate

- [ ] Tipi TypeScript completi

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/api/mutations.ts, frontend/src/features/estimates/api/queries.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.8
Area: estimates
Fase: MVP
Dipendenze: TASK 4.6

## TASK 4.8: Implementazione Componente EstimateForm

**Descrizione:** Creare form per creazione/modifica stime con validazione.

**Microstep:**

1. Creare file `frontend/src/features/estimates/components/EstimateForm.tsx`

2. Definire schema Zod per validazione: ticker (required), direction, target_profit_percent, stop_loss_percent, notes

3. Configurare react-hook-form con zodResolver

4. Implementare campo ticker con autocomplete (usa API search)

5. Implementare campi numerici con validazione range

6. Implementare preview calcoli: target price, stop loss price in tempo reale

7. Implementare submit con `useCreateEstimate`

8. Mostrare errori validazione inline

9. Mostrare errori API con toast/alert

**Acceptance Criteria:**

- [ ] Validazione client-side completa

- [ ] Autocomplete ticker funzionante

- [ ] Preview calcoli aggiornato in tempo reale

- [ ] Submit disabilitato durante invio

- [ ] Errori mostrati chiaramente

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/components/EstimateForm.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.9
Area: estimates
Fase: MVP
Dipendenze: TASK 4.6

## TASK 4.9: Implementazione Componente EstimateCard

**Descrizione:** Creare card per visualizzazione singola stima in lista.

**Microstep:**

1. Creare file `frontend/src/features/estimates/components/EstimateCard.tsx`

2. Mostrare ticker, direction badge, status badge

3. Mostrare prezzi: entry, current, target, stop loss

4. Mostrare P&L: valore assoluto e percentuale con colore verde/rosso

5. Mostrare data apertura, giorni aperti

6. Mostrare AI model badge, confidence score

7. Implementare click handler per navigazione a dettaglio

8. Implementare menu azioni: edit, close, delete

9. Rendere componente responsive: card su mobile, row su desktop

**Acceptance Criteria:**

- [ ] Tutti i dati chiave visibili

- [ ] Colori P&L corretti (verde positivo, rosso negativo)

- [ ] Azioni accessibili

- [ ] Layout responsive

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/components/EstimateCard.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.10
Area: estimates
Fase: MVP
Dipendenze: TASK 4.6, TASK 4.9

## TASK 4.10: Implementazione Componente EstimatesList

**Descrizione:** Creare lista stime con filtri e ordinamento.

**Microstep:**

1. Creare file `frontend/src/features/estimates/components/EstimatesList.tsx`

2. Usare `useEstimates` hook per dati

3. Implementare filtri: status dropdown, ticker autocomplete, date range (date picker)

4. Implementare ordinamento: by date, by P&L, by ticker

5. Implementare virtualizzazione lista per performance (react-window)

6. Mostrare skeleton durante loading

7. Mostrare empty state quando nessun risultato

8. Mostrare error state con retry button

9. Implementare infinite scroll o paginazione

**Acceptance Criteria:**

- [ ] Filtri aggiornano query in tempo reale

- [ ] Ordinamento funzionante

- [ ] Virtualizzazione per liste lunghe (100+ items)

- [ ] Stati loading/empty/error gestiti

- [ ] Scroll infinito o paginazione funzionante

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/components/EstimatesList.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.13
Area: portfolio
Fase: MVP
Dipendenze: TASK 4.6

## TASK 4.13: Implementazione Dashboard Portfolio

**Descrizione:** Creare dashboard con metriche aggregate portfolio.

**Microstep:**

1. Creare file `frontend/src/features/portfolio/components/Dashboard.tsx`

2. Mostrare metriche top-level: total P&L, total invested, active estimates count

3. Mostrare breakdown per status: open, closed win, closed loss

4. Implementare grafico P&L cumulativo nel tempo (Recharts)

5. Implementare grafico distribuzione per ticker (pie chart)

6. Implementare tabella top performers / worst performers

7. Usare aggregazioni server-side per performance

8. Implementare refresh periodico (ogni 5 min)

**Acceptance Criteria:**

- [ ] Metriche aggregate corrette

- [ ] Grafici interattivi con tooltip

- [ ] Performance accettabile con molti dati

- [ ] Refresh automatico funzionante

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/portfolio/, frontend/src/features/portfolio/components/Dashboard.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.14
Area: market-data
Fase: MVP
Dipendenze: TASK 4.6

## TASK 4.14: Implementazione Price Chart

**Descrizione:** Creare componente grafico prezzi con candlestick/line.

**Microstep:**

1. Creare file `frontend/src/features/market-data/components/PriceChart.tsx`

2. Accettare props: ticker, dateRange, chartType (line/candlestick)

3. Usare hook per fetch dati storici con aggregazione appropriata

4. Implementare grafico linea con Recharts

5. Implementare overlay con entry price, target, stop loss della stima associata

6. Implementare zoom in/out con cambio aggregazione (1D -> 1W -> 1M)

7. Implementare tooltip con dettagli OHLCV

8. Mostrare loading skeleton durante fetch

**Acceptance Criteria:**

- [ ] Grafico renderizza correttamente dati storici

- [ ] Zoom cambia livello aggregazione

- [ ] Overlay livelli prezzo visibili

- [ ] Tooltip informativo

- [ ] Performance fluida anche con molti datapoint

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/market-data/, frontend/src/features/market-data/components/PriceChart.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.15
Area: chat-ai
Fase: MVP
Dipendenze: TASK 4.5

## TASK 4.15: Implementazione Chat AI Component

**Descrizione:** Creare componente chat per interazione con AI.

**Microstep:**

1. Creare file `frontend/src/features/chat-ai/components/ChatInterface.tsx`

2. Implementare lista messaggi con distinzione user/assistant

3. Implementare input con invio su Enter e bottone

4. Implementare hook `useSendChatMessage` per POST a `/api/chat`

5. Mostrare indicatore "typing" durante attesa risposta

6. Supportare markdown nella risposta AI

7. Implementare scroll automatico a nuovo messaggio

8. Persistere cronologia chat in sessionStorage

**Acceptance Criteria:**

- [ ] Messaggi distinti visivamente per ruolo

- [ ] Input funziona con Enter e click

- [ ] Indicatore loading durante attesa

- [ ] Markdown renderizzato (grassetto, elenchi, codice)

- [ ] Scroll a nuovo messaggio

---

### Istruzioni per LLM
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/chat-ai/, frontend/src/features/chat-ai/components/ChatInterface.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.
