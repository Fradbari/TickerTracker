# Backend

ID: TASK 1.1
Area: backend
Fase: MVP
Dipendenze: -

## TASK 1.1: Setup Struttura Layer Backend

**Descrizione:** Creare la struttura di cartelle e file base per il layering esplicito del backend FastAPI.

**Microstep:**

1\. Creare cartella `backend/src/` come root del codice sorgente

2\. Creare sottocartelle per ogni bounded context: `estimates/`, `market_data/`, `sync/`, `analytics/`, `shared/`

3\. Per ogni bounded context, creare le sottocartelle: `api/`, `schemas/`, `domain/`, `services/`, `repositories/`

4\. Creare cartella `backend/src/infra/` con sottocartelle: `yahoo/`, `drive/`, `cache/`, `logging/`, `security/`

5\. Creare file `__init__.py` in ogni cartella

6\. Creare file `README.md` in `backend/src/` che documenta la convenzione di layering

**Acceptance Criteria:**

- [ ] Struttura cartelle completa e navigabile

- [ ] Ogni cartella ha un `__init__.py`

- [ ] README documenta lo scopo di ogni layer (api, schemas, domain, services, repositories, infra)

- [ ] Nessun file di logica ancora presente (solo struttura)

---

### Istruzioni per LLM
- Non modificare file fuori da [README.md, __init__.py, analytics/, api/, backend/src/, backend/src/infra/, cache/, domain/, ...] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.2
Area: backend
Fase: MVP
Dipendenze: TASK 1.1

## TASK 1.2: Definizione Modello Risposta API Standard

**Descrizione:** Creare lo schema Pydantic per il modello di risposta API uniforme usato da tutti gli endpoint.

**Microstep:**

1\. Creare file `backend/src/shared/schemas/api_response.py`

2\. Definire schema `ApiResponse` con campi: `success` (bool), `data` (generic/nullable), `error` (nullable), `trace_id` (UUID string)

3\. Definire schema `ApiError` con campi: `code` (string), `message` (string), `details` (optional dict)

4\. Creare funzioni helper: `success_response(data, trace_id)`, `error_response(code, message, details, trace_id)`

5\. Documentare con docstring l'uso previsto

**Acceptance Criteria:**

- [ ] Schema `ApiResponse` è generico e accetta qualsiasi tipo di `data`

- [ ] Schema `ApiError` è annidabile in `ApiResponse.error`

- [ ] Funzioni helper producono risposte conformi allo schema

- [ ] Tutti i campi hanno type hints corretti

- [ ] Docstring spiega quando usare success vs error response

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/schemas/api_response.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.3
Area: backend
Fase: MVP
Dipendenze: TASK 1.2

## TASK 1.3: Creazione Value Object Money (Backend)

**Descrizione:** Implementare il value object immutabile `Money` per gestire importi monetari con precisione decimale.

**Microstep:**

1\. Creare file `backend/src/shared/domain/value_objects/money.py`

2\. Definire dataclass frozen `Money` con campi: `amount` (Decimal), `currency` (str, default "USD")

3\. Implementare `__post_init__` per convertire input non-Decimal in Decimal

4\. Implementare metodi: `__add__`, `__sub__`, `__mul__` (con Decimal/int), `__neg__`

5\. Implementare metodo `round(places: int)` con ROUND_HALF_UP

6\. Implementare metodo `to_dict()` che restituisce `{"amount": str, "currency": str}`

7\. Implementare metodo class `from_dict(data: dict)`

8\. Aggiungere validazione: currency deve essere stringa 3 caratteri uppercase

**Acceptance Criteria:**

- [ ] Classe è immutabile (frozen dataclass)

- [ ] Tutti i calcoli usano Decimal, mai float

- [ ] Somma/sottrazione tra valute diverse solleva ValueError

- [ ] Moltiplicazione accetta solo Decimal o int

- [ ] Serializzazione/deserializzazione round-trip funziona

- [ ] Test unitari coprono tutti i metodi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/money.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.4
Area: backend
Fase: MVP
Dipendenze: TASK 1.3

## TASK 1.4: Creazione Value Object Percentage (Backend)

**Descrizione:** Implementare il value object immutabile `Percentage` per gestire valori percentuali.

**Microstep:**

1\. Creare file `backend/src/shared/domain/value_objects/percentage.py`

2\. Definire dataclass frozen `Percentage` con campo: `value` (Decimal)

3\. Implementare `__post_init__` per conversione a Decimal

4\. Implementare class method `from_basis_points(bps: int)`

5\. Implementare metodo `apply_to(money: Money) -> Money`

6\. Implementare metodo `as_multiplier() -> Decimal` (restituisce 1 + value)

7\. Implementare metodi `__add__`, `__sub__` tra Percentage

8\. Implementare `to_dict()` e `from_dict()`

**Acceptance Criteria:**

- [ ] Classe è immutabile

- [ ] Conversione da basis points corretta (100 bps = 1% = 0.01)

- [ ] `apply_to` restituisce Money con importo corretto

- [ ] `as_multiplier` per 10% restituisce Decimal("1.10")

- [ ] Test unitari coprono tutti i metodi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/percentage.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.5
Area: backend
Fase: MVP
Dipendenze: TASK 1.4

## TASK 1.5: Creazione Value Object PriceTarget (Backend)

**Descrizione:** Implementare il value object `PriceTarget` che incapsula target, stop loss e take profit con validazioni.

**Microstep:**

1\. Creare file `backend/src/shared/domain/value_objects/price_target.py`

2\. Definire dataclass frozen `PriceTarget` con campi: `entry_price` (Money), `stop_loss` (Money), `take_profit` (Money), `direction` (Literal["LONG", "SHORT"])

3\. Implementare `__post_init__` con validazioni:

- Per LONG: stop_loss < entry_price < take_profit

