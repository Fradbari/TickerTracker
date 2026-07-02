# Scheduler & Outbox Pattern

Il backend usa `APScheduler` per job periodici (sync Drive, refresh materialized view, target check) **e** il pattern Outbox per la delivery affidabile di eventi verso Google Drive.

## Scheduler

**Tipo:** `AsyncIOScheduler` (timezone UTC)
**Lifecycle:** avvio automatico su FastAPI startup, shutdown graceful su FastAPI shutdown
**Logging:** inizio/fine job, durata, successo/fallimento via `structlog` (vedi `LOGGING.md`)

### Job schedulati

| Job ID | Cadenza | Cosa fa |
|---|---|---|
| `process_outbox_events` | ogni 30s | Preleva eventi non processati da `estimate_events` e li dispatcha |
| `handle_dead_letters` | 02:00 UTC / giorno | Gestione eventi con 5 retry falliti |
| `refresh_market_data` | ogni 5 min (lun-ven 14:00-21:55 UTC) | Ingest price Yahoo per simboli aperti |
| `daily_history_sync` | 23:00 UTC / giorno | Sync end-of-day OHLCV |
| `refresh_materialized_views` | ogni 5 min | `REFRESH MATERIALIZED VIEW CONCURRENTLY estimate_summary_view` |
| `check_targets` | ogni minuto | Verifica target/stop su stime OPEN, auto-close |

Tutti i job sono implementati in `src/infra/scheduler/jobs.py` e registrati in `src/infra/scheduler/scheduler.py` con wrapper per logging e metriche.

Vedi anche `backend/docs/METRICS.md` per `@track_duration` applicato ai job.

## Pattern Outbox

Garantisce **delivery affidabile** degli eventi verso Google Drive anche in caso di failure di rete/API.

### Funzionamento (5 fasi)

1. **Salvataggio atomico**: l'evento (nuova stima, update, close) viene salvato nella **stessa transazione** che modifica l'aggregate root (`Estimate`).
2. **Polling asincrono**: il job `process_outbox_events` legge da `estimate_events` ogni 30s.
3. **Transaction isolation**: ogni evento viene processato in una transazione separata (no lock global).
4. **Retry con backoff esponenziale**: max 5 retry, poi `DEAD_LETTER`.
5. **Dead Letter Queue**: eventi con 5 retry falliti → tabella/log `dead_letter` con `error` field. Alert placeholder per Slack/Email webhook (vedi `LOGGING.md`).

### Campi che mutano sull'evento

`EstimateEvent` è **append-only** (`created_at` immutabile). Solo questi 3 campi sono aggiornabili:

| Campo | Tipo | Quando |
|---|---|---|
| `processed_at` | timestamp | Quando il job lo ha marcato processato |
| `retry_count` | int | Incrementato ad ogni failure |
| `error` | str | Ultimo messaggio di errore |

### Mapping event → sync action

| Event type | `CREATED` / `UPDATED` / `CLOSED` | `PRICE_UPDATED` / `TARGET_HIT` / `STOP_HIT` / `REOPENED` |
|---|---|---|
| Sync Drive? | Sì → `sync_estimate_to_drive(estimate_id)` | No → solo `mark_processed()` |
| Retry su failure | Sì (fino a 5) | N/A |

### Idempotenza

I consumer di `sync_estimate_to_drive(**)` **devono essere idempotenti**: la re-delivery dopo un retry è uno scenario atteso, non un bug.

### Graceful degradation

Se `SyncService` non è disponibile o `sync_estimate_to_drive()` non è registrato:
- ⚠️ log warning (no crash)
- evento marcato processato
- il processing continua sugli eventi successivi

### File chiave

| File | Cosa contiene |
|---|---|
| `src/infra/outbox/outbox_processor.py` | `OutboxProcessor` con `process_pending()` / `handle_dead_letters()` |
| `src/infra/scheduler/jobs.py` | Definizioni dei job APScheduler |
| `src/infra/scheduler/scheduler.py` | Bootstrap `AsyncIOScheduler` + shutdown graceful |
| `src/estimates/domain/estimate_event.py` | `EstimateEvent.mark_processed()` / `mark_failed()` / `can_retry()` / `is_dead_letter()` |
| `src/estimates/repositories/estimate_event_repository.py` | `get_unprocessed()` / `get_dead_letters()` |

### ⚠️ Gotcha percorso

L'outbox **NON** vive in `backend/src/sync/` — quel folder è solo per Google Drive sync, CSV/JSON parsers, e `sync_job` repository.
Outbox + Dead Letter sono in **`backend/src/infra/outbox/`**.

### Test coverage

- Unit: `tests/unit/outbox/test_outbox_processor.py` (95%+ coverage)
- E2E: `tests/e2e/test_outbox_e2e.py` (flow completo: create → process → Drive)

## Vedere anche

- Runbook Yahoo outage (ops): [`../../Docs/runbook/yahoo-outage.md`](../../Docs/runbook/yahoo-outage.md)
- Runbook monitoring (ops): [`../../Docs/runbook/monitoring.md`](../../Docs/runbook/monitoring.md)
