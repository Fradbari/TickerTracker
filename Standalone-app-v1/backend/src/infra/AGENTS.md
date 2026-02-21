# AGENTS — infra

ID: TASK 2.20
Area: infra
Fase: MVP
Dipendenze: -
**Status: ✅ COMPLETED**

## TASK 2.20: Implementazione Google Drive Client

**Descrizione:** Creare client per interazione con Google Drive API.

**Microstep:**

1\. ✅ Creare file `backend/src/infra/drive/client.py`

2\. ✅ Definire classe `GoogleDriveClient`

3\. ✅ Implementare autenticazione con Service Account usando credenziali da Settings

4\. ✅ Implementare metodo `list_files(folder_id: str) -> List[DriveFile]`

5\. ✅ Implementare metodo `download_file(file_id: str) -> bytes`

6\. ✅ Implementare metodo `upload_file(folder_id: str, filename: str, content: bytes, mime_type: str) -> DriveFile`

7\. ✅ Implementare metodo `update_file(file_id: str, content: bytes) -> DriveFile`

8\. ✅ Implementare metodo `create_temp_file(folder_id: str, filename: str) -> DriveFile` per pattern file temporaneo

9\. ✅ Implementare metodo `delete_file(file_id: str) -> bool`

10\. ✅ Aggiungere logging e metriche per ogni operazione

**Acceptance Criteria:**

- [x] Autenticazione funziona con Service Account
- [x] Tutte le operazioni CRUD funzionano
- [x] Errori API gestiti con eccezioni tipizzate
- [x] Timeout configurabile

**Implementation Details:**

Files created:
- `src/infra/drive/client.py` - GoogleDriveClient with async methods
- `src/infra/drive/models.py` - DriveFile and DriveFileMetadata dataclasses
- `src/infra/drive/exceptions.py` - Typed exceptions for Drive operations
- `tests/infra/test_drive_client.py` - 16 unit tests (all passing)

Features:
- Async API using asyncio.run_in_executor for blocking Google API calls
- Service account authentication via JSON credentials
- Full CRUD operations: list, download, upload, update, delete, create_temp
- Comprehensive error handling with typed exceptions
- Structured logging for all operations
- Configurable timeout for API operations

Test Coverage: 16/16 tests passing ✅

### Sync Engine & retro‑compatibilità (TASK 2.20-2.23)

Questi task coprono il nuovo Sync Engine con Google Drive e garantiscono la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) tramite test E2E dedicati.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, backend/src/infra/drive/client.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.24
Area: infra
Fase: MVP
Dipendenze: TASK 2.11, TASK 2.22

## TASK 2.24: Setup Background Worker (APScheduler)

**Descrizione:** Configurare worker per job schedulati di sync e aggiornamento.

**Microstep:**

1\. Installare dipendenza `apscheduler`

2\. Creare file `backend/src/infra/scheduler/scheduler.py`

3\. Configurare `AsyncIOScheduler` con timezone UTC

4\. Definire job `refresh_market_data`: ogni 5 minuti durante orari di mercato

5\. Definire job `daily_history_sync`: ogni giorno alle 23:00 UTC

6\. Definire job `refresh_materialized_views`: ogni 5 minuti

7\. Definire job `check_targets`: ogni minuto per verificare hit target/stop

8\. Implementare hook startup/shutdown per FastAPI

9\. Aggiungere logging per inizio/fine ogni job

10\. Aggiungere metrica per durata e successo/fallimento job

**Acceptance Criteria:**

- [ ] Scheduler parte con l'applicazione

- [ ] Job eseguono agli orari configurati

- [ ] Shutdown graceful dei job in corso

- [ ] Errori nei job non crashano l'applicazione

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, backend/src/infra/scheduler/scheduler.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.25
Area: infra
Fase: MVP
Dipendenze: TASK 2.24

# @workspace — TASK 2.25: Completa Pattern Outbox per Eventi Drive

## Context
- ✅ **EstimateEvent** esteso con campi outbox (`processed_at`, `retry_count`, `error`) — commit `d271aef`
- ✅ **Migrazione Alembic** applicata
- ✅ **EstimateService** salva eventi **atomicamente** nella stessa transazione

---

## Implementazione Richiesta