- Per SHORT: take_profit < entry_price < stop_loss

- Tutte le currency devono corrispondere

4\. Implementare metodo `risk_reward_ratio() -> Decimal`

5\. Implementare metodo `is_target_hit(current_price: Money) -> bool`

6\. Implementare metodo `is_stop_hit(current_price: Money) -> bool`

7\. Implementare `to_dict()` e `from_dict()`

**Acceptance Criteria:**

- [ ] Validazione solleva ValueError per configurazioni invalide

- [ ] Risk/reward ratio calcolato correttamente per entrambe le direzioni

- [ ] Metodi is_target_hit e is_stop_hit funzionano per LONG e SHORT

- [ ] Test unitari coprono scenari validi e invalidi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/value_objects/price_target.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.6
Area: backend
Fase: MVP
Dipendenze: TASK 1.3, TASK 1.4, TASK 1.5

## TASK 1.6: Configurazione Ambienti con Pydantic Settings

**Descrizione:** Implementare sistema di configurazione multi-ambiente con pydantic-settings.

**Microstep:**

1\. Creare file `backend/src/shared/infra/config.py`

2\. Definire classe `Settings` che eredita da `BaseSettings`

3\. Definire campi per ogni ambiente: `ENVIRONMENT` (local/staging/prod), `DEBUG`, `LOG_LEVEL`

4\. Definire campi database: `DATABASE_URL` (SecretStr)

5\. Definire campi API esterne: `YAHOO_CACHE_TTL`, `GEMINI_API_KEY` (SecretStr), `FINNHUB_API_KEY` (SecretStr, optional)

6\. Definire campi Drive: `GOOGLE_SERVICE_ACCOUNT_JSON` (SecretStr), `DRIVE_FOLDER_ID`

7\. Definire campi sicurezza: `ENCRYPTION_KEY` (SecretStr), `JWT_SECRET` (SecretStr)

8\. Configurare `model_config` con `env_file='.env'`, `case_sensitive=False`

9\. Creare funzione `get_settings()` con cache (lru_cache)

10\. Creare file `.env.example` con tutti i campi documentati

**Acceptance Criteria:**

- [ ] Settings carica variabili da file .env

- [ ] Tutti i secret usano tipo SecretStr

- [ ] Valori di default sensati per development

- [ ] `.env.example` documenta tutte le variabili richieste

- [ ] `get_settings()` restituisce sempre la stessa istanza (cached)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/config.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.7
Area: backend
Fase: MVP
Dipendenze: TASK 1.1

**TASK 1.7: Middleware Sicurezza Base & Healthcheck**

**Descrizione:**  
Aggiungere un middleware di sicurezza base (header, CORS, small rate limit) e endpoint di healthcheck per uso con Docker.

**Microstep:**

- Creare file backend/src/shared/infra/security_middleware.py.
- Implementare un middleware FastAPI che:
  - Aggiunge header di sicurezza minimi (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection).
  - Configura CORS per l'origin del frontend (es. <http://localhost:3000>).
  - Implementa un rate limit molto semplice in memoria per IP (es. max 60 richieste/minuto), disattivabile via config.
- Registrare il middleware in main.py dell'app FastAPI.
- Creare router backend/src/shared/api/health_routes.py con:
  - GET /health che ritorna {status: "ok"}.
  - GET /health/db che prova una query SELECT 1.
- Documentare nel README come usare /health per verificare che il container backend sia up.

**Acceptance Criteria:**

- Tutte le risposte includono i security header base.
- Il frontend può chiamare il backend senza problemi di CORS.
- /health e /health/db risultano verdi quando il DB è raggiungibile.
- Il rate limit può essere disabilitato via Settings per uso locale se non necessario.

Nota: per scenari multi‑utente avanzati esistono estensioni in SEZIONE 3 (TASK 3.1-3.2) che arricchiscono sicurezza e rate limiting.

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.1
Area: backend
Fase: MVP
Dipendenze: -

## TASK 2.1: Setup Progetto Python con Poetry/uv

**Descrizione:** Inizializzare il progetto Python backend con dependency management moderno.

**Microstep:**

1\. Creare file `backend/pyproject.toml` con metadata progetto

2\. Configurare dipendenze principali: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic, pydantic-settings

3\. Configurare dipendenze sviluppo: pytest, pytest-asyncio, pytest-cov, ruff, mypy, httpx

4\. Configurare sezione `[tool.ruff]` per linting

5\. Configurare sezione `[tool.mypy]` con strict mode

6\. Configurare sezione `[tool.pytest.ini_options]`

7\. Creare file `backend/.python-version` con versione 3.11+

8\. Creare `backend/Makefile` con comandi: install, lint, typecheck, test, run

**Acceptance Criteria:**

- [ ] `poetry install` o `uv sync` completa senza errori

- [ ] `make lint` esegue ruff senza errori

- [ ] `make typecheck` esegue mypy senza errori

- [ ] `make test` esegue pytest

- [ ] `make run` avvia server uvicorn

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/.python-version, backend/Makefile, backend/pyproject.toml] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.3
Area: backend
Fase: MVP
Dipendenze: TASK 2.2

## TASK 2.3: Definizione Modello SQLAlchemy - Ticker

**Descrizione:** Creare il modello SQLAlchemy per l'entità Ticker (anagrafica titoli).

**Microstep:**

1\. Creare file `backend/src/market_data/domain/entities.py`

2\. Definire classe `Ticker` che eredita da Base

3\. Definire colonne: `id` (UUID, PK), `symbol` (String 10, unique), `name` (String 255), `exchange` (String 50), `currency` (String 3), `asset_type` (String 20: stock/etf/crypto)

4\. Definire colonne audit: `created_at`, `updated_at` con default e onupdate

5\. Definire indice su `symbol`

6\. Definire `__repr__` per debug

**Acceptance Criteria:**

