# AGENTS — estimates

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 4.6
Area: features_estimates
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/api/mutations.ts, frontend/src/features/estimates/api/queries.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.8
Area: features_estimates
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/components/EstimateForm.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.9
Area: features_estimates
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/components/EstimateCard.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.10
Area: features_estimates
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/estimates/, frontend/src/features/estimates/components/EstimatesList.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.