### 1) AGGIUNGI METODI HELPER `EstimateEvent`
**File:** `src/estimates/domain/events.py`

```python
def mark_processed(self) -> None:
    """Mark event as successfully processed."""
    self.processed_at = datetime.now(timezone.utc)
    self.error = None

def mark_failed(self, error_msg: str) -> None:
    """Mark event processing failed, increment retry."""
    self.retry_count += 1
    self.error = error_msg[:500]  # Truncate to DB limit

def can_retry(self) -> bool:
    """Check if event can be retried (max 5 attempts)."""
    return self.retry_count < 5 and self.processed_at is None

def is_dead_letter(self) -> bool:
    """Check if event is dead letter (max retries exceeded)."""
    return self.retry_count >= 5 and self.processed_at is None

@classmethod
async def get_unprocessed(cls, session: AsyncSession, limit: int = 100) -> List['EstimateEvent']:
    """Get unprocessed events for outbox processing."""
    result = await session.execute(
        select(cls)
        .where(cls.processed_at.is_(None))
        .where(cls.retry_count < 5)
        .order_by(cls.timestamp.asc())
        .limit(limit)
    )
    return result.scalars().all()

@classmethod
async def get_dead_letters(cls, session: AsyncSession) -> List['EstimateEvent']:
    """Get dead letter events (max retries exceeded)."""
    result = await session.execute(
        select(cls)
        .where(cls.processed_at.is_(None))
        .where(cls.retry_count >= 5)
        .order_by(cls.timestamp.asc())
    )
    return result.scalars().all()
```

---

### 2) OUTBOX PROCESSOR SERVICE
**File:** `src/infra/outbox/outbox_processor.py`

```python
class OutboxProcessor:
    def __init__(self, session_factory: async_sessionmaker, sync_service: SyncService):
        self._session_factory = session_factory
        self._sync_service = sync_service

    async def process_pending_events(self) -> dict:
        """
        Process unprocessed events with Drive sync.
        Returns: {"processed": int, "failed": int, "skipped": int}
        """
        # Get unprocessed events
        # For each event:
        #   - Try sync_estimate_to_drive if event_type in [CREATED, UPDATED, CLOSED]
        #   - On success: mark_processed() and commit
        #   - On failure: mark_failed(error) and commit
        #   - Each event in separate transaction for isolation
        # Log metrics

    async def handle_dead_letters(self) -> int:
        """
        Handle dead letter events (log + mark).
        Returns: count of dead letters found
        """
        # Get dead letters
        # For each: log.error with full details (estimate_id, event_type, error)
        # Mark error as "DEAD_LETTER: <original_error>"
        # Prepare for future alerting (Slack/Email hook placeholder)
```

---

### 3) SCHEDULER INTEGRATION
**File:** `src/infra/scheduler/jobs.py`  
- Job `process_outbox_events()`: istanzia `OutboxProcessor`, chiama `process_pending_events()`  
- Log strutturato: `{"job": "outbox", "processed": X, "failed": Y}`

**File:** `src/infra/scheduler/scheduler.py`  
- Register: `IntervalTrigger(seconds=30)` per `process_outbox_events`  
- Register: `CronTrigger(hour=2, minute=0)` per `handle_dead_letters`

---

### 4) SYNC SERVICE INTEGRATION
**File:** `src/infra/outbox/outbox_processor.py`

Implementa mapping **event_type → Drive action**:
- `CREATED` / `UPDATED` → `sync_service.sync_estimate_to_drive(estimate_id)`
- `CLOSED` → idem (Drive deve riflettere stato)
- Altri eventi → **skip** (log **debug**)

Gestisci `ImportError` per `SyncService` con **graceful degradation** (log **warning**, **skip** processing).

---

### 5) TESTS OBBLIGATORI

**File:** `tests/unit/outbox/test_outbox_processor.py`
```python
# test_process_single_event_success: mock SyncService, verify mark_processed
# test_process_event_failure_increments_retry: mock exception, verify retry_count++
# test_dead_letter_after_5_failures: simulate 5 failures, verify is_dead_letter
# test_event_isolation: 10 eventi, 1 fail non blocca altri 9
# test_get_unprocessed_excludes_processed: verify query logic
```

