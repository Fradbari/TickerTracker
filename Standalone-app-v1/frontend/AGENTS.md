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
6. Creare cart
