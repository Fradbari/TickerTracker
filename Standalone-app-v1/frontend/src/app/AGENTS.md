# AGENTS — app

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 4.1
Area: app
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/app/, @hookform/resolvers, @tanstack/react-query, app/, features/, shared/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.3
Area: app
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/app/, frontend/src/app/providers/QueryProvider.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 4.7
Area: app
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/app/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.