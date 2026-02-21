# AGENTS — shared

ID: TASK 1.1
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, README.md, __init__.py, analytics/, api/, backend/src/, backend/src/infra/, cache/, domain/, drive/, ...] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.2
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/schemas/api_response.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.3
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/domain/value_objects/money.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.4
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/domain/value_objects/percentage.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.5
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/domain/value_objects/price_target.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.6
Area: shared
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

11\. Creare/aggiornare `backend/.gitignore` per escludere `.env`, `__pycache__/`, `.venv/`, `.pytest_cache/`, `.coverage`, `.mypy_cache/`**

12\. Creare test in `tests/unit/shared/test_config.py` per verificare caricamento, singleton, e protezione SecretStr


**Acceptance Criteria:**

- [ ] Settings carica variabili da file .env

- [ ] Tutti i secret usano tipo SecretStr

- [ ] Valori di default sensati per development

- [ ] `.env.example` documenta tutte le variabili richieste

- [ ] `get_settings()` restituisce sempre la stessa istanza (cached)

- [ ] `.env` è in `.gitignore` e NON può essere committato

- [ ] Test unitari passano e coprono casi principali

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/infra/config.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 1.7
Area: shared
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
- Non modificare file fuori da [backend/src/shared/] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.1
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, backend/.python-version, backend/Makefile, backend/pyproject.toml] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.7
Area: shared
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

- [x] Password mai salvata in chiaro (campo per hash)

- [x] Relazione many-to-many funzionante

- [x] Ruoli base definiti

- [x] Utente può avere multipli ruoli

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/domain/user.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 2.10
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, alembic init backend/alembic, alembic.ini, alembic/env.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.3
Area: shared
Fase: Fase 2
Dipendenze: TASK 3.1, TASK 3.2
**Status: ✅ COMPLETED**

## TASK 3.3: Implementazione Input Validation Avanzata

**Descrizione:** Creare validatori Pydantic riutilizzabili per input sicuro.

**Microstep:**

1\. ✅ Creare file `src/shared/schemas/validators.py`

2\. ✅ Implementare `sanitize_ticker`: strip + uppercase + regex `^[A-Z0-9.\-]{1,10}$`

3\. ✅ Implementare `sanitize_text`: rimuove tag HTML (`<[^>]+>`), strip whitespace, tronca a `max_len` (default 500)

4\. ✅ Implementare `validate_price`: `> 0` e `≤ 999999.999999`, normalizza a 6 dp (ROUND_HALF_UP)

5\. ✅ Implementare `validate_percentage`: range `[-100, +1000]`, normalizza a 4 dp

6\. ✅ Implementare `validate_date_range`: `start ≤ end`, span ≤ 3650 giorni

7\. ✅ Applicare ai Pydantic schema: `@field_validator("exit_price")` in `CloseEstimateCommand`; `@field_validator("ai_reasoning")` in `Create/UpdateEstimateCommand`; `@model_validator(mode="after")` in `EstimateFilters`

8\. ✅ Aggiornare `src/shared/schemas/__init__.py` per esportare tutti e 5 i validatori

**Acceptance Criteria:**

- [x] Input malformati sollevano ValidationError

- [x] Messaggi errore user-friendly (in inglese)

- [x] Nessun input può causare injection SQL/XSS (verificato da test dedicati)

- [x] Test per ogni validatore

**Implementazione Completata (Task 3.3):**

File creati/modificati:
- `src/shared/schemas/validators.py` – 5 validatori standalone: `sanitize_ticker`, `sanitize_text`, `validate_price`, `validate_percentage`, `validate_date_range`
- `src/shared/schemas/__init__.py` – 5 nuove esportazioni
- `src/estimates/schemas/commands.py` – `@field_validator("exit_price")` in `CloseEstimateCommand`; `@field_validator("ai_reasoning")` in `CreateEstimateCommand` e `UpdateEstimateCommand`; import di `validate_price`, `sanitize_text`
- `src/estimates/schemas/filters.py` – `@model_validator(mode="after")` `validate_date_ranges` in `EstimateFilters`; import di `model_validator`, `validate_date_range`
- `tests/unit/shared/test_validators.py` – 63 test (6 classi: Ticker, Text, Price, Percentage, DateRange, SchemaIntegration)

Note tecniche:
- `from __future__ import annotations` NON usato nei test (causa string annotations incompatibili con slowapi wrapper)
- Vincoli di dominio `Field(gt=0, le=100)` su `stop_loss_percent` lasciati invariati
- `sanitize_text` rimuove solo tag HTML (non il contenuto interno ai tag) — comportamento conforme a `re.sub(r"<[^>]+>", "", v)`

Test risultati: 378/378 passed (63 nuovi + 315 precedenti)

---

### Istruzioni per LLM
- Non modificare file fuori da [`src/shared/schemas/validators.py`, `src/estimates/schemas/`] se non strettamente necessario.
- Endpoint decorati richiedono `from __future__ import annotations` rimosso dai file test.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.9
Area: shared
Fase: Fase 2
Dipendenze: TASK 2.20

## TASK 3.9: Implementazione Data Lineage Tracking ✅ COMPLETATO

**Status**: ✅ COMPLETATO — 515/515 test PASSED (20 nuovi test, zero regressioni)

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

- [x] Ogni record MarketData ha lineage completo (data_source, source_timestamp, ingestion_timestamp, quality_score)

- [x] Source timestamp riflette quando il dato è stato generato alla fonte (Yahoo: usa request timestamp come proxy)

- [x] Quality score calcolato (freshness 0.6 + completeness 0.4, clamped 0–1)

- [x] API espone lineage opzionale via `?include_lineage=true` su `GET /api/market/history/{ticker}`

**Implementazione (file creati/modificati):**

- `src/shared/domain/lineage.py` — **CREATO**: `DataSource` enum + `from_legacy()`, `LineageTracked` mixin con `compute_quality_score()`
- `src/shared/domain/__init__.py` — MODIFICATO: export `DataSource`, `LineageTracked`
- `src/market_data/domain/market_data.py` — MODIFICATO: `class MarketData(LineageTracked, Base)`, rimossi 3 campi inline
- `src/market_data/repositories/market_data_repository.py` — MODIFICATO: `MarketDataRow` + `source_timestamp`; `ingested_at` → `ingestion_timestamp`
- `src/market_data/services/market_data_service.py` — MODIFICATO: `DataSource.YAHOO_FINANCE.value` + `source_timestamp`
- `src/market_data/services/quality_monitor.py` — MODIFICATO: import `DataSource`
- `src/market_data/schemas/lineage.py` — **CREATO**: `MarketDataLineageSchema` Pydantic
- `src/market_data/api/routes.py` — MODIFICATO: `include_lineage` param, `HistoricalPricePoint.lineage`
- `alembic/versions/a3b5c7d9e1f0_add_lineage_source_timestamp.py` — **CREATO**: offline-only migration
- `tests/unit/shared/test_lineage.py` — **CREATO**: 20 unit test

---

### Istruzioni per LLM
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/domain/lineage.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.10
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/infra/database.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.

ID: TASK 3.11
Area: shared
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
- Non modificare file fuori da [backend/src/shared/, backend/src/shared/repositories/pagination.py] se non strettamente necessario.
- Segui i microstep in ordine e non introdurre pattern/tecnologie non menzionati.
- Se trovi codice esistente che confligge con queste istruzioni, fermati e proponi una breve nota invece di riscrivere tutto.
- Alla fine, produci un elenco puntato con file modificati e test eseguiti.