- [ ] Modello ha tutti i campi richiesti con tipi corretti

- [ ] UUID generato automaticamente se non fornito

- [ ] Timestamps gestiti automaticamente

- [ ] Indice su symbol definito

- [ ] Constraint unique su symbol

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.4
Area: backend
Fase: MVP
Dipendenze: TASK 2.3

## TASK 2.4: Definizione Modello SQLAlchemy - Estimate

**Descrizione:** Creare il modello SQLAlchemy per l'entità Estimate (stime/previsioni).

**Microstep:**

1\. Creare file `backend/src/estimates/domain/entities.py`

2\. Definire classe `Estimate` che eredita da Base

3\. Definire colonne identificative: `id` (UUID, PK), `ticker_id` (FK to Ticker), `user_id` (FK to User, nullable per ora)

4\. Definire colonne prezzo: `start_price` (DECIMAL 10,4), `target_price` (DECIMAL 10,4), `stop_loss_price` (DECIMAL 10,4)

5\. Definire colonne target: `target_profit_percent` (DECIMAL 8,4), `stop_loss_percent` (DECIMAL 8,4)

6\. Definire colonne stato: `status` (Enum: OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_MANUAL, EXPIRED), `direction` (Enum: LONG, SHORT)

7\. Definire colonne AI: `ai_model` (String), `ai_confidence` (DECIMAL 5,2), `ai_reasoning` (Text)

8\. Definire colonne date: `created_at`, `updated_at`, `closed_at` (nullable)

9\. Definire colonne esito: `exit_price` (DECIMAL 10,4, nullable), `realized_pnl` (DECIMAL 12,4, nullable)

10\. Definire relazione con Ticker

11\. Definire indici: su `ticker_id`, su `status`, su `created_at`, indice parziale su status='OPEN'

**Acceptance Criteria:**

- [ ] Tutti i campi prezzo usano DECIMAL, non FLOAT

- [ ] Enums definiti come tipi Python Enum

- [ ] Foreign key a Ticker definita correttamente

- [ ] Indici ottimizzati per query frequenti

- [ ] Campi nullable marcati esplicitamente

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.5
Area: backend
Fase: MVP
Dipendenze: TASK 2.4

## TASK 2.5: Definizione Modello SQLAlchemy - EstimateEvent (Event Sourcing)

**Descrizione:** Creare il modello per Event Sourcing delle stime.

**Microstep:**

1\. Creare file `backend/src/estimates/domain/events.py`

2\. Definire Enum `EstimateEventType`: CREATED, UPDATED, PRICE_UPDATED, TARGET_HIT, STOP_HIT, CLOSED, REOPENED

3\. Definire classe `EstimateEvent` che eredita da Base

4\. Definire colonne: `id` (UUID, PK), `estimate_id` (FK to Estimate), `event_type` (Enum), `event_data` (JSONB), `user_id` (UUID, nullable), `timestamp` (DateTime with timezone)

5\. Definire indice composto su `(estimate_id, timestamp)`

6\. Definire constraint: timestamp deve avere timezone

**Acceptance Criteria:**

- [ ] Eventi sono immutabili (no update)

- [ ] JSONB usato per flessibilità dati evento

- [ ] Indice permette query efficienti per timeline

- [ ] Ogni tipo evento documentato nel Enum

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/domain/events.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.6
Area: backend
Fase: MVP
Dipendenze: TASK 2.5

## TASK 2.6: Definizione Modello SQLAlchemy - MarketData

**Descrizione:** Creare il modello per dati storici di mercato (OHLCV).

**Microstep:**

1\. Creare file `backend/src/market_data/domain/market_data.py`

2\. Definire classe `MarketData` che eredita da Base

3\. Definire colonne: `ticker_id` (FK), `date` (Date), `open` (DECIMAL 10,4), `high` (DECIMAL 10,4), `low` (DECIMAL 10,4), `close` (DECIMAL 10,4), `volume` (BigInteger)

4\. Definire PK composta: `(ticker_id, date)`

5\. Definire colonne lineage: `data_source` (String), `ingested_at` (DateTime), `quality_score` (DECIMAL 3,2)

6\. Definire indici: su `date`, su `(ticker_id, date)` unique

**Acceptance Criteria:**

- [ ] PK composta impedisce duplicati per ticker+data

- [ ] Tutti i prezzi usano DECIMAL

- [ ] Volume usa BigInteger per supportare valori grandi

- [ ] Metadati lineage presenti per audit

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/domain/market_data.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.7
Area: backend
Fase: Fase 2
Dipendenze: TASK 2.3

## TASK 2.7: Definizione Modello SQLAlchemy - User e Role (RBAC Base)

**Descrizione:** Creare modelli per utenti e ruoli, preparando per multi-utente futuro.

**Microstep:**

1\. Creare file `backend/src/shared/domain/user.py`

2\. Definire Enum `RoleType`: ADMIN, USER, READONLY

3\. Definire classe `User`: `id` (UUID), `email` (String, unique), `hashed_password` (String, nullable), `is_active` (Boolean), `created_at`, `updated_at`

4\. Definire classe `Role`: `id` (UUID), `name` (RoleType), `description` (String)

5\. Definire tabella associativa `user_roles` per relazione many-to-many

6\. Definire relazioni bidirezionali User &lt;-&gt; Role

**Acceptance Criteria:**

- [ ] Password mai salvata in chiaro (campo per hash)

- [ ] Relazione many-to-many funzionante

- [ ] Ruoli base definiti

- [ ] Utente può avere multipli ruoli

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/user.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.8
Area: backend
Fase: Fase 2
Dipendenze: TASK 2.3

## TASK 2.8: Definizione Modello SQLAlchemy - SyncJob

**Descrizione:** Creare modello per tracciare i job di sincronizzazione con Google Drive.

**Microstep:**

