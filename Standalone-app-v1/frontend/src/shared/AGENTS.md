# AGENTS — shared

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 1.8
Area: shared
Fase: MVP
Dipendenze: -

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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/shared/, frontend/src/shared/utils/decimal.ts, frontend/src/shared/utils/financial.ts, frontend/src/shared/utils/percentage.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.4
Area: shared
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/shared/, frontend/src/shared/api/client.ts, frontend/src/shared/api/types.ts] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.5
Area: shared
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/shared/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.11
Area: shared
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/shared/, frontend/public/manifest.webmanifest, index.html] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.12
Area: shared
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/shared/, frontend/src/shared/i18n/config.ts, locales/en/common.json, locales/it/common.json] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.