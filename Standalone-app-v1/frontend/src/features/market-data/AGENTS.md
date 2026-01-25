# AGENTS — market-data

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 4.14
Area: features_market_data
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/market-data/, frontend/src/features/market-data/components/PriceChart.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.