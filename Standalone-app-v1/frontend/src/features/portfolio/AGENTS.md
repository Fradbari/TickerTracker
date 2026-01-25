# AGENTS — portfolio

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 4.13
Area: features_portfolio
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/portfolio/, frontend/src/features/portfolio/components/Dashboard.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.