**File:** `tests/integration/test_outbox_e2e.py`
```python
# test_create_estimate_persists_unprocessed_event: create estimate, verify event with processed_at is NULL
# test_outbox_processor_processes_event: insert event, run processor, verify processed_at set
# test_retry_logic: simulate Drive error, verify retry_count incremented
```

---

## Acceptance Criteria VINCOLANTI
- Eventi salvati **atomicamente** con estimates (già implementato)
- `OutboxProcessor` processa eventi **ogni 30s** via scheduler
- **Retry automatico** con **max 5** tentativi (no exponential backoff necessario)
- **Dead letter** dopo 5 retry: `log.error()` + mark `"DEAD_LETTER: <error>"`
- **Transaction isolation**: ogni evento **commit separato**
- **Test coverage > 80%** per `OutboxProcessor` e metodi helper
- **No perdita eventi**: transazioni atomiche + retry logic garantiscono delivery

---

## Note Critiche Architettura
- **EstimateService non modificare**: eventi già salvati correttamente
- Eventi **IMMUTABILI**: `processed_at` / `retry_count` / `error` sono gli **unici** campi modificabili post‑creazione
- **Drive sync idempotente**: stesso evento riprovato *N* volte deve essere safe
- **Graceful degradation**: se `SyncService` non esiste/importabile, `OutboxProcessor` log warning e continua
- **Structured logging**: tutti i log devono avere context (`event_id`, `estimate_id`, `retry_count`)

---

## Dipendenze Verificate
- ✅ `EstimateEvent` con campi outbox (**commit `d271aef`**)
- ✅ **Alembic migration** (**commit `d271aef`**)
- ✅ **APScheduler** (TASK **2.24**)
- ⚠️ `SyncService.sync_estimate_to_drive()` **potrebbe non esistere**: gestire `ImportError`

---

# SEZIONE 3: SICUREZZA, OSSERVABILITÀ, GOVERNANCE

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.1
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.1: Implementazione Security Middleware

