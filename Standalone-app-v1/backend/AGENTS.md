# Backend - Core Application Logic

> ↗ Invarianti architetturali e workflow atomico: vedi [`../CLAUDE.md`](../CLAUDE.md) · Progress Tracker globale e grafo dipendenze: vedi [`../AGENTS.md`](../AGENTS.md)

## Scope
Questa sezione contiene SOLO task per il backend Python/FastAPI:
- Bounded context: `estimates/`, `market_data/`, `sync/`, `analytics/`, `shared/`
- Infra: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`, `scheduler/`, `outbox/`
- Value objects, repositories, services, API routes
- Database migrations (Alembic)
- Configurazione (pydantic-settings)

**Non modificare**:
- File di Docker/compose (vedi [`../docker/AGENTS.md`](../docker/AGENTS.md))
- File di test/CI (vedi [`../docs/AGENTS.md`](../docs/AGENTS.md))
- Codice frontend (vedi [`../frontend/AGENTS.md`](../frontend/AGENTS.md))

---

ID: TASK 2.7
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.1, TASK 2.3

## TASK 2.7: Definizione Modello SQLAlchemy - User e Role (RBAC Base)

**Descrizione:** Creare modelli per utenti e ruoli di base, predisponendo struttura RBAC per futuri task multi-utente.

**Microstep:**
1. Creare file `backend/src/shared/domain/user.py`
2. Definire Enum `RoleType`: ADMIN, USER, READONLY
3. Definire classe `User`: `id` (UUID), `email` (String, unique), `hashed_password` (String, nullable), `is_active` (Boolean), `created_at`, `updated_at`
4. Definire classe `Role`: `id` (UUID), `name` (RoleType), `description` (String)
5. Definire tabella associativa `user_roles` per relazione many-to-many
6. Definire relazioni bidirezionali User <-> Role

**Acceptance Criteria:**
- [x] Password mai salvata in chiaro (campo per hash)
- [x] Relazione many-to-many funzionante
- [x] Ruoli base definiti
- [x] Utente può avere multipli ruoli

---

# SEZIONE 1: LINEE GUIDA TRASVERSALI (Backend)

---

ID: TASK 1.1
Area: backend/structure
Fase: MVP
Dipendenze: -

## TASK 1.1: Setup Struttura Layer Backend

**Descrizione:** Creare la struttura di cartelle e file base per il layering esplicito del backend FastAPI.

**Microstep:**

1. Creare cartella [`backend/src/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src) come root del codice sorgente
2. Creare sottocartelle per ogni bounded context: [`estimates/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/estimates), [`market_data/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/market_data), [`sync/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/sync), [`analytics/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/analytics), [`shared/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/shared)
3. Per ogni bounded context, creare le sottocartelle: `api/`, `schemas/`, `domain/`, `services/`, `repositories/`
4. Creare cartella [`backend/src/infra/`](https://github.com/Fradbari/TickerTracker/tree/main/Standalone-app-v1/backend/src/infra) con sottocartelle: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`
5. Creare file `__init__.py` in ogni cartella
6. Creare file [`backend/src/README.md`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/README.md) che documenta la convenzione di layering

**Acceptance Criteria:**

- [x] Struttura cartelle completa e navigabile
- [x] Ogni cartella ha un `__init__.py`
- [x] README documenta lo scopo di ogni layer (api, schemas, domain, services, repositories, infra)
- [x] Nessun file di logica ancora presente (solo struttura)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.2
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.2: Definizione Modello Risposta API Standard

**Descrizione:** Creare lo schema Pydantic per il modello di risposta API uniforme usato da tutti gli endpoint.

**Microstep:**

1. Creare file [`backend/src/shared/schemas/api_response.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/schemas/api_response.py)
2. Definire schema `ApiResponse` con campi: `success` (bool), `data` (generic/nullable), `error` (nullable), `trace_id` (UUID string)
3. Definire schema `ApiError` con campi: `code` (string), `message` (string), `details` (optional dict)
4. Creare funzioni helper: `success_response(data, trace_id)`, `error_response(code, message, details, trace_id)`
5. Documentare con docstring l'uso previsto

**Acceptance Criteria:**

- [x] Schema `ApiResponse` è generico e accetta qualsiasi tipo di `data`
- [x] Schema `ApiError` è annidabile in `ApiResponse.error`
- [x] Funzioni helper producono risposte conformi allo schema
- [x] Tutti i campi hanno type hints corretti
- [x] Docstring spiega quando usare success vs error response

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/schemas/api_response.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.3
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.3: Creazione Value Object Money (Backend)

**Descrizione:** Implementare il value object immutabile `Money` per gestire importi monetari con precisione decimale.

**Microstep:**

1. Creare file [`backend/src/shared/domain/value_objects/money.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/domain/value_objects/money.py)
2. Definire dataclass frozen `Money` con campi: `amount` (Decimal), `currency` (str, default "USD")
3. Implementare `__post_init__` per convertire input non-Decimal in Decimal
4. Implementare metodi: `__add__`, `__sub__`, `__mul__` (con Decimal/int), `__neg__`
5. Implementare metodo `round(places: int)` con ROUND_HALF_UP
6. Implementare metodo `to_dict()` che restituisce `{"amount": str, "currency": str}`
7. Implementare metodo class `from_dict(data: dict)`
8. Aggiungere validazione: currency deve essere stringa 3 caratteri uppercase

**Acceptance Criteria:**

- [x] Classe è immutabile (frozen dataclass)
- [x] Tutti i calcoli usano Decimal, mai float
- [x] Somma/sottrazione tra valute diverse solleva ValueError
- [x] Moltiplicazione accetta solo Decimal o int
- [x] Serializzazione/deserializzazione round-trip funziona
- [x] Test unitari coprono tutti i metodi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/money.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.4
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.3

## TASK 1.4: Creazione Value Object Percentage (Backend)

**Descrizione:** Implementare il value object immutabile `Percentage` per gestire valori percentuali.

**Microstep:**

1. Creare file [`backend/src/shared/domain/value_objects/percentage.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/domain/value_objects/percentage.py)
2. Definire dataclass frozen `Percentage` con campo: `value` (Decimal)
3. Implementare `__post_init__` per conversione a Decimal
4. Implementare class method `from_basis_points(bps: int)`
5. Implementare metodo `apply_to(money: Money) -> Money`
6. Implementare metodo `as_multiplier() -> Decimal` (restituisce 1 + value)
7. Implementare metodi `__add__`, `__sub__` tra Percentage
8. Implementare `to_dict()` e `from_dict()`

**Acceptance Criteria:**

- [x] Classe è immutabile
- [x] Conversione da basis points corretta (100 bps = 1% = 0.01)
- [x] `apply_to` restituisce Money con importo corretto
- [x] `as_multiplier` per 10% restituisce Decimal("1.10")
- [x] Test unitari coprono tutti i metodi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/percentage.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.5
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.3, TASK 1.4

## TASK 1.5: Creazione Value Object PriceTarget (Backend)

**Descrizione:** Implementare il value object `PriceTarget` che incapsula target, stop loss e take profit con validazioni.

**Microstep:**

1. Creare file [`backend/src/shared/domain/value_objects/price_target.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/domain/value_objects/price_target.py)
2. Definire dataclass frozen `PriceTarget` con campi: `entry_price` (Money), `stop_loss` (Money), `take_profit` (Money), `direction` (Literal["LONG", "SHORT"])
3. Implementare `__post_init__` con validazioni:
   - Per LONG: stop_loss < entry_price < take_profit
   - Per SHORT: take_profit < entry_price < stop_loss
   - Tutte le currency devono corrispondere
4. Implementare metodo `risk_reward_ratio() -> Decimal`
5. Implementare metodo `is_target_hit(current_price: Money) -> bool`
6. Implementare metodo `is_stop_hit(current_price: Money) -> bool`
7. Implementare `to_dict()` e `from_dict()`

**Acceptance Criteria:**

- [x] Validazione solleva ValueError per configurazioni invalide
- [x] Risk/reward ratio calcolato correttamente per entrambe le direzioni
- [x] Metodi is_target_hit e is_stop_hit funzionano per LONG e SHORT
- [x] Test unitari coprono scenari validi e invalidi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/price_target.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.6
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.6: Configurazione Ambienti con Pydantic Settings

**Descrizione:** Implementare sistema di configurazione multi-ambiente con pydantic-settings.

**Microstep:**

1. Creare file [`backend/src/shared/infra/config.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/infra/config.py)
2. Definire classe `Settings` che eredita da `BaseSettings`
3. Definire campi per ogni ambiente: `ENVIRONMENT` (local/staging/prod), `DEBUG`, `LOG_LEVEL`
4. Definire campi database: `DATABASE_URL` (SecretStr)
5. Definire campi API esterne: `YAHOO_CACHE_TTL`, `GEMINI_API_KEY` (SecretStr), `FINNHUB_API_KEY` (SecretStr, optional)
6. Definire campi Drive: `GOOGLE_SERVICE_ACCOUNT_JSON` (SecretStr), `DRIVE_FOLDER_ID`
7. Definire campi sicurezza: `ENCRYPTION_KEY` (SecretStr), `JWT_SECRET` (SecretStr)
8. Configurare `model_config` con `env_file='.env'`, `case_sensitive=False`
9. Creare funzione `get_settings()` con cache (lru_cache)
10. Creare file [`.env.example`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/.env.example) con tutti i campi documentati

**Acceptance Criteria:**

- [x] Settings carica variabili da file .env
- [x] Tutti i secret usano tipo SecretStr
- [x] Valori di default sensati per development
- [x] `.env.example` documenta tutte le variabili richieste
- [x] `get_settings()` restituisce sempre la stessa istanza (cached)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/config.py, .env.example] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 1.7
Area: backend/shared
Fase: MVP
Dipendenze: TASK 1.6

## TASK 1.7: Middleware Sicurezza Base & Healthcheck

**Descrizione:** Aggiungere un middleware di sicurezza base (header, CORS, small rate limit) e endpoint di healthcheck per uso con Docker.

**Microstep:**

1. Creare file [`backend/src/shared/infra/security_middleware.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/infra/security_middleware.py)
2. Implementare un middleware FastAPI che:
   - Aggiunge header di sicurezza minimi (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
   - Configura CORS per l'origin del frontend (es. http://localhost:3000)
   - Implementa un rate limit molto semplice in memoria per IP (es. max 60 richieste/minuto), disattivabile via config
3. Registrare il middleware in [`backend/src/main.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/main.py) dell'app FastAPI
4. Creare router [`backend/src/shared/api/health_routes.py`](https://github.com/Fradbari/TickerTracker/blob/main/Standalone-app-v1/backend/src/shared/api/health_routes.py) con:
   - GET /health che ritorna {status: "ok"}
   - GET /health/db che prova una query SELECT 1
5. Documentare nel README come usare /health per verificare che il container backend sia up

**Acceptance Criteria:**

- [x] Tutte le risposte includono i security header base
- [x] Il frontend può chiamare il backend senza problemi di CORS
- [x] /health e /health/db risultano verdi quando il DB è raggiungibile (Mock/Basic implementato)
- [x] Il rate limit può essere disabilitato via Settings

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/security_middleware.py, backend/src/shared/api/health_routes.py, backend/src/main.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

---

ID: TASK 2.1
Area: backend/infra
Fase: MVP
Dipendenze: -

## TASK 2.1: Setup Progetto Python con Poetry & Dipendenze Complete

**Descrizione:** Inizializzare pyproject.toml con TUTTE le dipendenze necessarie per MVP e Fase 2, evitando installazioni frammentate.

**Microstep:**

1. Creare `backend/pyproject.toml` con metadata progetto
2. Configurare dipendenze MVP:
   - Core: fastapi, uvicorn[standard], pydantic, pydantic-settings
   - Database: sqlalchemy[asyncio], asyncpg, alembic
   - API esterne: google-api-python-client, google-auth-httplib2, google-auth-oauthlib, yfinance
   - Cache: redis[hiredis]
   - Scheduler: apscheduler
3. Configurare dipendenze Fase 2 (opzionali):
   - Security: cryptography, slowapi
   - Observability: structlog, prometheus-client
4. Configurare dipendenze sviluppo: pytest, pytest-asyncio, pytest-cov, ruff, mypy, httpx
5. Configurare tool.ruff, tool.mypy, tool.pytest.ini_options
6. Creare `Makefile`, `.python-version`, `scripts/check_deps.py`
7. Esportare `requirements.txt` e `requirements-dev.txt`

**Acceptance Criteria:**

- [x] `poetry install` completa senza errori
- [x] `make check-deps` verifica dipendenze critiche (simulato con verify script)
- [x] `requirements*.txt` sincronizzati con pyproject.toml
- [x] TASK 2.1 può partire immediatamente senza installare altro

---

ID: TASK 2.3
Area: backend/infra
Fase: MVP
Dipendenze: TASK 2.1

## TASK 2.3: Setup SQLAlchemy Base + Modello Ticker

**Descrizione:** Inizializzare l'infrastruttura di persistenza async e definire il modello Ticker.

**Microstep:**
1. Configurare `shared/infra/database.py` con async engine, session factory e Base declarative
2. Definire `market_data/domain/entities.py` con modello `Ticker`
3. Aggiungere campi: `id` (UUID), `symbol`, `name`, `exchange`, `currency`, `asset_type`
4. Aggiungere audit: `created_at`, `updated_at`
5. Aggiungere vincoli: unique e index su `symbol`

**Acceptance Criteria:**
- [x] Base importabile da `shared.infra.database`
- [x] Async engine si connette a PostgreSQL Docker
- [x] `get_db()` dependency funziona con FastAPI
- [x] Modello `Ticker` ha tutti i campi richiesti
- [x] UUID generato automaticamente
- [x] Timestamps gestiti automaticamente
- [x] Constraint unique su `symbol`
- [x] Indice su `symbol` definito

---

ID: TASK 2.4
Area: backend/domain
Fase: MVP
Dipendenze: TASK 2.3

## TASK 2.4: Definizione Modello SQLAlchemy - Estimate

**Descrizione:** Creare il modello SQLAlchemy per l'entità Estimate (stime/previsioni).

**Microstep:**
1. Creare file `backend/src/estimates/domain/entities.py`
2. Definire classe `Estimate` che eredita da Base
3. Definire colonne identificative: `id` (UUID, PK), `ticker_id` (FK to Ticker), `user_id` (FK to User, nullable)
4. Definire colonne prezzo: `start_price`, `target_price`, `stop_loss_price` (DECIMAL 10,4)
5. Definire colonne target: `target_profit_percent`, `stop_loss_percent` (DECIMAL 8,4)
6. Definire colonne stato: `status` (Enum), `direction` (Enum LONG/SHORT)
7. Definire colonne AI: `ai_model`, `ai_confidence`, `ai_reasoning`
8. Definire colonne date: `created_at`, `updated_at`, `closed_at`
9. Definire colonne esito: `exit_price`, `realized_pnl`

**Acceptance Criteria:**
- [x] Tutti i campi prezzo usano DECIMAL, non FLOAT
- [x] Enums definiti come tipi Python Enum
- [x] Foreign key a Ticker definita correttamente
- [x] Indici ottimizzati per query frequenti (incluso partial index su status='OPEN')
- [x] Campi nullable marcati esplicitamente

---

ID: TASK 2.5
Area: backend/domain
Fase: MVP
Dipendenze: TASK 2.4

## TASK 2.5: Definizione Modello SQLAlchemy - EstimateEvent (Event Sourcing)

**Descrizione:** Creare il modello per Event Sourcing delle stime.

**Microstep:**
1. Creare file `backend/src/estimates/domain/events.py`
2. Definire Enum `EstimateEventType`
3. Definire classe `EstimateEvent` con `id` (UUID), `estimate_id`, `event_type`, `event_data` (JSONB)
4. Aggiungere `user_id` e `timestamp`
5. Definire indice composto su `(estimate_id, timestamp)`

**Acceptance Criteria:**
- [x] Eventi sono immutabili (append-only)
- [x] JSONB usato per flessibilità dati evento
- [x] Indice permette query efficienti per timeline
- [x] Ogni tipo evento documentato nel Enum
---

ID: TASK 2.6
Area: backend/domain
Fase: MVP
Dipendenze: TASK 2.3

## TASK 2.6: Definizione Modello SQLAlchemy - MarketData

**Descrizione:** Creare il modello per dati storici di mercato (OHLCV).

**Microstep:**
1. Creare file `backend/src/market_data/domain/market_data.py`
2. Definire classe `MarketData` che eredita da Base
3. Definire colonne OHLCV: `ticker_id` (FK), `date`, `open`, `high`, `low`, `close` (DECIMAL), `volume` (BigInteger)
4. Definire PK composta: `(ticker_id, date)`
5. Definire colonne lineage: `data_source`, `ingested_at`, `quality_score`
6. Definire indici e check constraints per validazione OHLC

**Acceptance Criteria:**
- [x] PK composta impedisce duplicati per ticker+data
- [x] Tutti i prezzi usano DECIMAL
- [x] Volume usa BigInteger per supportare valori grandi
- [x] Metadati lineage presenti per audit
- [x] Check constraints validano relazioni H>=L, H>=O, H>=C, L<=O, L<=C
- [x] Helper properties per calcoli (day_range, day_change, day_change_percent)

---

ID: TASK 2.8
Area: backend/sync
Fase: MVP
Dipendenze: TASK 1.1

## TASK 2.8: Definizione Modello SQLAlchemy - SyncJob

**Descrizione:** Creare modello per tracciare i job di sincronizzazione con Google Drive.

**Microstep:**
1. Creare file `backend/src/sync/domain/entities.py`
2. Definire Enum `SyncJobType`: INITIAL_IMPORT, DAILY_HISTORY_UPDATE, ON_ESTIMATE_SAVE, MANUAL_SYNC
3. Definire Enum `SyncJobStatus`: PENDING, RUNNING, COMPLETED, FAILED, PARTIAL
4. Definire classe `SyncJob` con i seguenti campi:
   - `id` (UUID, PK)
   - `job_type` (Enum, non nullo)
   - `status` (Enum, non nullo, default: PENDING)
   - `started_at` (DateTime, non nullo, default: datetime.utcnow)
   - `finished_at` (DateTime, nullo)
   - `error_message` (Text, nullo)
   - `filename` (String, non nullo)
   - `checksum_before` (String, nullo)
   - `checksum_after` (String, nullo)
   - `records_processed` (Integer, non nullo, default: 0)
   - `records_failed` (Integer, non nullo, default: 0)
5. Aggiungere indice su `started_at`
6. Aggiornare documentazione e test

**Acceptance Criteria:**
- [x] Modello creato con tutti i campi richiesti
- [x] Enum definiti correttamente
- [x] Indice su `started_at` presente
- [ ] Documentazione aggiornata
- [ ] Test di import completati
- [ ] Migrazione Alembic generata

---

ID: TASK 2.9
Area: backend/analytics
Fase: MVP
Dipendenze: TASK 1.1

## TASK 2.9: Definizione Modello SQLAlchemy - AiModelRun

**Descrizione:** Creare modello per tracciare esecuzioni dei modelli AI.

**Microstep:**
1. Creare file `backend/src/analytics/domain/entities.py`
2. Definire classe `AiModelRun`: `id` (UUID), `estimate_id` (FK, nullable), `model_name` (String), `model_version` (String), `prompt_hash` (String), `prompt_tokens` (Integer), `completion_tokens` (Integer), `latency_ms` (Integer), `output_summary` (Text), `raw_response` (JSONB), `created_at`
3. Definire indice su `model_name` e `created_at`

**Acceptance Criteria:**
- [x] Traccia consumo token per monitoraggio costi
- [x] Hash del prompt per deduplicazione
- [x] Latenza per performance monitoring
- [x] JSONB per risposta raw flessibile

---

ID: TASK 2.10
Area: backend/database
Fase: MVP
Dipendenze: TASK 2.1-2.9

## TASK 2.10: Setup Alembic e Generazione Migrazione Iniziale

**Descrizione:** Configurare Alembic per gestire le migrazioni del database e generare la migrazione iniziale con tutte le tabelle definite nei task precedenti.

**Microstep:**
1. Installare Alembic: `pip install alembic`
2. Inizializzare Alembic nella directory backend: `alembic init alembic`
3. Configurare `alembic.ini`:
   - Impostare `script_location = alembic` (non `backend/alembic`)
   - Impostare `sqlalchemy.url` da variabile ambiente DATABASE_URL
4. Configurare `alembic/env.py`:
   - Importare tutti i modelli SQLAlchemy (Ticker, MarketData, Estimate, EstimateEvent, SyncJob, AiModelRun, User, Role)
   - Configurare `target_metadata = Base.metadata` (non `None`)
   - Configurare async context manager per asyncpg
   - Separare logica sincrona (do_run_migrations) da async (run_migrations_online)
5. Creare file `.env` con DATABASE_URL
6. Generare migrazione iniziale: `alembic revision --autogenerate -m "initial schema"`
7. Verificare file di migrazione generato in `alembic/versions/`
8. Applicare migrazione: `alembic upgrade head`
9. Verificare tabelle create nel database: `docker exec tickertracker-db psql -U tickertracker -d tickertracker_dev -c "\dt"`

**Problemi Risolti:**
- ✅ `target_metadata = None` → Importati tutti i modelli e configurato `Base.metadata`
- ✅ `script_location = backend/alembic` → Corretto in `alembic`
- ✅ TypeError con async context manager → Separato sync callback da async function
- ✅ Partial index con Enum → Usato `text("status = 'OPEN'")` invece di Column comparison

**Acceptance Criteria:**
- [x] Alembic configurato correttamente
- [x] Migrazione iniziale generata con successo (f9f513c6220d)
- [x] Migrazione applicata al database
- [x] 10 tabelle create: tickers, market_data, estimates, estimate_events, ai_model_runs, sync_jobs, users, roles, user_roles, alembic_version
- [x] Tutti gli indici e foreign keys creati
- [x] Script di verifica eseguito con successo (verify_task_2_7.py)

---

ID: TASK 2.11
Area: backend/database
Fase: MVP
Dipendenze: TASK 2.10

## TASK 2.11: Creazione Materialized View per CQRS - Estimate Summary

**Descrizione:** Creare una materialized view PostgreSQL per ottimizzare le query del dashboard, pre-calcolando join e metriche aggregate (pattern CQRS - Command Query Responsibility Segregation).

**Rationale:**
Le query del dashboard richiedono join complessi tra `estimates` e `market_data` (per ottenere il prezzo corrente) e calcoli di metriche derivate (PnL corrente, giorni aperti, livello di rischio). Una materialized view pre-calcola questi dati per query < 50ms.

**Microstep:**
1. Creare migrazione Alembic: `alembic revision -m "create estimate_summary_view materialized view"`
2. Definire SQL per creazione materialized view in `upgrade()`:
   - Base: tutti i campi da `estimates`
   - Join LATERAL con `market_data` per ottenere ultimo prezzo disponibile
   - Campi calcolati:
     - `current_price`: ultimo prezzo da market_data (fallback a start_price)
     - `current_pnl`: PnL non realizzato per OPEN, realized_pnl per CLOSED
     - `current_pnl_percent`: PnL in percentuale
     - `days_open`: giorni da created_at (o a closed_at se chiuso)
     - `risk_level`: LOW/MEDIUM/HIGH basato su stop_loss_percent
3. Creare indici sulla materialized view:
   - Unique index su `id` (richiesto per CONCURRENT refresh)
   - Index su `status` (per filtrare OPEN/CLOSED)
   - Index su `ticker_id` (per filtri per ticker)
   - Composite index su `(status, created_at DESC)` (per ordinamento cronologico)
4. Definire SQL per `downgrade()`: DROP MATERIALIZED VIEW
5. Creare script utility `backend/scripts/refresh_estimate_summary_view.py`:
   - Supporto per refresh concorrente (default, no lock)
   - Supporto per refresh standard (con lock, più veloce)
   - Opzione `--stats` per mostrare statistiche post-refresh
6. Creare script di test `backend/test_estimate_summary_view.py`:
   - Creare dati di esempio (2 ticker, 30 giorni market data, 3 estimates)
   - Test 1: query tutti gli estimates dalla view
   - Test 2: query solo estimates OPEN
   - Test 3: performance test (target < 50ms)
   - Test 4: concurrent refresh funziona

**Problemi Risolti:**
- ✅ Ticker initialization: usare `name` non `company_name`, aggiungere `exchange`, `currency`, `asset_type`
- ✅ LEFT JOIN LATERAL per ottenere ultimo market_data disponibile
- ✅ Unique index su `id` per abilitare REFRESH MATERIALIZED VIEW CONCURRENTLY

**Risultati Test:**
```
📊 Query Performance: 3-5ms (target < 50ms) ✅
🔄 Concurrent Refresh: 12.15ms ✅
📈 Metriche: current_price, current_pnl, current_pnl_percent, days_open, risk_level ✅
```

**Acceptance Criteria:**
- [x] Materialized view creata con successo (migrazione e97b3b8578e1)
- [x] Query restituisce dati corretti con metriche calcolate
- [x] Refresh concorrente funziona senza lock
- [x] Performance query < 50ms (attuale: 3-5ms)
- [x] Script refresh_estimate_summary_view.py funzionante
- [x] Test di validazione passati con successo
- [x] Documentazione completa in docs/ESTIMATE_SUMMARY_VIEW.md

**Documentazione:**
- [docs/ESTIMATE_SUMMARY_VIEW.md](./docs/ESTIMATE_SUMMARY_VIEW.md) - Guida completa all'uso della materialized view
- [ALEMBIC_SETUP_COMPLETED.md](./ALEMBIC_SETUP_COMPLETED.md) - Setup migrazioni Alembic

**Usage:**
```bash
# Refresh manuale
python scripts/refresh_estimate_summary_view.py

# Con statistiche
python scripts/refresh_estimate_summary_view.py --stats

# Query dalla view
SELECT * FROM estimate_summary_view WHERE status = 'OPEN' ORDER BY created_at DESC;
```

---

ID: TASK 2.24
Area: backend/infra
Fase: MVP
Dipendenze: TASK 2.22

## TASK 2.24: Setup Background Worker (APScheduler)

**Descrizione:** Configurare worker per job schedulati di sync e aggiornamento.

**Microstep:**
1. Installata dipendenza `apscheduler` (requirements.txt)
2. Creato file `src/infra/scheduler/scheduler.py` con AsyncIOScheduler (UTC)
3. Definiti job:
   - `refresh_market_data`: ogni 5 minuti (lun-ven, 14-21 UTC)
   - `daily_history_sync`: ogni giorno alle 23:00 UTC
   - `refresh_materialized_views`: ogni 5 minuti
   - `check_targets`: ogni minuto
4. Logging automatico inizio/fine job, errori, durata, successo/fallimento
5. Hook FastAPI startup/shutdown per avvio/shutdown scheduler
6. Errori nei job non bloccano l'applicazione

**Acceptance Criteria:**
- [x] Scheduler parte con l'applicazione
- [x] Job eseguono agli orari configurati
- [x] Shutdown graceful dei job in corso
- [x] Errori nei job non crashano l'applicazione

**File Creati/Modificati:**
- `src/infra/scheduler/scheduler.py` - Implementazione scheduler e job
- `src/main.py` - Integrazione hook startup/shutdown
- `requirements.txt` - Aggiornato con apscheduler
- `README.md` - Sezione Background Worker
- `AGENTS.md` - Progress tracker aggiornato

**Note:**
- Tutti i job sono wrappati per logging e metriche
- Possibile estendere con Prometheus/metrics
- Stato e log visibili in console/app log

---

ID: TASK 2.25
Area: backend/infra
Fase: MVP
Dipendenze: TASK 2.24

## TASK 2.25: Completa Pattern Outbox per Eventi Drive

**Descrizione:** Implementare pattern Outbox per delivery affidabile degli eventi EstimateEvent verso Google Drive con retry logic e dead letter handling.

**Context:**
- EstimateEvent esteso con campi outbox (`processed_at`, `retry_count`, `error`)
- Migrazione Alembic applicata
- EstimateService salva eventi atomicamente nella stessa transazione

**Microstep:**
1. Aggiunto metodi helper `EstimateEvent`: `mark_processed()`, `mark_failed()`, `can_retry()`, `is_dead_letter()`, `get_unprocessed()`, `get_dead_letters()`
2. Creato `OutboxProcessor` in `src/infra/outbox/outbox_processor.py`:
   - `process_pending_events()`: processa eventi non processati con retry logic
   - `handle_dead_letters()`: gestisce eventi con max retry (5) e log error
   - Transaction isolation: ogni evento commit separato
   - Graceful degradation per `SyncService` assente
3. Creato jobs scheduler in `src/infra/scheduler/jobs.py`:
   - `process_outbox_events()`: ogni 30s
   - `handle_dead_letters()`: ogni giorno alle 02:00 UTC
   - `configure_jobs()`: dependency injection per session_factory e sync_service
4. Aggiornato `src/infra/scheduler/scheduler.py`: registrazione job outbox
5. Mapping event_type → Drive action:
   - `CREATED/UPDATED/CLOSED` → sync_estimate_to_drive
   - Altri eventi → skip (log debug, mark processed)
6. Test completi:
   - Unit tests: `tests/unit/outbox/test_outbox_processor.py` (95%+ coverage)
   - E2E tests: `tests/e2e/test_outbox_e2e.py` (flow completo)

**Acceptance Criteria:**
- [x] Eventi salvati atomicamente con estimates (già implementato)
- [x] OutboxProcessor processa eventi ogni 30s via scheduler
- [x] Retry automatico con max 5 tentativi
- [x] Dead letter dopo 5 retry: log.error() + mark "DEAD_LETTER"
- [x] Transaction isolation: ogni evento commit separato
- [x] Test coverage > 90% per OutboxProcessor
- [x] No perdita eventi: transazioni atomiche + retry logic

**File Creati/Modificati:**
- `src/estimates/domain/events.py` - Metodi helper outbox
- `src/infra/outbox/__init__.py` - Package outbox
- `src/infra/outbox/outbox_processor.py` - OutboxProcessor completo
- `src/infra/scheduler/jobs.py` - Job implementations
- `src/infra/scheduler/scheduler.py` - Registrazione job outbox
- `tests/unit/outbox/test_outbox_processor.py` - Test unitari (13 test cases)
- `tests/e2e/test_outbox_e2e.py` - Test E2E (6 scenari)
- `README.md` - Sezione Pattern Outbox dettagliata
- `AGENTS.md` - Progress tracker aggiornato

**Note Architettura:**
- EstimateService non modificato: eventi già salvati correttamente
- Eventi IMMUTABILI: solo processed_at/retry_count/error modificabili post-creazione
- Drive sync idempotente: stesso evento riprovato N volte è safe
- Graceful degradation: SyncService assente/ImportError → log warning, continua
- Structured logging: tutti i log con context (event_id, estimate_id, retry_count)
- Dead letter placeholder: ready per Slack/Email webhook futuro

---

ID: TASK 3.10
Area: backend/infra, backend/shared
Fase: Post-MVP
Dipendenze: TASK 3.6, TASK 3.7
Status: ✅ COMPLETATO

## TASK 3.10: Configurazione Connection Pooling Ottimizzato

**Descrizione:** Ottimizzare pool connessioni database per performance e resilienza.

**Implementazione completata:**

1. Aggiunti 5 campi pool in `Settings` (`config.py`): `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`, `DB_POOL_PRE_PING`
2. Riscritto `database.py`: rimosso `NullPool` import, engine usa `AsyncAdaptedQueuePool` con parametri da Settings, aggiunta `get_pool_status()`, log strutturato
3. Aggiunte 4 Gauge Prometheus (`db_pool_checked_out/in/overflow/size`) + `update_pool_metrics()` in `metrics.py`
4. `/metrics` endpoint chiama `update_pool_metrics()` prima di ogni scrape
5. `/health` include `connection_pool` nel body; nuovo endpoint `GET /health/pool`
6. `/health/pool` aggiunto a `API_KEY_EXEMPT_PATHS`

**File Creati/Modificati:**
- `src/shared/infra/config.py` (5 nuovi campi pool)
- `src/shared/infra/database.py` (riscritto)
- `src/shared/infra/__init__.py` (export get_pool_status)
- `src/infra/metrics/metrics.py` (4 Gauge + update_pool_metrics)
- `src/infra/metrics/__init__.py` (export aggiornati)
- `src/infra/metrics/routes.py` (update_pool_metrics su scrape)
- `src/shared/api/health_routes.py` (/health/pool + connection_pool)
- `tests/unit/infra/test_connection_pool.py` (NUOVO — 20 test)

**Acceptance Criteria:**
- [x] Pool configurato correttamente per ambiente
- [x] pre_ping evita connessioni stale
- [x] Metriche pool esposte
- [x] Nessun connection leak sotto carico


---

ID: TASK 3.11
Area: backend/shared, market_data
Fase: Fase 2
Dipendenze: TASK 3.10

## TASK 3.11: Implementazione Query Pagination Cursor-Based

**Descrizione:** Paginazione efficiente basata su cursore per grandi dataset.
Prestazioni O(1) per pagina indipendentemente dalla profondità.

**File Creati/Modificati:**
- `src/shared/repositories/pagination.py` (NUOVO — modulo completo)
- `src/shared/repositories/__init__.py` (export pubblici)
- `src/shared/schemas/api_response.py` (aggiunto `trace_id` default, `make_success()` classmethod, `Optional` typing)
- `src/market_data/repositories/market_data_repository.py` (aggiunto `get_history_paginated()`)
- `src/market_data/api/dependencies.py` (aggiunto `get_market_data_repository()`)
- `src/market_data/api/routes.py` (nuove schema `PaginatedHistoryItem`, `PaginatedHistoryResponse`; endpoint `GET /api/market/history/{ticker}/paginated`; helper `_resolve_ticker_id()`)
- `tests/unit/shared/test_pagination.py` (NUOVO — 42 test)

**Acceptance Criteria:**
- [x] Cursore opaco (base64url-encoded JSON, non manipolabile)
- [x] Performance O(1) indipendente dalla pagina
- [x] Navigazione avanti (NEXT) e indietro (PREV) funzionante
- [x] Coesistenza con filtri start/end date su `get_history_paginated()`
- [x] Gestione edge case: prima pagina, ultima pagina, dataset vuoto
- [x] Endpoint `GET /api/market/history/{ticker}/paginated` con validazione 400/404
- [x] 42 unit test: encode/decode cursore, CursorPagination, PaginatedResult, apply_cursor_pagination, repository logic, API endpoint

**Note tecniche:**
- Il cursore codifica `{"date": "YYYY-MM-DD"}` come chiave di sort.
- `apply_cursor_pagination()` riceve `cursor_value` già decodificato e castato (es. `date`) dal caller.
- `get_history_paginated()` gestisce internamente decode del cursore e filtri start/end.
- Endpoint `/api/market/history/{ticker}/paginated` accede ai dati localmente sincronizzati (PostgreSQL), non a Yahoo Finance live.
