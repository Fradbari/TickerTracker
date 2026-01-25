# AGENTS — chat-ai

## Regole generali (Frontend)
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).

ID: TASK 4.15
Area: features_chat_ai
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
- **Regola**: tutti i calcoli finanziari devono usare il wrapper decimale (es. `frontend/src/shared/finance/decimalMoney.ts` **oppure** `frontend/src/shared/utils/financial.ts`/`decimal.ts`). Non usare mai il tipo `number` JS per calcoli/arrotondamenti; converti input da form/JSON in Decimal nel wrapper.
- **Regola**: tutte le chiamate HTTP devono passare da `frontend/src/shared/api/client.ts` (client centralizzato, con interceptor e tipi). È vietato usare `fetch`/`axios` direttamente nei componenti o hook di feature; usa gli helper tipizzati e gli hook (`useApiQuery`/`useApiMutation`).
- Non modificare file fuori da [frontend/src/features/chat-ai/, frontend/src/features/chat-ai/components/ChatInterface.tsx] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.