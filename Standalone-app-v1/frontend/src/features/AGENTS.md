# AGENTS — features (common)

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 4.2
Area: features_common
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/, api/, components/, frontend/src/app/, frontend/src/features/chat-ai/, frontend/src/features/estimates/, frontend/src/features/market-data/, frontend/src/features/portfolio/, frontend/src/shared/, hooks/, ...] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.