1\. Creare file `backend/src/sync/domain/entities.py`

2\. Definire Enum `SyncJobType`: INITIAL_IMPORT, DAILY_HISTORY_UPDATE, ON_ESTIMATE_SAVE, MANUAL_SYNC

3\. Definire Enum `SyncJobStatus`: PENDING, RUNNING, COMPLETED, FAILED, PARTIAL

4\. Definire classe `SyncJob`: `id` (UUID), `job_type` (Enum), `status` (Enum), `started_at`, `finished_at` (nullable), `error_message` (Text, nullable), `filename` (String), `checksum_before` (String), `checksum_after` (String), `records_processed` (Integer), `records_failed` (Integer)

5\. Definire indice su `started_at` per ordinamento cronologico

**Acceptance Criteria:**

- [ ] Tutti i tipi di job rappresentati

- [ ] Stati permettono tracking completo del ciclo di vita

- [ ] Checksum permette verifica integrità

- [ ] Contatori permettono monitoraggio successo/fallimento

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.9
Area: backend
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
- Non modificare file fuori da [backend/src/analytics/domain/entities.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.10
Area: backend
Fase: MVP
Dipendenze: TASK 2.6

## TASK 2.10: Setup Alembic per Migrazioni Database

**Descrizione:** Configurare Alembic per gestione migrazioni schema database.

**Microstep:**

1\. Installare alembic come dipendenza

2\. Eseguire `alembic init backend/alembic`

3\. Configurare `alembic.ini` con path corretto

4\. Modificare `alembic/env.py` per usare async engine e importare tutti i modelli

5\. Configurare `alembic/env.py` per leggere DATABASE_URL da Settings

6\. Creare prima migrazione: `alembic revision --autogenerate -m "initial_schema"`

7\. Verificare migrazione generata

8\. Documentare comandi nel Makefile: `make migrate`, `make migrate-down`, `make migrate-new`

**Acceptance Criteria:**

- [ ] `alembic upgrade head` esegue senza errori

- [ ] `alembic downgrade -1` esegue senza errori

- [ ] Migrazione riflette tutti i modelli definiti

- [ ] Async engine configurato correttamente

---

### Istruzioni per LLM
- Non modificare file fuori da [alembic init backend/alembic, alembic.ini, alembic/env.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.11
Area: backend
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
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.12
Area: backend
Fase: MVP
Dipendenze: TASK 2.4, TASK 2.10

## TASK 2.12: Creazione Repository Estimate

**Descrizione:** Implementare repository per accesso dati Estimate.

**Microstep:**

1\. Creare file `backend/src/estimates/repositories/estimate_repository.py`

2\. Definire classe `EstimateRepository`

3\. Iniettare async session factory

4\. Implementare metodo `create(estimate: Estimate) -> Estimate`

5\. Implementare metodo `get_by_id(id: UUID) -> Optional[Estimate]`

6\. Implementare metodo `get_all(filters: EstimateFilters, pagination: Pagination) -> PaginatedResult[Estimate]`

7\. Implementare metodo `update(estimate: Estimate) -> Estimate`

8\. Implementare metodo `soft_delete(id: UUID) -> bool`

9\. Implementare metodo `get_active_by_ticker(ticker_id: UUID) -> List[Estimate]`

10\. Usare async/await per tutte le operazioni

**Acceptance Criteria:**

- [ ] Tutte le operazioni CRUD funzionano

- [ ] Paginazione cursor-based implementata

- [ ] Filtri applicati correttamente

- [ ] Soft delete imposta flag, non cancella

- [ ] Transazioni gestite correttamente

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/repositories/estimate_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.13
Area: backend
Fase: MVP
Dipendenze: TASK 2.6, TASK 2.10

## TASK 2.13: Creazione Repository MarketData

**Descrizione:** Implementare repository per accesso dati MarketData.

**Microstep:**

1\. Creare file `backend/src/market_data/repositories/market_data_repository.py`

2\. Definire classe `MarketDataRepository`

3\. Implementare metodo `upsert_daily(ticker_id: UUID, data: List[MarketDataRow])` con ON CONFLICT UPDATE

4\. Implementare metodo `get_history(ticker_id: UUID, start: date, end: date) -> List[MarketData]`

5\. Implementare metodo `get_latest_price(ticker_id: UUID) -> Optional[MarketData]`

6\. Implementare metodo `get_latest_prices_batch(ticker_ids: List[UUID]) -> Dict[UUID, MarketData]`

7\. Implementare metodo `get_aggregated(ticker_id: UUID, interval: str) -> List[AggregatedData]` per intervalli 1D/1W/1M

**Acceptance Criteria:**

- [ ] Upsert non crea duplicati

- [ ] Query batch evita N+1

- [ ] Aggregazioni calcolate lato DB

- [ ] Performance accettabile per 10 anni di dati

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/repositories/market_data_repository.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.14
Area: backend
Fase: MVP
Dipendenze: TASK 2.12

## TASK 2.14: Creazione Service EstimateService

**Descrizione:** Implementare service layer per orchestrazione business logic stime.

**Microstep:**

1\. Creare file `backend/src/estimates/services/estimate_service.py`

2\. Definire classe `EstimateService`

3\. Iniettare dipendenze: `EstimateRepository`, `MarketDataProvider`, `EventPublisher`

4\. Implementare metodo `create_estimate(command: CreateEstimateCommand) -> Estimate`:

- Validare input

- Recuperare prezzo corrente da provider

- Calcolare target_price e stop_loss da percentuali

- Creare Estimate

- Pubblicare evento ESTIMATE_CREATED

- Salvare evento in EstimateEvent

5\. Implementare metodo `update_estimate(command: UpdateEstimateCommand) -> Estimate`

6\. Implementare metodo `close_estimate(id: UUID, exit_price: Decimal, reason: str) -> Estimate`

7\. Implementare metodo `check_and_update_targets(estimate_id: UUID)` per verificare hit target/stop

**Acceptance Criteria:**

- [ ] Validazione input completa

- [ ] Eventi pubblicati per ogni operazione

- [ ] Transazione atomica (DB + evento)

- [ ] Errori business sollevano eccezioni tipizzate

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/services/estimate_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.15
Area: backend
Fase: MVP
Dipendenze: TASK 2.5, TASK 2.12

## TASK 2.15: Creazione Service EstimateHistoryService (Event Sourcing)

**Descrizione:** Implementare service per ricostruzione stato storico stime.

**Microstep:**

1\. Creare file `backend/src/estimates/services/estimate_history_service.py`

2\. Definire classe `EstimateHistoryService`

3\. Iniettare `EstimateEventRepository`

4\. Implementare metodo `get_state_at(estimate_id: UUID, at_time: datetime) -> EstimateSnapshot`:

- Recuperare tutti gli eventi fino a at_time

- Ricostruire stato applicando eventi in ordine

5\. Implementare metodo `get_audit_trail(estimate_id: UUID) -> List[AuditEntry]`:

- Restituire lista eventi con metadata human-readable

6\. Implementare metodo `get_changes_between(estimate_id: UUID, start: datetime, end: datetime) -> List[Change]`

**Acceptance Criteria:**

- [ ] Stato ricostruito correttamente per qualsiasi timestamp

- [ ] Audit trail completo e ordinato

- [ ] Performance accettabile per stime con molti eventi

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/estimates/services/estimate_history_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.16
Area: backend
Fase: MVP
Dipendenze: TASK 2.14

## TASK 2.16: Creazione API Router Estimates

**Descrizione:** Implementare endpoint REST per gestione stime.

**Microstep:**

1\. Creare file `backend/src/estimates/api/routes.py`

2\. Creare router FastAPI con prefix `/api/estimates`

3\. Implementare endpoint `POST /` per creazione stima

4\. Implementare endpoint `GET /` per lista stime con filtri (status, ticker, date_range, ai_model)

5\. Implementare endpoint `GET /{id}` per dettaglio singola stima

6\. Implementare endpoint `PATCH /{id}` per aggiornamento parziale

7\. Implementare endpoint `DELETE /{id}` per chiusura/cancellazione

8\. Implementare endpoint `GET /{id}/history` per audit trail

9\. Tutti gli endpoint restituiscono `ApiResponse` standard

10\. Aggiungere dependency injection per services

**Acceptance Criteria:**

- [ ] Tutti gli endpoint documentati con OpenAPI

- [ ] Request validation con Pydantic

- [ ] Response conforme a schema ApiResponse

- [ ] Errori restituiti con codici appropriati (400, 404, 500)

- [ ] Filtri funzionanti e combinabili

---

### Istruzioni per LLM
- Non modificare file fuori da [/api/estimates, DELETE /{id}, GET /, GET /{id}, GET /{id}/history, PATCH /{id}, POST /, backend/src/estimates/api/routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.17
Area: backend
Fase: MVP
Dipendenze: -

## TASK 2.17: Creazione API Router Market Data

**Descrizione:** Implementare endpoint REST per dati di mercato.

**Microstep:**

1\. Creare file `backend/src/market_data/api/routes.py`

2\. Creare router FastAPI con prefix `/api/market`

3\. Implementare endpoint `GET /price/{ticker}` per prezzo corrente

4\. Implementare endpoint `GET /history/{ticker}` con query params: start_date, end_date, interval

5\. Implementare endpoint `GET /fundamentals/{ticker}` per dati fondamentali

6\. Implementare endpoint `GET /search` con query param `q` per autocomplete ticker

7\. Aggiungere caching headers appropriati (Cache-Control)

**Acceptance Criteria:**

- [ ] Prezzi restituiti con metadata (source, timestamp, stale flag)

- [ ] History supporta aggregazione 1D/1W/1M

- [ ] Search restituisce max 10 risultati ordinati per rilevanza

- [ ] Cache headers impostati correttamente

Nota: tutti gli endpoint leggono i dati tramite MarketDataProvider (TASK 2.18-2.19), senza dipendere direttamente da yfinance.

---

### Istruzioni per LLM
- Non modificare file fuori da [/api/market, GET /fundamentals/{ticker}, GET /history/{ticker}, GET /price/{ticker}, GET /search, backend/src/market_data/api/routes.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.18
Area: backend
Fase: MVP
Dipendenze: TASK 2.17

**TASK 2.18: Definizione MarketDataProvider Astratto**

**Descrizione:**  
Definire un'interfaccia MarketDataProvider per disaccoppiare la logica di business dalla specifica sorgente dati (Yahoo oggi, altri provider domani).

**Microstep:**

- Creare file backend/src/market_data/domain/providers.py.
- Definire Protocol/classe astratta MarketDataProvider con metodi:
  - get_current_price(ticker: str) -> PriceData
  - get_historical_prices(ticker: str, start: date, end: date, interval: str) -> list[PriceData]
  - get_fundamentals(ticker: str) -> FundamentalsData.
- Definire dataclass Pydantic/Domain PriceData e FundamentalsData da usare come contratti interni.
- Aggiornare i servizi esistenti in backend/src/market_data/services/ (es. MarketDataService) per dipendere da MarketDataProvider invece che chiamare direttamente yfinance.
- Preparare stub/placeholder per futuri provider (es. FinnhubMarketDataProvider) con NotImplementedError.

**Acceptance Criteria:**

- Tutta la logica di mercato usa MarketDataProvider e non dipende da yfinance direttamente.
- MarketDataService riceve il provider via dependency injection FastAPI.
- I test possono usare un FakeMarketDataProvider per simulare dati senza chiamate esterne.

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.19
Area: backend
Fase: MVP
Dipendenze: TASK 2.18

**TASK 2.19: Caching & Backoff per MarketDataProvider**

**Descrizione:**  
Ridurre chiamate a Yahoo/Finnhub e gestire in modo resiliente timeouts e rate‑limit, usando cache in memoria e backoff.

**Microstep:**

- Creare file backend/src/infra/cache/memory_cache.py con una semplice cache LRU/TTL (es. cachetools.TTLCache).
- Creare classe CachedMarketDataProvider in backend/src/market_data/infrastructure/cached_provider.py che implementa MarketDataProvider e wrappa un provider sottostante (YahooMarketDataProvider).
- Implementare TTL differenziato:
  - Prezzi correnti: TTL 60s.
  - Storico: TTL 1h.
  - Fundamentals: TTL 24h.
- Aggiungere logica di backoff:
  - Su TimeoutError o HTTP 429/5xx, ritentare fino a N volte (es. 3) con ritardo esponenziale (es. 0.5s, 1s, 2s).
  - In caso di fallimento definitivo, se presente un valore in cache "stale", restituirlo con flag stale=True nel PriceData/FundamentalsData.
- Configurare via Settings i TTL e il numero massimo di retry.
- Aggiornare la dependency injection in FastAPI per usare CachedMarketDataProvider come implementazione di default.

**Acceptance Criteria:**

- Le chiamate ripetute allo stesso endpoint/ticker entro il TTL non generano chiamate esterne aggiuntive.
- In caso di timeout/rate‑limit, il sistema usa il dato in cache se disponibile e non va in errore 500 immediato.
- I test coprono: cache hit, cache miss, fallback a dati stale, backoff su errori.

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.20
Area: drive
Fase: MVP
Dipendenze: -

## TASK 2.20: Implementazione Google Drive Client

**Descrizione:** Creare client per interazione con Google Drive API.

**Microstep:**

1\. Creare file `backend/src/infra/drive/client.py`

2\. Definire classe `GoogleDriveClient`

3\. Implementare autenticazione con Service Account usando credenziali da Settings

4\. Implementare metodo `list_files(folder_id: str) -> List[DriveFile]`

5\. Implementare metodo `download_file(file_id: str) -> bytes`

6\. Implementare metodo `upload_file(folder_id: str, filename: str, content: bytes, mime_type: str) -> DriveFile`

7\. Implementare metodo `update_file(file_id: str, content: bytes) -> DriveFile`

8\. Implementare metodo `create_temp_file(folder_id: str, filename: str) -> DriveFile` per pattern file temporaneo

9\. Implementare metodo `delete_file(file_id: str) -> bool`

10\. Aggiungere logging e metriche per ogni operazione

**Acceptance Criteria:**

- [ ] Autenticazione funziona con Service Account

- [ ] Tutte le operazioni CRUD funzionano

- [ ] Errori API gestiti con eccezioni tipizzate

- [ ] Timeout configurabile

### Sync Engine & retro‑compatibilità (TASK 2.20-2.23)

Questi task coprono il nuovo Sync Engine con Google Drive e garantiscono la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) tramite test E2E dedicati.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/drive/client.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.21
Area: drive
Fase: MVP
Dipendenze: TASK 2.20

## TASK 2.21: Implementazione CSV Parser Legacy

**Descrizione:** Creare parser bidirezionale per formato CSV legacy TickerTracker.

**Microstep:**

1\. Creare file `backend/src/sync/infra/csv_parser.py`

2\. Definire classe `LegacyCsvParser`

3\. Implementare metodo `parse_estimates_csv(content: bytes) -> List[LegacyEstimateRow]`:

- Gestire encoding UTF-8 con BOM

- Mappare le 120+ colonne del formato legacy

- Gestire colonne vuote o mancanti senza crash

- Restituire lista di dataclass con dati parsed

4\. Implementare metodo `export_estimate_to_csv_row(estimate: Estimate, fundamentals: dict) -> str`:

- Mappare dati puliti nel formato "piatto" legacy

- Gestire valori None

5\. Implementare metodo `parse_history_csv(content: bytes) -> List[LegacyHistoryRow]`

6\. Implementare metodo `export_history_to_csv(data: List[MarketData]) -> bytes`

7\. Creare file di mapping colonne per documentazione

**Acceptance Criteria:**

- [ ] Parse gestisce file reali legacy senza errori

- [ ] Round-trip parse -> export -> parse produce stessi dati

- [ ] Colonne mancanti hanno default sensati

- [ ] Encoding gestito correttamente

Nota: la retro‑compatibilità del formato legacy è validata dai test E2E del TASK 2.23.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/infra/csv_parser.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.22
Area: drive
Fase: MVP
Dipendenze: TASK 2.21

## TASK 2.22: Implementazione Sync Service

**Descrizione:** Implementare service per sincronizzazione bidirezionale con Drive.

**Microstep:**

1\. Creare file `backend/src/sync/services/sync_service.py`

2\. Definire classe `SyncService`

3\. Iniettare: `GoogleDriveClient`, `LegacyCsvParser`, `EstimateRepository`, `MarketDataRepository`, `SyncJobRepository`

4\. Implementare metodo `run_initial_import()`:

- Scaricare file JSON backup e CSV history da Drive

- Parsare e importare stime nel DB

- Creare SyncJob con risultato

5\. Implementare metodo `sync_estimate_to_drive(estimate_id: UUID)`:

- Recuperare stima e fundamentals

- Esportare in formato CSV

- Aggiornare file Drive con pattern file temporaneo

- Calcolare e salvare checksum

6\. Implementare metodo `run_daily_history_sync()`:

- Per ogni ticker attivo, aggiornare file History_*.csv su Drive

7\. Implementare logica di conflict resolution: last-writer-wins con logging conflitti

**Acceptance Criteria:**

- [ ] Import non crea duplicati (idempotente)

- [ ] Export usa file temporaneo per atomicità

- [ ] Checksum verificato dopo ogni operazione

- [ ] Conflitti loggati per review manuale

Nota: la retro‑compatibilità del formato legacy è validata dai test E2E del TASK 2.23.

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/sync/services/sync_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.23
Area: drive
Fase: MVP
Dipendenze: TASK 2.22

## TASK 2.23: **Test Retro‑compatibilità Backup & History Legacy (Sync Engine)**

**Descrizione:**  
Validare che il nuovo backend mantenga la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) prodotti dalla versione HTML+GAS.

**Microstep:**

- Creare file backend/tests/e2e/test_legacy_compatibility.py.
- Aggiungere fixture che carica 1-2 file JSON di backup reali e 1-2 file History_*.csv reali da una cartella tests/fixtures/legacy/.
- Scrivere test test_import_backup_json_roundtrip:
  - Importare il backup JSON con gli stessi path usati da SyncService.run_initial_import().
  - Esportare lo stato corrente del DB in un nuovo JSON "simulato".
  - Verificare che numero di stime, ticker e campi chiave (ticker, data apertura, target %, stop %, status) coincidano.
- Scrivere test test_import_history_csv_roundtrip:
  - Parsare un CSV legacy con LegacyCsvParser.parse_history_csv.
  - Importare i dati in MarketDataRepository.
  - Esportare nuovamente con LegacyCsvParser.export_history_to_csv.
  - Verificare che dati OHLC e date siano identici (a parte eventuali colonne vuote aggiuntive).
- Aggiungere un test test_sync_estimate_to_drive_does_not_break_legacy_file_format:
  - Usare sync_estimate_to_drive(estimate_id) con un estimate di test.
  - Scaricare il file aggiornato da un Drive finto (o mockato) e verificare che le colonne obbligatorie del formato legacy siano tutte presenti e nell'ordine previsto.

**Acceptance Criteria:**

- Import + export di backup JSON non perde nessuna stima né cambia i valori chiave.
- Import + export di CSV storico produce gli stessi valori OHLC e date.
- I file generati dal nuovo SyncService sono ancora leggibili dallo script HTML+GAS originale.
- I test e2e possono essere eseguiti localmente con pytest senza dipendenze da Drive reale (mocks/fixtures).

Questi task coprono il nuovo Sync Engine con Google Drive e garantiscono la piena retro‑compatibilità con i file legacy (backup JSON e History_*.csv) tramite test E2E dedicati.

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.24
Area: backend
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
- Non modificare file fuori da [backend/src/infra/scheduler/scheduler.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.25
Area: backend
Fase: MVP
Dipendenze: TASK 2.24

## TASK 2.25: Implementazione Pattern Outbox per Eventi

**Descrizione:** Creare pattern outbox per pubblicazione affidabile eventi verso Drive.

**Microstep:**

1\. Creare modello SQLAlchemy `OutboxEvent`: `id`, `event_type`, `payload` (JSONB), `created_at`, `processed_at` (nullable), `error` (nullable), `retry_count`

2\. Creare migrazione Alembic

3\. Modificare `EstimateService` per salvare eventi in outbox nella stessa transazione del DB

4\. Creare `OutboxProcessor` che:

- Legge eventi non processati

- Esegue azione (es. sync verso Drive)

- Marca come processato o incrementa retry_count

5\. Schedulare `OutboxProcessor` ogni 30 secondi

6\. Implementare dead letter: dopo N retry, marca come failed e alerta

**Acceptance Criteria:**

- [ ] Eventi salvati atomicamente con dati business

- [ ] Processor riprova eventi falliti

- [ ] Dead letter per eventi irrecuperabili

- [ ] Nessuna perdita di eventi

---

# SEZIONE 3: SICUREZZA, OSSERVABILITÀ, GOVERNANCE

---

### Istruzioni per LLM
- Non modificare file fuori da [repo root] se non strettamente necessario.
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

- [ ] Headers presenti in tutte le response

- [ ] API key validata se configurata

- [ ] Logging strutturato per ogni request

- [ ] Middleware non rallenta significativamente (<1ms overhead)

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/infra/security/middleware.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.2
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.2: Implementazione Rate Limiting

Priorità: Fase 2 (necessario solo in scenari multi‑utente / produzione, NON blocca l'ambiente locale single‑user).

**Descrizione:** Aggiungere rate limiting per protezione API.

**Microstep:**

1\. Installare dipendenza `slowapi`

2\. Creare file `backend/src/infra/security/rate_limit.py`

3\. Configurare `Limiter` con storage Redis

4\. Definire limiti di default: 100 req/minuto per IP

5\. Definire limiti specifici per endpoint sensibili:

- `/api/chat`: 10 req/minuto

- `/api/estimates` POST: 30 req/minuto

- `/api/market/price`: 60 req/minuto

6\. Implementare response 429 con header `Retry-After`

7\. Aggiungere whitelist per IP interni/admin

**Acceptance Criteria:**

- [ ] Rate limit applicato correttamente

- [ ] Storage Redis per condivisione tra istanze

- [ ] Response 429 include Retry-After

- [ ] Whitelist funzionante

---

### Istruzioni per LLM
- Non modificare file fuori da [/api/chat, /api/estimates, /api/market/price, backend/src/infra/security/rate_limit.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.3
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.3: Implementazione Input Validation Avanzata

**Descrizione:** Creare validatori Pydantic riutilizzabili per input sicuro.

**Microstep:**

1\. Creare file `backend/src/shared/schemas/validators.py`

2\. Implementare validatore `sanitize_ticker`: solo A-Z, 0-9, ., -, max 10 caratteri

3\. Implementare validatore `sanitize_text`: rimuove tag HTML, limita lunghezza

4\. Implementare validatore `validate_price`: positivo, max 6 decimali, range ragionevole

5\. Implementare validatore `validate_percentage`: range -100% a +1000%

6\. Implementare validatore `validate_date_range`: start <= end, max 10 anni span

7\. Applicare validatori agli schema Pydantic esistenti

**Acceptance Criteria:**

- [ ] Input malformati sollevano ValidationError

- [ ] Messaggi errore user-friendly

- [ ] Nessun input può causare injection SQL/XSS

- [ ] Test per ogni validatore

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/schemas/validators.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
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
- Non modificare file fuori da [backend/src/infra/security/encryption.py] se non strettamente necessario.
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
- Non modificare file fuori da [backend/src/infra/logging/config.py] se non strettamente necessario.
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
- Non modificare file fuori da [GET /metrics, backend/src/infra/metrics/metrics.py] se non strettamente necessario.
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
- Non modificare file fuori da [GET /health, GET /health/live, GET /health/ready, backend/src/infra/health/health_service.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.8
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.8: Implementazione Data Quality Monitor

Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).

**Descrizione:** Creare sistema di monitoraggio qualità dati di mercato.

**Microstep:**

1\. Creare file `backend/src/market_data/services/quality_monitor.py`

2\. Definire dataclass `QualityRule`: name, description, check_fn, severity

3\. Definire dataclass `QualityIssue`: ticker, rule_name, severity, message, detected_at

4\. Implementare regole di default:

- Prezzi positivi

- No gap > 5 giorni lavorativi

- Variazione giornaliera < 50%

- Volume > 0

5\. Implementare metodo `run_checks(ticker: str) -> List[QualityIssue]`

6\. Implementare metodo `run_all_checks() -> Dict[str, List[QualityIssue]]`

7\. Schedulare check giornaliero

8\. Loggare/alertare su issue critici

**Acceptance Criteria:**

- [ ] Regole coprono scenari comuni di data corruption

- [ ] Issue loggati con dettagli sufficienti per debug

- [ ] Alert per issue severity=critical

- [ ] Report giornaliero generato

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/market_data/services/quality_monitor.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.9
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.9: Implementazione Data Lineage Tracking

Priorità: Fase 2 (opzionale per ambiente locale single‑user; implementare solo se servono metriche/monitoring avanzati).

**Descrizione:** Aggiungere metadati di provenienza a tutti i dati di mercato.

**Microstep:**

1\. Creare file `backend/src/shared/domain/lineage.py`

2\. Definire Enum `DataSource`: YAHOO_FINANCE, FINNHUB, MANUAL_ENTRY, DRIVE_SYNC, CALCULATED

3\. Definire mixin `LineageTracked` con campi: data_source, source_timestamp, ingestion_timestamp, quality_score

4\. Applicare mixin a modello MarketData

5\. Creare migrazione Alembic per nuove colonne

6\. Modificare provider e import per popolare campi lineage

7\. Esporre lineage negli endpoint API (campo opzionale includable)

**Acceptance Criteria:**

- [ ] Ogni record MarketData ha lineage completo

- [ ] Source timestamp riflette quando il dato è stato generato alla fonte

- [ ] Quality score calcolato (freshness + completeness)

- [ ] API permette di filtrare/ordinare per lineage

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/domain/lineage.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.10
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.10: Configurazione Connection Pooling Ottimizzato

Priorità: Media (consigliato dopo l'MVP per migliorare performance e stabilità, ma non blocca l'uso locale base).

**Descrizione:** Ottimizzare pool connessioni database per performance e resilienza.

**Microstep:**

1\. Modificare file `backend/src/shared/infra/database.py`

2\. Configurare QueuePool con parametri:

- pool_size: 5 (dev) / 10 (prod)

- max_overflow: 10 (dev) / 20 (prod)

- pool_timeout: 30 secondi

- pool_recycle: 1800 secondi (30 min)

- pool_pre_ping: True

3\. Leggere configurazione da Settings

4\. Aggiungere metriche pool: connections_in_use, connections_available

5\. Documentare tuning per diversi carichi

**Acceptance Criteria:**

- [ ] Pool configurato correttamente per ambiente

- [ ] pre_ping evita connessioni stale

- [ ] Metriche pool esposte

- [ ] Nessun connection leak sotto carico

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/infra/database.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.11
Area: infra
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.11: Implementazione Query Pagination Cursor-Based

Priorità: Fase 2 (necessario solo con dataset molto grandi; non blocca l'MVP locale).**Descrizione:** Implementare paginazione efficiente basata su cursore per grandi dataset.

**Microstep:**

1\. Creare file `backend/src/shared/repositories/pagination.py`

2\. Definire dataclass `CursorPagination`: cursor (optional), limit, direction (NEXT/PREV)

3\. Definire dataclass `PaginatedResult[T]`: items, next_cursor, prev_cursor, has_more

4\. Implementare funzione `encode_cursor(values: dict) -> str` (base64 encode)

5\. Implementare funzione `decode_cursor(cursor: str) -> dict`

6\. Implementare helper `apply_cursor_pagination(query, cursor, sort_columns)` per SQLAlchemy

7\. Modificare repository MarketData per usare cursor pagination

8\. Documentare formato cursore e limitazioni

**Acceptance Criteria:**

- [ ] Cursore opaco (non manipolabile dall'utente)

- [ ] Performance O(1) indipendente dalla pagina

- [ ] Navigazione avanti e indietro funzionante

- [ ] Gestione edge case: prima pagina, ultima pagina, dataset vuoto

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/repositories/pagination.py] se non strettamente necessario.
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
- Non modificare file fuori da [POST /api/admin/feature-flags, backend/src/infra/feature_flags/service.py] se non strettamente necessario.
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
- Non modificare file fuori da [backend/scripts/backup.py] se non strettamente necessario.
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
- Non modificare file fuori da [Sezione 1 (Setup base):

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