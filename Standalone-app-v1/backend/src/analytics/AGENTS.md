# AGENTS — analytics

ID: TASK 2.9
Area: analytics
Fase: Fase 2
Dipendenze: TASK 2.3

## TASK 2.9: Definizione Modello SQLAlchemy - AiModelRun

**Descrizione:** Creare modello per tracciare esecuzioni dei modelli AI.

**Microstep:**

1\. Creare file `backend/src/analytics/domain/entities.py`

2\. Definire classe `AiModelRun`: `id` (UUID), `estimate_id` (FK, nullable), `model_name` (String), `model_version` (String), `prompt_hash` (String), `prompt_tokens` (Integer), `completion_tokens` (Integer), `latency_ms` (Integer), `output_summary` (Text), `raw_response` (JSONB), `created_at`

3\. Definire indice su `model_name` e `created_at`

**Acceptance Criteria:**

- [ ] Traccia consumo token per monitoraggio costi

- [ ] Hash del prompt per deduplicazione

- [ ] Latenza per performance monitoring

- [ ] JSONB per risposta raw flessibile

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/analytics/, backend/src/analytics/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.11
Area: analytics
Fase: MVP
Dipendenze: TASK 2.4, TASK 2.6

## TASK 2.11: Creazione Materialized View EstimateSummaryView (CQRS)

**Descrizione:** Creare materialized view per query dashboard ottimizzate.

**Microstep:**

1\. Creare migrazione Alembic per materialized view

2\. Definire view `estimate_summary_view` con colonne: tutti i campi Estimate + `current_price` (da ultima MarketData), `current_pnl`, `current_pnl_percent`, `days_open`, `risk_level` (calcolato)

3\. Creare indici sulla materialized view: su `status`, su `ticker_id`

4\. Creare funzione/comando per refresh: `REFRESH MATERIALIZED VIEW CONCURRENTLY`

5\. Documentare che la view richiede indice unique per refresh concurrente

**Acceptance Criteria:**

- [ ] View creata con successo

- [ ] Query su view restituisce dati corretti

- [ ] Refresh concurrente funziona senza lock

- [ ] Performance query < 50ms per lista stime

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/analytics/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.