Priorità: Fase 2 (necessario solo in scenari multi‑utente / produzione, NON blocca l'ambiente locale single‑user).

**Descrizione:** Creare middleware FastAPI per sicurezza centralizzata.

**Microstep:**

1\. Creare file `backend/src/infra/security/middleware.py`

2\. Definire classe `SecurityMiddleware`

3\. Implementare aggiunta security headers a ogni response:

- `X-Content-Type-Options: nosniff`

- `X-Frame-Options: DENY`

- `X-XSS-Protection: 1; mode=block`

- `Strict-Transport-Security` (solo se HTTPS)

- `Content-Security-Policy` configurabile

4\. Implementare validazione API key da header `X-API-Key` (opzionale, configurabile)

5\. Implementare logging request con campi: method, path, status, duration, client_ip

6\. Registrare middleware in applicazione FastAPI

**Acceptance Criteria:**

- [x] Headers presenti in tutte le response

- [x] API key validata se configurata

- [x] Logging strutturato per ogni request

- [x] Middleware non rallenta significativamente (<1ms overhead)

**Implementazione Completata (Task 3.1):**

File creati/modificati:
- `src/infra/security/middleware.py` – `SecurityMiddleware(BaseHTTPMiddleware)`:
  headers statici + HSTS condizionale (HTTPS only) + CSP configurabile +
  validazione `X-API-Key` con exempt paths + logging strutturato (structlog)
- `src/infra/security/__init__.py` – esporta `SecurityMiddleware`, `register_security_middleware`
- `src/shared/infra/config.py` – nuovi campi: `ENABLE_API_KEY_AUTH`, `API_KEY`,
  `API_KEY_EXEMPT_PATHS`, `CSP_POLICY`, `REQUEST_LOG_ENABLED`
- `src/shared/infra/security_middleware.py` – `setup_security_middleware` chiama
  `register_security_middleware` come layer più esterno (ultimo registrato)
- `tests/unit/infra/test_security_middleware.py` – 29 test, tutti verdi

Test risultati: 310/310 passed (29 nuovi + 281 precedenti)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, backend/src/infra/security/middleware.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.2
Area: infra
Fase: Fase 2
Dipendenze: TASK 3.1
**Status: ✅ COMPLETED**

## TASK 3.2: Implementazione Rate Limiting

Priorità: Fase 2 (necessario solo in scenari multi‑utente / produzione, NON blocca l'ambiente locale single‑user).

**Descrizione:** Aggiungere rate limiting per protezione API tramite slowapi + Redis.

**Microstep:**

1\. ✅ Aggiungere 7 nuovi campi a `src/shared/infra/config.py` (`REDIS_URL`, `RATE_LIMIT_SLOWAPI_ENABLED`, `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_CHAT`, `RATE_LIMIT_ESTIMATES_POST`, `RATE_LIMIT_MARKET_PRICE`, `RATE_LIMIT_WHITELIST_IPS`)

2\. ✅ Creare file `src/infra/security/rate_limit.py` con `_build_limiter()`, singleton `limiter`, `is_whitelisted()`, `_rate_limit_exceeded_handler()`, `setup_rate_limiter()`

3\. ✅ Configurare `Limiter` con storage Redis (fallback automatico a memory:// se Redis non disponibile)

4\. ✅ Definire limiti di default: 100 req/minuto per IP; per-endpoint: estimates POST 30/min, market price 60/min, chat 10/min

5\. ✅ Implementare `_RequestContextMiddleware` (ContextVar) per supporto whitelist IP zero-arg (richiesto da slowapi)

6\. ✅ Implementare response 429 con header `Retry-After` e `X-RateLimit-Limit` nel body JSON standard `ApiResponse`

7\. ✅ Aggiungere whitelist per IP interni/loopback (`127.0.0.1`, `::1`)

8\. ✅ Aggiornare `src/infra/security/__init__.py`, `src/main.py`, route handlers estimates e market_data

**Acceptance Criteria:**

- [x] Rate limit applicato correttamente (per-route e default)

- [x] Storage Redis per condivisione tra istanze (con memory fallback)

- [x] Response 429 include Retry-After e X-RateLimit-Limit

- [x] Whitelist funzionante (zero-arg via ContextVar)

**Implementazione Completata (Task 3.2):**

File creati/modificati:
- `src/infra/security/rate_limit.py` – `_build_limiter()`, `limiter` singleton, `_RequestContextMiddleware`, `is_whitelisted()` (zero-arg), `_rate_limit_exceeded_handler()`, `setup_rate_limiter()`
- `src/infra/security/__init__.py` – aggiunge esportazione `limiter`, `is_whitelisted`, `setup_rate_limiter`
- `src/shared/infra/config.py` – 7 nuovi campi rate limiting
- `src/main.py` – `setup_rate_limiter(app)` aggiunto prima di `setup_security_middleware`
- `src/estimates/api/routes.py` – `@limiter.limit("30/minute")` su `create_estimate` + `request: Request, response: Response`
- `src/market_data/api/routes.py` – `@limiter.limit("60/minute")` su `get_current_price` + `request: Request`
- `.env.example` – 7 nuove variabili con commenti nella sezione Rate Limiting
- `tests/unit/infra/test_rate_limit.py` – 33 test (8 classi: _client_ip, is_whitelisted, _build_limiter, setup_rate_limiter, 429 handler, integration enforced, whitelist, settings defaults)

Quirk rilevante: `from __future__ import annotations` nei file test causa PEP 563 string annotations; con functools.wraps il wrapper usa `__globals__` di slowapi (non del test module) — FastAPI non riesce a resolvere `'StarletteRequest'` e tratta il param come query. Fix: rimuovere `from __future__ import annotations` dal file di test.

Test risultati: 315/315 passed (33 nuovi + 282 precedenti)

---

### Istruzioni per LLM
- Non modificare file fuori da [`src/infra/security/rate_limit.py`, `src/estimates/api/routes.py`, `src/market_data/api/routes.py`] se non strettamente necessario.
- Endpoint decorati con `@limiter.limit()` DEVONO avere `request: Request` E `response: Response` come parametri.
- `is_whitelisted()` è zero-arg (legge da ContextVar); l'ordine middleware è: `_RequestContextMiddleware` DOPO `SlowAPIMiddleware` in `add_middleware` (Starlette: ultimo aggiunto = più esterno).
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.4
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.4: Implementazione Encryption at Rest

**Descrizione:** Creare tipo SQLAlchemy per campi cifrati nel database.

**Microstep:**

1\. Creare file `backend/src/infra/security/encryption.py`

2\. Implementare classe `EncryptedString` che estende `TypeDecorator`

3\. Usare `cryptography.fernet` per cifratura simmetrica

4\. Implementare `process_bind_param`: cifra prima di salvare

5\. Implementare `process_result_value`: decifra dopo lettura

6\. Chiave di cifratura da Settings (SecretStr)

7\. Documentare campi che usano questo tipo

8\. Implementare utility per rotazione chiave

**Acceptance Criteria:**

- [ ] Dati cifrati nel DB non leggibili direttamente

- [ ] Lettura/scrittura trasparente per l'applicazione

- [ ] Chiave gestita in modo sicuro

- [ ] Procedura rotazione documentata

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, backend/src/infra/security/encryption.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.5
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.5: Setup Structured Logging con Correlation ID

**Descrizione:** Configurare logging strutturato JSON con correlation ID per tracing.

**Microstep:**

1\. Installare dipendenza `structlog`

2\. Creare file `backend/src/infra/logging/config.py`

3\. Configurare structlog con processors: add_log_level, TimeStamper(ISO), JSONRenderer

4\. Creare ContextVar `correlation_id` per request tracing

5\. Creare middleware che:

- Legge header `X-Correlation-ID` o genera nuovo UUID

- Imposta ContextVar

- Aggiunge correlation_id alla response

6\. Creare processor structlog che aggiunge correlation_id a ogni log

7\. Configurare livelli log da Settings (DEBUG in dev, INFO in prod)

**Acceptance Criteria:**

- [ ] Tutti i log sono JSON

- [ ] Correlation ID presente in ogni log entry

- [ ] Correlation ID propagato in response header

- [ ] Livello log configurabile per ambiente

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, backend/src/infra/logging/config.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.6
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.6: Implementazione Metriche Prometheus

Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).

**Descrizione:** Esporre metriche business e tecniche per monitoring.

**Microstep:**

1\. Installare dipendenza `prometheus-client`

2\. Creare file `backend/src/infra/metrics/metrics.py`

3\. Definire metriche business:

- `Counter` estimates_created_total (labels: ticker, ai_model)

- `Counter` estimates_closed_total (labels: ticker, outcome)

- `Gauge` active_estimates_total (labels: status)

- `Gauge` current_portfolio_pnl

4\. Definire metriche tecniche:

- `Histogram` api_request_duration_seconds (labels: endpoint, method, status)

- `Counter` yahoo_api_calls_total (labels: endpoint, status)

- `Counter` drive_sync_operations_total (labels: operation, status)

- `Counter` cache_hits_total / cache_misses_total (labels: cache_name)

5\. Creare endpoint `GET /metrics` che espone metriche in formato Prometheus

6\. Creare helper decorator `@track_duration` per misurare latenza

**Acceptance Criteria:**

- [ ] Endpoint /metrics restituisce formato Prometheus valido

- [ ] Metriche aggiornate in tempo reale

- [ ] Labels permettono drill-down

- [ ] Histogram ha bucket appropriati per latenze

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, GET /metrics, backend/src/infra/metrics/metrics.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.7
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.7: Implementazione Health Checks Completi

Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).

**Descrizione:** Creare endpoint health check per tutte le dipendenze.

**Microstep:**

1\. Creare file `backend/src/infra/health/health_service.py`

2\. Definire dataclass `ComponentHealth`: name, status (HEALTHY/DEGRADED/UNHEALTHY), latency_ms, message

3\. Definire dataclass `SystemHealth`: status, version, uptime_seconds, components

4\. Implementare check per ogni componente:

- Database: `SELECT 1`

- Redis: `PING`

- Yahoo API: get price per AAPL (ticker sempre disponibile)

- Google Drive: list files nella folder configurata

5\. Implementare `check_all()` che esegue check in parallelo

6\. Creare endpoint `GET /health` con SystemHealth completo

7\. Creare endpoint `GET /health/ready` per Kubernetes readiness (solo DB)

8\. Creare endpoint `GET /health/live` per Kubernetes liveness (solo processo vivo)

**Acceptance Criteria:**

- [ ] /health restituisce stato tutti i componenti

- [ ] Componenti non critici in DEGRADED non rendono sistema UNHEALTHY

- [ ] /health/ready fallisce se DB non disponibile

- [ ] /health/live sempre OK se processo risponde

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, GET /health, GET /health/live, GET /health/ready, backend/src/infra/health/health_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.12
Area: infra
Fase: MVP
Dipendenze: -

## TASK 5.12: Implementare Feature Flags

**Descrizione:** Creare sistema feature flags per rollout graduali.

**Microstep:**

1\. Creare file `backend/src/infra/feature_flags/service.py`

2\. Definire Enum `FeatureFlag` con flag iniziali: NEW_DASHBOARD_UI, AI_RECOMMENDATIONS, DRIVE_SYNC_V2

3\. Implementare `FeatureFlagService` con storage Redis

4\. Implementare metodo `is_enabled(flag, user_id)`: check globale, poi percentage rollout, poi whitelist

5\. Implementare metodo `enable(flag, percentage)`

6\. Implementare metodo `disable(flag)`

7\. Creare endpoint admin `POST /api/admin/feature-flags` per gestione

8\. Creare dependency FastAPI per inject service

**Acceptance Criteria:**

- [ ] Flag possono essere abilitati globalmente

- [ ] Rollout percentuale funziona (deterministico per user)

- [ ] Whitelist override funziona

- [ ] Stato flag persistito in Redis

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, POST /api/admin/feature-flags, backend/src/infra/feature_flags/service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.13
Area: infra
Fase: MVP
Dipendenze: -

## TASK 5.13: Implementare Backup Automatico

**Descrizione:** Creare sistema backup database automatico.

**Microstep:**

1\. Creare file `backend/scripts/backup.py`

2\. Implementare funzione `create_full_backup()`:

- Esegui pg_dump con compressione

- Cifra output con Fernet (chiave da settings)

- Upload a storage (S3 o Drive folder dedicato)

- Log risultato

3\. Implementare funzione `verify_backup(backup_path)`:

- Scarica backup

- Decifra

- Verifica con pg_restore --list

4\. Schedulare backup giornaliero (APScheduler o cron)

5\. Schedulare verifica settimanale

6\. Implementare retention policy: mantieni ultimi 30 backup

7\. Implementare alerting su fallimento

**Acceptance Criteria:**

- [ ] Backup creato giornalmente

- [ ] Backup cifrato

- [ ] Verifica integrità funzionante

- [ ] Alert su fallimento

- [ ] Cleanup vecchi backup automatico

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, backend/scripts/backup.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 5.17
Area: infra
Fase: MVP
Dipendenze: -

## TASK 5.17: Creare Script Migrazione Dati v2.4 -> v3.0

**Descrizione:** Script per migrare dati da versione legacy.

**Microstep:**

1\. Creare file `backend/scripts/migrate_from_legacy.py`

2\. Implementare funzione `connect_to_drive()`: autenticazione

3\. Implementare funzione `download_legacy_data()`: scarica JSON e CSV da Drive

4\. Implementare funzione `parse_legacy_json(content)`: parsing stime legacy

5\. Implementare funzione `parse_legacy_history(content)`: parsing prezzi storici

6\. Implementare funzione `transform_to_new_schema(legacy_data)`: mapping campi

7\. Implementare funzione `validate_transformed_data(data)`: validazione

8\. Implementare funzione `import_to_database(data)`: insert nel nuovo DB

9\. Implementare funzione `verify_migration()`: confronto conteggi e totali

10\. Creare report migrazione con statistiche

**Acceptance Criteria:**

- [ ] Script eseguibile da riga di comando

- [ ] Tutti i dati legacy importati

- [ ] Validazione previene import dati corrotti

- [ ] Report finale mostra successo/errori

- [ ] Idempotente (rilanciabile senza duplicati)

---

# APPENDICE: Dipendenze tra Task

Priorità MVP (ambiente locale single‑user):

- Sezione 1: tutti i task 1.1-1.8.

- Sezione 2: 2.1-2.6, 2.10, 2.12-2.13, 2.16-2.21, 2.24-2.27.

- Sezione 3: solo 3.10 (facoltativo) e 3.12 (obbligatorio); il resto è Fase 2.

- Sezione 4: 4.1-4.10, 4.7; 4.11-4.12 subito dopo se vuoi completare UX.

- Sezione 5: almeno test unitari/lint (5.x base), E2E/CI/CD restano Fase 2.

```

Sezione 1 (Setup base):

1.1 → 1.2 → 1.3 → 1.4 → 1.5

1.6 (parallelo a 1.3-1.5)

1.8 (parallelo, richiede solo 1.1)

Sezione 2 (Backend):

2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6 → 2.10

2.7, 2.8, 2.9 (paralleli dopo 2.3)

2.11 (richiede 2.4, 2.6)

2.12 (richiede 2.4, 2.10)

2.13 (richiede 2.6, 2.10)

2.14 (richiede 2.12)

2.15 (richiede 2.5, 2.12)

2.16 (richiede 2.14)

2.17 → 2.18 → 2.19

2.20 → 2.21 → 2.22 → 2.23 (collegati 2.21, 2.22, 2.23)

2.24 (richiede 2.11, 2.22)

2.25 (richiede 2.24)

Sezione 3 (Sicurezza/Observability):

Tutti paralleli dopo completamento 2.20.

- 3.12: priorità alta (MVP locale).

- 3.10: priorità media (post-MVP).

- 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.11: Fase 2 (opzionali per uso single‑user).

Sezione 4 (Frontend):

4.1 → 4.2 → 4.3 → 4.4

4.5 → 4.6, 4.7, 4.8 , 4.9, 4.10, 4.11, 4.12

4.13 (richiede 4.6)

4.14 (richiede 4.6)

4.15 (richiede 4.5)

Sezione 5 (Testing/CI):

5.1 → 5.2, 5.3, 5.4, 5.5

5.6 → 5.7

5.8 (richiede 5.1, 5.6)

5.9 (richiede 5.4)

5.10 (richiede 5.4, 5.7)

5.11 (richiede 5.10)

5.12-5.17 (paralleli dopo setup base)

```

---

# NOTE PER L'LLM ESECUTORE

1\. **Esegui un task alla volta** e verifica gli acceptance criteria prima di procedere

2\. **Chiedi chiarimenti** se un requisito è ambiguo

3\. **Documenta** ogni scelta implementativa non ovvia

4\. **Testa** ogni componente prima di passare al successivo

5\. **Committa** con messaggi descrittivi che referenziano il task ID

6\. **Segnala** blocchi o dipendenze mancanti

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/, backend/scripts/, Sezione 1 (Setup base):

1.1 → 1.2 → 1.3 → 1.4 → 1.5

1.6 (parallelo a 1.3-1.5)

1.8 (parallelo, richiede solo 1.1)

Sezione 2 (Backend):

2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6 → 2.10

2.7, 2.8, 2.9 (paralleli dopo 2.3)

2.11 (richiede 2.4, 2.6)

2.12 (richiede 2.4, 2.10)

2.13 (richiede 2.6, 2.10)

2.14 (richiede 2.12)

2.15 (richiede 2.5, 2.12)

2.16 (richiede 2.14)

2.17 → 2.18 → 2.19

2.20 → 2.21 → 2.22 → 2.23 (collegati 2.21, 2.22, 2.23)

2.24 (richiede 2.11, 2.22)

2.25 (richiede 2.24)

Sezione 3 (Sicurezza/Observability):

Tutti paralleli dopo completamento 2.20.

- 3.12: priorità alta (MVP locale).

- 3.10: priorità media (post-MVP).

- 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.11: Fase 2 (opzionali per uso single‑user).

Sezione 4 (Frontend):

4.1 → 4.2 → 4.3 → 4.4

4.5 → 4.6, 4.7, 4.8 , 4.9, 4.10, 4.11, 4.12

4.13 (richiede 4.6)

4.14 (richiede 4.6)

4.15 (richiede 4.5)

Sezione 5 (Testing/CI):

5.1 → 5.2, 5.3, 5.4, 5.5

5.6 → 5.7

5.8 (richiede 5.1, 5.6)

5.9 (richiede 5.4)

5.10 (richiede 5.4, 5.7)

5.11 (richiede 5.10)

5.12-5.17 (paralleli dopo setup base), backend/scripts/migrate_from_legacy.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.